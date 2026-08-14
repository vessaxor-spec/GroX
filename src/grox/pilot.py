from __future__ import annotations
from pathlib import Path
from typing import Any
import uuid
from .contracts import MissionOrder, MissionMode, RiskClass, Evidence
from .state import StateStore
from .crew.roster import CrewRoster
from .tools.gateway import ToolGateway
from .runtime.executor import CrewExecutor
from .mission_control.core import MissionControl
from .verification.core import IndependentVerifier
from .reasoning import ReasoningError, build_reasoner_from_env

_AUTO = object()
_RISK_RANK = {RiskClass.low:0, RiskClass.medium:1, RiskClass.high:2, RiskClass.critical:3}

class PilotGorXu:
    """GroX's sole operational orchestrator."""
    def __init__(self, vessel_root:Path, *, reasoner:Any=_AUTO):
        self.root=vessel_root.resolve()
        self.store=StateStore(self.root/'configs/state/grox.sqlite3')
        self.roster=CrewRoster(self.root/'configs/crew/dossiers',self.store)
        self.mission_control=MissionControl()
        self.gateway=ToolGateway(self.root)
        self.executor=CrewExecutor(self.gateway)
        self.verifier=IndependentVerifier()
        self.reasoner=build_reasoner_from_env() if reasoner is _AUTO else reasoner

    @property
    def cognitive_status(self)->str:
        return getattr(self.reasoner,'name','deterministic-only') if self.reasoner else 'deterministic-only'

    def _required_caps(self, mode:MissionMode)->list[str]:
        return {'inspect':['repo_read'],'repair':['repo_read','repo_write'],'verify':['repo_read','verify'],'execute':['repo_read']}[mode.value]

    def _roster_summary(self)->list[dict[str,Any]]:
        return [
            {'crew_id':d.crew_id,'division':d.division,'title':d.title,'capabilities':sorted(d.capabilities),'tags':sorted(d.tags),'verification':d.verification}
            for d in self.roster.all()
        ]

    def _interpret(self,directive:str):
        if not self.reasoner: return None,None
        try:
            return self.reasoner.interpret(directive,roster=self._roster_summary()),None
        except (ReasoningError,ValueError,TypeError) as e:
            return None,str(e)

    def _reconcile_mode(self,directive:str,explicit:MissionMode|None,brief)->MissionMode:
        policy=self.mission_control.infer_mode(directive,explicit)
        if explicit or not brief: return policy
        # The reasoning model may narrow/clarify non-mutating work, never grant mutation authority.
        if policy is MissionMode.execute and brief.proposed_mode=='inspect':
            return MissionMode.inspect
        return policy

    def _reconcile_risk(self,directive:str,explicit:RiskClass|None,brief)->RiskClass:
        policy=self.mission_control.assess_risk(directive,explicit)
        if not brief or not brief.proposed_risk: return policy
        proposed=RiskClass(brief.proposed_risk)
        return proposed if _RISK_RANK[proposed] > _RISK_RANK[policy] else policy

    def _select_crew(self,directive:str,required:list[str],crew_id:str|None,brief):
        if crew_id: return self.roster.get(crew_id)
        if brief:
            for cid in brief.candidate_crew_ids:
                try: candidate=self.roster.get(cid)
                except KeyError: continue
                if set(required).issubset(candidate.capabilities): return candidate
        return self.roster.select(directive,required)

    def command(self, directive:str, *, mode:MissionMode|None=None, risk:RiskClass|None=None, crew_id:str|None=None, scope:str='.', parameters:dict|None=None)->dict:
        brief,cognition_error=self._interpret(directive)
        mode=self._reconcile_mode(directive,mode,brief)
        risk=self._reconcile_risk(directive,risk,brief)
        mission_id=f"MSN-{uuid.uuid4().hex[:12]}"; self.store.create_mission(mission_id,directive,mode.value,risk.value)
        req=self._required_caps(mode)
        try:
            crew=self._select_crew(directive,req,crew_id,brief)
            if not set(req).issubset(crew.capabilities): raise LookupError(f"Crew {crew.crew_id} lacks required capabilities {req}")
            actions=self.mission_control.default_actions(mode)
            objective=brief.objective if brief else directive
            order=MissionOrder.new(mission_id,directive,objective,mode,crew.crew_id,required_capabilities=req,allowed_actions=actions,
                forbidden_actions=[] if mode is MissionMode.repair else ['fs_write'],scope=[scope],risk_class=risk,
                verification_requirements=['independent'] if self.mission_control.verification_required(mode,risk) else [],
                stop_conditions=['blocker','better_or_safer_path','missing_capability','elevated_risk','scope_change','irreversible_consequence'],parameters=parameters or {})
            self.store.save_order(order)
            if brief:
                self.store.add_evidence(mission_id,order.order_id,Evidence('cognitive_plan',{'provider':self.cognitive_status,**brief.to_dict()}))
            if cognition_error:
                self.store.add_evidence(mission_id,order.order_id,Evidence('cognition_degraded',{'provider':self.cognitive_status,'error':cognition_error,'fallback':'deterministic control plane'}))
            self.store.crew_on_duty(crew.crew_id,mission_id); self.store.update_order(order.order_id,'running')
            result=self.executor.execute(order)
            for ev in result.evidence: self.store.add_evidence(mission_id,order.order_id,ev)
            self.store.update_order(order.order_id,result.status); self.store.crew_sleep(crew.crew_id,mission_id,result.summary)

            verification=None
            if result.status=='completed' and self.mission_control.verification_required(mode,risk):
                vcrew=self.roster.select(f"verify {directive}",['repo_read','verify'],exclude=[crew.crew_id],verifier=True)
                vorder=MissionOrder.new(mission_id,directive,f"Independently verify order {order.order_id}",MissionMode.verify,vcrew.crew_id,
                    required_capabilities=['repo_read','verify'],allowed_actions=['fs_list','fs_read','test_run'],forbidden_actions=['fs_write'],scope=[scope],risk_class=risk,parent_order_id=order.order_id)
                self.store.save_order(vorder); self.store.crew_on_duty(vcrew.crew_id,mission_id); self.store.update_order(vorder.order_id,'running')
                ok,msg=self.verifier.verify(crew.crew_id,vcrew.crew_id,result)
                vev=Evidence('independent_verification',{'ok':ok,'message':msg,'executor':crew.crew_id,'verifier':vcrew.crew_id})
                self.store.add_evidence(mission_id,vorder.order_id,vev); self.store.update_order(vorder.order_id,'completed' if ok else 'exception'); self.store.crew_sleep(vcrew.crew_id,mission_id,msg)
                verification={'ok':ok,'message':msg,'verifier':vcrew.crew_id,'order_id':vorder.order_id}
                if not ok: result.status='exception'

            summary=f"GorXu: {result.summary}"
            if brief: summary += f" | Cognitive strategy: {brief.recommended_option or 'structured interpretation'} ({brief.confidence:.2f})"
            if cognition_error: summary += " | Cognitive provider degraded; deterministic fallback used"
            if result.exception: summary += f" | Exception returned to Pilot: {result.exception['type']}"
            if verification: summary += f" | Verification: {'PASS' if verification['ok'] else 'FAIL'} by {verification['verifier']}"
            self.store.update_mission(mission_id,'completed' if result.status=='completed' else 'needs_pilot_decision',summary)
            return {'mission_id':mission_id,'mode':mode.value,'risk':risk.value,'crew':crew.crew_id,'status':result.status,'summary':summary,'verification':verification,'exception':result.exception,'cognition':brief.to_dict() if brief else None,'cognition_error':cognition_error}
        except Exception as e:
            self.store.update_mission(mission_id,'needs_pilot_decision',f"GorXu exception: {e}")
            return {'mission_id':mission_id,'mode':mode.value,'risk':risk.value,'status':'needs_pilot_decision','summary':f"GorXu exception: {e}",'exception':{'type':type(e).__name__,'message':str(e)},'cognition':brief.to_dict() if brief else None,'cognition_error':cognition_error}

    def repair_write(self,path:str,content:str,*,risk:RiskClass|None=None,crew_id:str|None=None)->dict:
        return self.command(f"Repair {path} by writing Commander-approved content",mode=MissionMode.repair,risk=risk,crew_id=crew_id,scope=path,parameters={'operation':'write_text','path':path,'content':content})
