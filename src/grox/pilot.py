from __future__ import annotations
from pathlib import Path
from typing import Any
from time import perf_counter
import os
import traceback
import uuid
from .contracts import MissionOrder, MissionMode, RiskClass, Evidence, TourResult
from .state import StateStore
from .durable_state import DurableState
from .crew.roster import CrewRoster
from .runtime_layout import VesselLayout
from .tools.layout_gateway import LayoutToolGateway
from .runtime.executor import CrewExecutor
from .mission_control.core import MissionControl
from .verification.core import IndependentVerifier
from .reasoning import AssistantResponse, ReasoningError, build_reasoner_from_env
from .live_environment import (
    LiveEnvironmentAwareness, LiveResourceSnapshot, ResourcePolicy, ResourceSelectionError,
)
from .native_model_runtime import LocalModelRuntime
from .tool_awareness import ToolCapabilityAwareness
from .cognition_awareness import CognitionProviderAwareness, CognitionProviderPolicy
from .cognition_discovery import ConfiguredCognitionDiscovery, nonsecret_reasoner_config_from_env
from .configured_connection_awareness import ConfiguredConnectionPolicyAwareness
from .configured_local_readiness import ConfiguredLocalCognitionReadiness
from .graph import MissionGraphPlan
from .graph.runtime import GraphExecutionError, MissionGraphRunner
from .intelligence import LivingCompanyIntelligence
from .operations import ExecutiveExceptionLoop
from .evaluation import OrchestrationEvaluator

_AUTO = object()
_RISK_RANK = {RiskClass.low:0, RiskClass.medium:1, RiskClass.high:2, RiskClass.critical:3}

class PilotGorXu:
    """GroX's sole operational orchestrator."""
    def __init__(
        self, vessel_root:Path|VesselLayout, *, reasoner:Any=_AUTO, gateway_policy=None,
        extra_allowed_origins=(), secret_broker=None, mcp_registry=None,
    ):
        layout=vessel_root if isinstance(vessel_root,VesselLayout) else VesselLayout.legacy(vessel_root)
        self.layout=layout
        self.root=layout.work_root
        self.asset_root=layout.asset_root
        self.state_root=layout.state_root
        self.store=StateStore(layout.state_path('grox.sqlite3'))
        self.durable=DurableState(self.store)
        self.roster=CrewRoster(layout.asset_path('configs/crew/dossiers'),self.store)
        self.mission_control=MissionControl()
        self.gateway=LayoutToolGateway(
            layout, policy=gateway_policy, extra_allowed_origins=extra_allowed_origins,
            secret_broker=secret_broker, mcp_registry=mcp_registry,
        )
        self._tool_awareness=ToolCapabilityAwareness(self.gateway)
        self._cognition_transport_observations:dict[str,Any]={}
        self._cognition_endpoint_observations:dict[str,Any]={}
        self.executor=CrewExecutor(self.gateway,self.durable)
        self.verifier=IndependentVerifier()
        self.intelligence=LivingCompanyIntelligence(self.store,self.roster)
        self.exception_loop=ExecutiveExceptionLoop(self.durable)
        self.evaluation=OrchestrationEvaluator(self.store,self.durable,self.roster)
        self.reasoner=build_reasoner_from_env(layout=layout) if reasoner is _AUTO else reasoner
        local_runtime=getattr(self.reasoner,'runtime',None) if self.reasoner else None
        self._live_environment=(
            LiveEnvironmentAwareness(
                local_runtime, observation_recorder=self.store.record_resource_observation
            )
            if isinstance(local_runtime,LocalModelRuntime) else None
        )

    @property
    def cognitive_status(self)->str:
        return getattr(self.reasoner,'name','deterministic-only') if self.reasoner else 'deterministic-only'

    def live_resource_inventory(self, policy:ResourcePolicy, *, placement:str='gorxu')->dict[str,Any]:
        """Return fresh bounded local-resource state without activating anything.

        A Pilot without a bound LocalModelRuntime reports the local live-resource
        surface unavailable rather than fabricating discovery or availability.
        """
        if self._live_environment is None:
            return {
                'schema':'grox-live-environment-inventory-v1',
                'status':'unavailable',
                'placement':placement,
                'resources':[],
                'authority_changed':False,
                'auto_activation':False,
            }
        inventory=self._live_environment.inventory(policy,placement=placement).to_dict()
        return {'status':'ok',**inventory}

    def select_live_resource(self, policy:ResourcePolicy, *, placement:str='gorxu')->LiveResourceSnapshot:
        """Select within explicit policy; selection never loads or activates."""
        if self._live_environment is None:
            raise ResourceSelectionError('Pilot has no bound local model runtime for live-resource selection')
        return self._live_environment.select(policy,placement=placement)

    def live_resource_history(self, resource_id:str|None=None, *, limit:int=20)->list[dict[str,Any]]:
        """Return durable historical execution identity; never current readiness."""
        return self.store.resource_observations(resource_id=resource_id,limit=limit)

    def live_tool_capability_inventory(self, *, order:MissionOrder|None=None)->dict[str,Any]:
        """Return fresh governed A5 capability state without invoking tools."""
        return self._tool_awareness.inventory(order=order)

    def _cognition_provider_awareness(self)->CognitionProviderAwareness:
        crew_provider=getattr(self.executor,'cognition_provider',None)
        return CognitionProviderAwareness(
            reasoner=self.reasoner,
            crew_provider=crew_provider,
            gateway=self.gateway,
            transport_observations=self._cognition_transport_observations,
            endpoint_observations=self._cognition_endpoint_observations,
        )

    def live_cognition_provider_inventory(self, *, policy:CognitionProviderPolicy|None=None)->dict[str,Any]:
        """Return fresh hosted cognition binding state without invoking providers."""
        return self._cognition_provider_awareness().inventory(policy=policy)

    def live_configured_cognition_inventory(self)->dict[str,Any]:
        """Discover supported non-secret cognition configuration without binding or invocation."""
        return ConfiguredCognitionDiscovery(nonsecret_reasoner_config_from_env()).inventory()

    def live_configured_connection_policy_inventory(self, *, order:MissionOrder|None=None)->dict[str,Any]:
        """Report configured remote connection policy state without network or provider activity."""
        inventory=self.live_configured_cognition_inventory()
        resources=inventory.get('resources') or []
        resource=resources[0] if len(resources)==1 else {}
        return ConfiguredConnectionPolicyAwareness(self.gateway).inventory(resource=resource,order=order)

    def live_configured_local_cognition_readiness_inventory(self)->dict[str,Any]:
        """Report explicit non-activating readiness for configured local llama.cpp cognition."""
        inventory=self.live_configured_cognition_inventory()
        resources=inventory.get('resources') or []
        resource=resources[0] if len(resources)==1 else {}
        executable=os.getenv('GROX_LLAMA_CPP_EXECUTABLE','').strip()
        return ConfiguredLocalCognitionReadiness(self.layout).inventory(resource=resource,executable=executable)

    def refresh_cognition_transport(self, *, resource_id:str, order:MissionOrder)->dict[str,Any]:
        """Refresh bounded remote-origin transport evidence through the governed Tool Gateway."""
        return self._cognition_provider_awareness().refresh_transport(resource_id=resource_id,order=order)

    def refresh_cognition_endpoint_surface(self, *, resource_id:str, order:MissionOrder)->dict[str,Any]:
        """Refresh exact bound remote endpoint-surface evidence through the governed Tool Gateway."""
        return self._cognition_provider_awareness().refresh_endpoint_surface(resource_id=resource_id,order=order)

    def _required_caps(self, mode:MissionMode)->list[str]:
        return {'inspect':['repo_read'],'repair':['repo_read','repo_write'],'verify':['repo_read','verify'],'execute':['repo_read']}[mode.value]

    def _roster_summary(self)->list[dict[str,Any]]:
        # Cognitive discovery receives descriptive Crew metadata only. Capability
        # and tag gates remain local deterministic routing inputs.
        return self.roster.cognitive_directory()

    def _reasoner_usage(self)->dict[str,Any]|None:
        getter=getattr(self.reasoner,'usage_snapshot',None) if self.reasoner else None
        if not callable(getter): return None
        try:
            usage=getter()
            if usage is None: return None
            if hasattr(usage,'to_dict') and callable(usage.to_dict):
                return usage.to_dict()
            if isinstance(usage,dict):
                return dict(usage)
        except (AttributeError,TypeError,ValueError):
            # Usage telemetry is observational only and must not become a new
            # execution dependency or authority gate.
            return None
        return None

    def _interpret(self,directive:str):
        if not self.reasoner: return None,None,None
        try:
            brief=self.reasoner.interpret(directive,roster=self._roster_summary())
            return brief,None,self._reasoner_usage()
        except (ReasoningError,ValueError,TypeError) as e:
            return None,str(e),self._reasoner_usage()

    def ask(self, message: str) -> dict[str, Any]:
        """Return one direct GorXu assistant response without creating a Mission.

        Direct cognition is advisory text only. It cannot route Crew, issue a
        Mission Order, mutate the Vessel, or widen authority.
        """
        if not isinstance(message, str) or not message.strip():
            raise ValueError("Commander input must be a non-empty string")
        if len(message) > 32768:
            raise ValueError("Commander input exceeds the bounded direct-assistance ceiling")
        provider = self.cognitive_status
        if not self.reasoner:
            return {
                "status": "cognition_unavailable", "commander_input": message, "response": None,
                "provider": provider, "error": "no cognitive provider is configured",
                "mission_created": False, "crew_delegated": False, "authority_changed": False,
            }
        responder = getattr(self.reasoner, "respond", None)
        if not callable(responder):
            return {
                "status": "cognition_unavailable", "commander_input": message, "response": None,
                "provider": provider, "error": "configured cognitive provider has no direct-assistance capability",
                "mission_created": False, "crew_delegated": False, "authority_changed": False,
            }
        try:
            turn = responder(message)
            if not isinstance(turn, AssistantResponse):
                raise ReasoningError("direct-assistance provider returned the wrong contract type")
        except (ReasoningError, ValueError, TypeError) as exc:
            return {
                "status": "cognition_unavailable", "commander_input": message, "response": None,
                "provider": provider, "error": str(exc),
                "mission_created": False, "crew_delegated": False, "authority_changed": False,
            }
        return {
            "status": "answered", "commander_input": turn.commander_input, "response": turn.response,
            "provider": provider, "usage": self._reasoner_usage(),
            "mission_created": False, "crew_delegated": False, "authority_changed": False,
        }

    def _reconcile_mode(self,directive:str,explicit:MissionMode|None,brief)->MissionMode:
        policy=self.mission_control.infer_mode(directive,explicit)
        if explicit or not brief: return policy
        if policy is MissionMode.execute and brief.proposed_mode=='inspect':
            return MissionMode.inspect
        return policy

    def _reconcile_risk(self,directive:str,explicit:RiskClass|None,brief)->RiskClass:
        policy=self.mission_control.assess_risk(directive,explicit)
        if not brief or not brief.proposed_risk: return policy
        proposed=RiskClass(brief.proposed_risk)
        return proposed if _RISK_RANK[proposed] > _RISK_RANK[policy] else policy

    def _select_crew(self,directive:str,required:list[str],crew_id:str|None,brief,risk:RiskClass):
        if crew_id:
            return self.roster.get(crew_id), None
        preferred=brief.candidate_crew_ids if brief else []
        decision=self.intelligence.route(directive,required,risk=risk,preferred_ids=preferred)
        return decision.crew, decision

    def _record_unexpected_defect(self, mission_id:str, *, context:dict[str,Any], exc:Exception)->dict[str,Any]:
        trace=''.join(traceback.format_exception(type(exc),exc,exc.__traceback__))[-12000:]
        payload={
            'classification':'unexpected_defect',
            'exception_type':type(exc).__name__,
            'message':str(exc),
            'traceback':trace,
            'context':context,
        }
        self.store.add_evidence(mission_id,'GORXU-FAULT',Evidence('unexpected_defect',payload))
        return payload

    def _mission_outcome(self, order:MissionOrder, result:TourResult, verification:dict|None)->dict[str,Any]:
        kinds={ev.kind for ev in result.evidence}
        operation=str(order.parameters.get('operation') or '')
        verification_scope='bounded_execution_evidence' if verification else None
        if result.status!='completed':
            rollback=next((ev.content for ev in reversed(result.evidence) if ev.kind=='mutation_rollback'),None)
            rollback_completed=isinstance(rollback,dict) and rollback.get('status')=='rolled_back'
            exception_type=str((result.exception or {}).get('type') or '')
            mutation_observed='mutation' in kinds
            mutation_unresolved=(mutation_observed and not rollback_completed) or exception_type=='mutation_state_diverged'
            effect='mutation_rolled_back' if mutation_observed and rollback_completed else ('mutation_state_unresolved' if mutation_unresolved else 'exception')
            return {
                'execution':result.status,
                'effect':effect,
                'objective':'not_delivered',
                'mutation':mutation_unresolved,
                'next_authority':'pilot_recovery' if mutation_unresolved else None,
                'verification_scope':verification_scope,
            }
        if order.mode is MissionMode.execute and 'inventory' in kinds:
            return {
                'execution':'completed',
                'effect':'scan_only',
                'objective':'not_delivered',
                'mutation':False,
                'next_authority':'explicit_operation_or_repair',
                'verification_scope':verification_scope,
            }
        if order.mode is MissionMode.repair and operation=='write_text':
            mutated='mutation' in kinds
            return {
                'execution':'completed',
                'effect':'mutation_applied' if mutated else 'mutation_verified',
                'objective':'satisfied',
                'mutation':mutated,
                'next_authority':None,
                'verification_scope':verification_scope,
            }
        if order.mode in {MissionMode.inspect,MissionMode.verify}:
            return {
                'execution':'completed',
                'effect':'inspection',
                'objective':'not_proven',
                'mutation':False,
                'next_authority':None,
                'verification_scope':verification_scope,
            }
        return {
            'execution':'completed',
            'effect':operation or 'governed_execute',
            'objective':'not_proven',
            'mutation':False,
            'next_authority':None,
            'verification_scope':verification_scope,
        }

    def command(self, directive:str, *, mode:MissionMode|None=None, risk:RiskClass|None=None, crew_id:str|None=None, scope:str='.', parameters:dict|None=None)->dict:
        brief,cognition_error,cognition_usage=self._interpret(directive)
        mode=self._reconcile_mode(directive,mode,brief)
        risk=self._reconcile_risk(directive,risk,brief)
        mission_id=f"MSN-{uuid.uuid4().hex[:12]}"; self.store.create_mission(mission_id,directive,mode.value,risk.value)
        if cognition_usage:
            self.store.add_evidence(mission_id,'GORXU-COGNITION',Evidence('cognitive_usage',cognition_usage))
        req=self._required_caps(mode)
        try:
            crew,routing=self._select_crew(directive,req,crew_id,brief,risk)
            if not set(req).issubset(crew.capabilities): raise LookupError(f"Crew {crew.crew_id} lacks required capabilities {req}")
            actions=self.mission_control.default_actions(mode)
            objective=brief.objective if brief else directive
            order=MissionOrder.new(mission_id,directive,objective,mode,crew.crew_id,required_capabilities=req,allowed_actions=actions,
                forbidden_actions=[] if mode is MissionMode.repair else ['fs_write'],scope=[scope],risk_class=risk,
                verification_requirements=['independent'] if self.mission_control.verification_required(mode,risk) else [],
                stop_conditions=['blocker','better_or_safer_path','missing_capability','elevated_risk','scope_change','irreversible_consequence'],parameters=parameters or {})
            memory_meta=self.intelligence.inject_order_context(order,objective)
            self.store.save_order(order)
            self.store.add_evidence(mission_id,order.order_id,Evidence('routing_decision',routing.to_dict() if routing else {
                'source':'explicit_crew_assignment','crew_id':crew.crew_id,'task_class':memory_meta['task_class']}))
            self.store.add_evidence(mission_id,order.order_id,Evidence('memory_selection',memory_meta))
            if brief:
                self.store.add_evidence(mission_id,order.order_id,Evidence('cognitive_plan',{'provider':self.cognitive_status,**brief.to_dict()}))
            if cognition_error:
                self.store.add_evidence(mission_id,order.order_id,Evidence('cognition_degraded',{'provider':self.cognitive_status,'error':cognition_error,'fallback':'deterministic control plane'}))
            self.store.crew_on_duty(crew.crew_id,mission_id); self.store.update_order(order.order_id,'running')
            started=perf_counter()
            result=self.executor.execute(order)
            elapsed_ms=(perf_counter()-started)*1000.0
            for ev in result.evidence: self.store.add_evidence(mission_id,order.order_id,ev)
            if result.exception:
                self.store.add_evidence(mission_id,order.order_id,Evidence('crew_exception',dict(result.exception)))
            self.store.update_order(order.order_id,result.status); self.store.crew_sleep(crew.crew_id,mission_id,result.summary)

            verification=None
            if result.status=='completed' and self.mission_control.verification_required(mode,risk):
                vrouting=self.intelligence.route(f"verify {directive}",['repo_read','verify'],exclude=[crew.crew_id],verifier=True,risk=risk)
                vcrew=vrouting.crew
                vorder=MissionOrder.new(mission_id,directive,f"Independently verify order {order.order_id}",MissionMode.verify,vcrew.crew_id,
                    required_capabilities=['repo_read','verify'],allowed_actions=['fs_list','fs_read','test_run'],forbidden_actions=['fs_write'],scope=[scope],risk_class=risk,parent_order_id=order.order_id)
                vmemory=self.intelligence.inject_order_context(vorder,vorder.objective)
                self.store.save_order(vorder)
                self.store.add_evidence(mission_id,vorder.order_id,Evidence('routing_decision',vrouting.to_dict()))
                self.store.add_evidence(mission_id,vorder.order_id,Evidence('memory_selection',vmemory))
                self.store.crew_on_duty(vcrew.crew_id,mission_id); self.store.update_order(vorder.order_id,'running')
                vstarted=perf_counter()
                ok,msg=self.verifier.verify(crew.crew_id,vcrew.crew_id,result)
                vlatency_ms=(perf_counter()-vstarted)*1000.0
                vev=Evidence('independent_verification',{'ok':ok,'message':msg,'executor':crew.crew_id,'verifier':vcrew.crew_id})
                self.store.add_evidence(mission_id,vorder.order_id,vev); self.store.update_order(vorder.order_id,'completed' if ok else 'exception'); self.store.crew_sleep(vcrew.crew_id,mission_id,msg)
                verification={'ok':ok,'message':msg,'verifier':vcrew.crew_id,'order_id':vorder.order_id}
                vresult=TourResult(vorder.order_id,vcrew.crew_id,'completed' if ok else 'exception',msg,[vev],None if ok else {'type':'verification_failure'})
                self.intelligence.record_performance(crew_id=vcrew.crew_id,mission_id=mission_id,order_id=vorder.order_id,task_class=vorder.parameters['_task_class'],result=vresult,latency_ms=vlatency_ms,risk=risk,verified=None)
                if not ok: result.status='exception'

            self.intelligence.record_performance(
                crew_id=crew.crew_id,mission_id=mission_id,order_id=order.order_id,task_class=order.parameters['_task_class'],
                result=result,latency_ms=elapsed_ms,risk=risk,verified=verification['ok'] if verification else None,
            )
            outcome=self._mission_outcome(order,result,verification)
            self.store.add_evidence(mission_id,order.order_id,Evidence('mission_outcome',outcome))
            summary=f"GorXu: {result.summary}"
            if brief: summary += f" | Cognitive strategy: {brief.recommended_option or 'structured interpretation'} ({brief.confidence:.2f})"
            if cognition_error: summary += " | Cognitive provider degraded; deterministic fallback used"
            if result.exception: summary += f" | Exception returned to Pilot: {result.exception['type']}"
            summary += (
                f" | Outcome: effect={outcome['effect']}; objective={outcome['objective']}; "
                f"mutation={'yes' if outcome['mutation'] else 'no'}"
            )
            if outcome['next_authority']:
                summary += f"; next_authority={outcome['next_authority']}"
            if verification:
                scope_note='; bounded execution evidence only' if outcome['objective']!='satisfied' else ''
                summary += f" | Verification: {'PASS' if verification['ok'] else 'FAIL'} by {verification['verifier']}{scope_note}"
            mission_status='scan_only' if result.status=='completed' and outcome['effect']=='scan_only' else ('completed' if result.status=='completed' else 'needs_pilot_decision')
            self.store.update_mission(mission_id,mission_status,summary)
            public_status=mission_status if mission_status=='scan_only' else result.status
            return {'mission_id':mission_id,'mode':mode.value,'risk':risk.value,'crew':crew.crew_id,'status':public_status,'execution_status':result.status,
                    'mission_status':mission_status,'outcome':outcome,'summary':summary,'verification':verification,'exception':result.exception,
                    'cognition':brief.to_dict() if brief else None,'cognition_error':cognition_error}
        except LookupError as exc:
            summary=f"GorXu bounded routing exception: {exc}"
            self.store.add_graph_event(
                mission_id,'routing_exception',
                {'cause_type':type(exc).__name__,'message':str(exc),'operation':'command'},
            )
            self.store.update_mission(mission_id,'needs_pilot_decision',summary)
            return {'mission_id':mission_id,'mode':mode.value,'risk':risk.value,'status':'needs_pilot_decision','summary':summary,
                    'exception':{'type':'routing_exception','cause_type':type(exc).__name__,'message':str(exc)},
                    'cognition':brief.to_dict() if brief else None,'cognition_error':cognition_error}
        except Exception as exc:
            defect=self._record_unexpected_defect(mission_id,context={'operation':'command','directive':directive,'mode':mode.value,'risk':risk.value},exc=exc)
            summary=f"GorXu contained unexpected defect: {defect['exception_type']}: {defect['message']}"
            self.store.update_mission(mission_id,'unexpected_defect',summary)
            return {'mission_id':mission_id,'mode':mode.value,'risk':risk.value,'status':'unexpected_defect','summary':summary,
                    'exception':{'type':'unexpected_defect',**defect},'cognition':brief.to_dict() if brief else None,'cognition_error':cognition_error}

    def command_graph(
        self,
        directive: str,
        *,
        plan: MissionGraphPlan | dict | None = None,
        risk: RiskClass | None = None,
        allow_repair: bool = False,
        plan_source: str | None = None,
    ) -> dict:
        global_risk = self.mission_control.assess_risk(directive, risk)
        mission_id = f"MSN-{uuid.uuid4().hex[:12]}"
        self.store.create_mission(mission_id, directive, 'graph', global_risk.value)
        try:
            if plan is None:
                planner = getattr(self.reasoner, 'plan_graph', None) if self.reasoner else None
                if not callable(planner):
                    raise ReasoningError('active cognitive provider does not supply Mission Graph planning')
                plan = planner(directive, roster=self._roster_summary())
                graph_usage=self._reasoner_usage()
                if graph_usage:
                    self.store.add_evidence(mission_id,'GORXU-GRAPH-PLAN',Evidence('cognitive_usage',graph_usage))
            if isinstance(plan, dict):
                plan = MissionGraphPlan.from_mapping(plan, expected_intent=directive)
            if not isinstance(plan, MissionGraphPlan):
                raise TypeError('plan must be a MissionGraphPlan or mapping')
            if plan.commander_intent != directive:
                raise ValueError('Mission Graph must preserve Commander intent verbatim')
            plan.validate()

            source = plan_source or (self.cognitive_status if self.reasoner else 'explicit-validated-plan')
            self.store.add_evidence(mission_id,'GORXU-GRAPH-PLAN',Evidence('mission_graph_plan', {'source': source, **plan.to_dict()}))
            self.durable.save_graph_run(mission_id, plan.to_dict(), global_risk.value, allow_repair)
            runner = MissionGraphRunner(
                store=self.store, roster=self.roster, executor=self.executor,
                mission_control=self.mission_control, verifier=self.verifier, intelligence=self.intelligence,
                exception_loop=self.exception_loop, durable=self.durable,
            )
            outcomes, synthesis = runner.run(mission_id=mission_id, directive=directive, plan=plan,global_risk=global_risk, allow_repair=allow_repair)
            self.store.add_evidence(mission_id,'GORXU-SYNTHESIS',Evidence('pilot_synthesis', synthesis.to_dict()))
            self.store.update_mission(mission_id, synthesis.outcome, synthesis.executive_summary)
            return {'mission_id': mission_id,'mode': 'graph','risk': global_risk.value,'status': synthesis.outcome,
                    'summary': synthesis.executive_summary,'plan_source': source,'graph': plan.to_dict(),
                    'nodes': {node_id: outcome.to_dict() for node_id, outcome in outcomes.items()},'synthesis': synthesis.to_dict()}
        except (ReasoningError,ValueError,TypeError,GraphExecutionError) as exc:
            summary = f"GorXu rejected bounded Mission Graph: {exc}"
            self.store.add_graph_event(mission_id,'graph_rejected',{'type':type(exc).__name__,'message':str(exc)})
            self.store.update_mission(mission_id,'needs_pilot_decision',summary)
            return {'mission_id':mission_id,'mode':'graph','risk':global_risk.value,'status':'needs_pilot_decision','summary':summary,
                    'exception':{'type':'graph_rejected','cause_type':type(exc).__name__,'message':str(exc)}}
        except Exception as exc:
            defect=self._record_unexpected_defect(mission_id,context={'operation':'command_graph','directive':directive,'risk':global_risk.value},exc=exc)
            self.store.add_graph_event(mission_id,'unexpected_defect',{'exception_type':defect['exception_type'],'message':defect['message']})
            summary=f"GorXu contained unexpected graph defect: {defect['exception_type']}: {defect['message']}"
            self.store.update_mission(mission_id,'unexpected_defect',summary)
            return {'mission_id':mission_id,'mode':'graph','risk':global_risk.value,'status':'unexpected_defect','summary':summary,
                    'exception':{'type':'unexpected_defect',**defect}}

    def resume_graph(self, mission_id: str) -> dict:
        run=self.durable.graph_run(mission_id)
        mission=self.store.mission(mission_id)
        if not run or not mission:
            return {'mission_id':mission_id,'mode':'graph','status':'needs_pilot_decision','summary':'Unknown durable Mission Graph'}
        if run['cancelled']:
            return {'mission_id':mission_id,'mode':'graph','status':'cancelled','summary':'Mission Graph was cancelled and will not resume'}
        if int(run['resume_count']) >= 3:
            summary='Durable Mission Graph resume budget exhausted; GorXu requires Pilot review'
            self.store.update_mission(mission_id,'needs_pilot_decision',summary)
            return {'mission_id':mission_id,'mode':'graph','status':'needs_pilot_decision','summary':summary,'resume_count':run['resume_count']}
        directive=mission['mission']['directive']
        global_risk=RiskClass(run['global_risk'])
        resume_count=self.durable.increment_resume(mission_id)
        self.store.update_mission(mission_id,'running',f'GorXu resuming durable Mission Graph; resume_count={resume_count}')
        self.store.add_graph_event(mission_id,'mission_resumed',{'resume_count':resume_count})
        try:
            plan=MissionGraphPlan.from_mapping(run['plan'],expected_intent=directive)
            runner=MissionGraphRunner(store=self.store,roster=self.roster,executor=self.executor,mission_control=self.mission_control,
                verifier=self.verifier,intelligence=self.intelligence,exception_loop=self.exception_loop,durable=self.durable)
            outcomes,synthesis=runner.run(mission_id=mission_id,directive=directive,plan=plan,global_risk=global_risk,allow_repair=run['allow_repair'],resume=True)
            self.store.add_evidence(mission_id,'GORXU-SYNTHESIS',Evidence('pilot_synthesis',{'resume_count':resume_count,**synthesis.to_dict()}))
            self.store.update_mission(mission_id,synthesis.outcome,synthesis.executive_summary)
            return {'mission_id':mission_id,'mode':'graph','risk':global_risk.value,'status':synthesis.outcome,
                    'summary':synthesis.executive_summary,'resume_count':resume_count,'graph':plan.to_dict(),
                    'nodes':{node_id:outcome.to_dict() for node_id,outcome in outcomes.items()},'synthesis':synthesis.to_dict()}
        except (ValueError,GraphExecutionError) as exc:
            summary=f'GorXu rejected durable Mission Graph resume: {exc}'
            self.store.add_graph_event(mission_id,'resume_rejected',{'type':type(exc).__name__,'message':str(exc)})
            self.store.update_mission(mission_id,'needs_pilot_decision',summary)
            return {'mission_id':mission_id,'mode':'graph','risk':global_risk.value,'status':'needs_pilot_decision','summary':summary,
                    'exception':{'type':'resume_rejected','cause_type':type(exc).__name__,'message':str(exc)},'resume_count':resume_count}
        except Exception as exc:
            defect=self._record_unexpected_defect(mission_id,context={'operation':'resume_graph','resume_count':resume_count,'risk':global_risk.value},exc=exc)
            self.store.add_graph_event(mission_id,'unexpected_defect',{'exception_type':defect['exception_type'],'message':defect['message']})
            summary=f"GorXu contained unexpected resume defect: {defect['exception_type']}: {defect['message']}"
            self.store.update_mission(mission_id,'unexpected_defect',summary)
            return {'mission_id':mission_id,'mode':'graph','risk':global_risk.value,'status':'unexpected_defect','summary':summary,
                    'exception':{'type':'unexpected_defect',**defect},'resume_count':resume_count}

    def cancel_graph(self, mission_id: str, reason: str='Cancelled by Commander/Pilot authority') -> dict:
        run=self.durable.graph_run(mission_id)
        if not run:
            return {'mission_id':mission_id,'status':'needs_pilot_decision','summary':'Unknown durable Mission Graph'}
        self.durable.cancel_graph_run(mission_id,reason)
        self.store.add_graph_event(mission_id,'mission_cancelled',{'reason':reason})
        return {'mission_id':mission_id,'status':'cancelled','summary':reason}

    def evaluate_mission(self, mission_id:str, *, suite:str='operational-history')->dict:
        return self.evaluation.capture_mission(mission_id,suite=suite)

    def find_routing_improvement(self, suite:str)->dict:
        return self.evaluation.find_routing_improvement(suite)

    def propose_improvement(self, *, proposal_type:str, target:str, proposed_change:dict, rationale:str, evidence:dict)->str:
        return self.evaluation.propose(proposal_type=proposal_type,target=target,proposed_change=proposed_change,rationale=rationale,evidence=evidence)

    def activate_improvement(self, proposal_id:str)->None:
        self.evaluation.activate_proposal(proposal_id)

    def repair_write(self,path:str,content:str,*,risk:RiskClass|None=None,crew_id:str|None=None)->dict:
        return self.command(f"Repair {path} by writing Commander-approved content",mode=MissionMode.repair,risk=risk,crew_id=crew_id,scope=path,parameters={'operation':'write_text','path':path,'content':content})