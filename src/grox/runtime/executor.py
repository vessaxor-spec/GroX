from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
import hashlib
import json
from typing import Any

from ..contracts import MissionOrder, MissionMode, TourResult, Evidence
from ..crew_cognition import CrewCognitionDenied, CrewCognitionError, CrewCognitionStep
from ..tools.gateway import ToolGateway, ToolDenied
from ..durable_state import DurableState


def _plain(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_plain(item) for item in value]
    return value


class CrewExecutor:
    def __init__(
        self,
        gateway:ToolGateway,
        durable:DurableState|None=None,
        *,
        cognition_provider:Any=None,
        cognition_max_steps:int=4,
        cognition_observation_chars:int=8000,
        cognition_max_test_runs:int=1,
        cognition_work_product_chars:int=4000,
    ):
        self.gateway=gateway; self.store=durable
        self.cognition_provider=cognition_provider
        self.cognition_max_steps=max(1,min(8,int(cognition_max_steps)))
        self.cognition_observation_chars=max(256,min(32000,int(cognition_observation_chars)))
        self.cognition_max_test_runs=max(0,min(1,int(cognition_max_test_runs)))
        self.cognition_work_product_chars=max(256,min(8192,int(cognition_work_product_chars)))

    def _repair_write_text(self, order:MissionOrder)->TourResult:
        evidence=[]
        target=order.parameters['path']; content=order.parameters['content']
        intended_sha=hashlib.sha256(content.encode('utf-8')).hexdigest()
        key=str(order.parameters.get('_idempotency_key') or order.order_id)
        journal=None
        if self.store is not None:
            journal=self.store.mutation(key)
            if journal is None:
                before=self.gateway.capture_text(order,target)
                journal=self.store.begin_mutation(
                    idempotency_key=key, mission_id=order.mission_id, order_id=order.order_id,
                    target=target, before_exists=before['exists'], before_content=before['content'],
                    before_sha256=before['sha256'], intended_sha256=intended_sha,
                )
            if journal['intended_sha256'] != intended_sha or journal['target'] != target:
                return TourResult(order.order_id,order.assigned_crew,'exception','Idempotency key conflicts with a different mutation',evidence,
                                  {'type':'mutation_state_diverged','irreversible':True,'recommendation':'Return to GorXu; do not overwrite journaled mutation state'})
            current=self.gateway.current_hash(target)
            if journal['status']=='rolled_back':
                return TourResult(order.order_id,order.assigned_crew,'exception','Prior attempt was rolled back; a new Pilot-authorized attempt is required',evidence,
                                  {'type':'mutation_rolled_back','recommendation':'Return to GorXu for a fresh bounded repair attempt'})
            if journal['status']=='verified':
                expected=journal['after_sha256'] or intended_sha
                if current!=expected:
                    return TourResult(order.order_id,order.assigned_crew,'exception','Verified mutation target later diverged from journaled state',evidence,
                                      {'type':'mutation_state_diverged','irreversible':True,'recommendation':'Return to GorXu; reconcile external change'})
                evidence.append(Evidence('idempotent_replay',{'idempotency_key':key,'path':target,'sha256':current,'status':'verified'}))
                return TourResult(order.order_id,order.assigned_crew,'completed',f"Repaired {target}; idempotent replay confirmed",evidence)
            if journal['status']=='prepared':
                before_sha=journal['before_sha256']
                if current==intended_sha:
                    self.store.update_mutation(key,'applied',after_sha256=current)
                elif current==before_sha or (not journal['before_exists'] and current is None):
                    result=self.gateway.write_text(order,target,content)
                    self.store.update_mutation(key,'applied',after_sha256=result['sha256'])
                else:
                    return TourResult(order.order_id,order.assigned_crew,'exception','Prepared mutation target diverged from both pre-state and intended state',evidence,
                                      {'type':'mutation_state_diverged','irreversible':True,'recommendation':'Return to GorXu; do not guess through conflicting state'})
            elif journal['status']=='applied':
                expected=journal['after_sha256'] or intended_sha
                if current!=expected:
                    return TourResult(order.order_id,order.assigned_crew,'exception','Applied mutation target changed outside the journal before verification',evidence,
                                      {'type':'mutation_state_diverged','irreversible':True,'recommendation':'Return to GorXu; do not overwrite external state'})
            journal=self.store.mutation(key)
            evidence.append(Evidence('mutation',{'operation':'write_text','idempotency_key':key,'before_sha256':journal['before_sha256'],
                                                 'path':target,'sha256':journal['after_sha256'],'journal_status':'applied'}))
        else:
            before=None
            p=(self.gateway.root/target)
            if p.exists(): before=self.gateway.hash_file(order,target)
            result=self.gateway.write_text(order,target,content)
            evidence.append(Evidence('mutation',{'operation':'write_text','before_sha256':before,**result}))

        if 'test_run' in order.allowed_actions:
            try:
                test=self.gateway.run_tests(order)
                evidence.append(Evidence('test_run',test))
                verification_failed=test['returncode']!=0
                failure_summary='Repair applied but tests failed'
                failure_type='post_repair_test_failure'
            except TimeoutError as exc:
                evidence.append(Evidence('test_run',{'status':'timeout','error':str(exc)}))
                verification_failed=True
                failure_summary='Repair applied but tests timed out'
                failure_type='post_repair_test_timeout'
            if verification_failed:
                if self.store is not None:
                    journal=self.store.mutation(key)
                    try:
                        rb=self.gateway.rollback_text(
                            order,target,existed=journal['before_exists'],content=journal['before_content'],
                            expected_current_sha256=journal['after_sha256'] or intended_sha,
                        )
                        self.store.update_mutation(key,'rolled_back')
                        evidence.append(Evidence('mutation_rollback',{'idempotency_key':key,**rb,'status':'rolled_back'}))
                        rollback='completed'
                    except (ToolDenied, OSError) as exc:
                        evidence.append(Evidence('mutation_rollback',{'idempotency_key':key,'status':'failed','error':str(exc)}))
                        return TourResult(order.order_id,order.assigned_crew,'exception','Repair verification failed and rollback could not safely reconcile target state',evidence,
                                          {'type':'mutation_state_diverged','irreversible':True,'rollback':'failed','recommendation':'Return to GorXu; do not overwrite divergent state'})
                else:
                    rollback='unavailable'
                return TourResult(order.order_id,order.assigned_crew,'exception',failure_summary,evidence,
                                  {'type':failure_type,'rollback':rollback,'recommendation':'Stop further mutation and return to GorXu'})
        if self.store is not None:
            self.store.update_mutation(key,'verified',after_sha256=self.gateway.current_hash(target))
        return TourResult(order.order_id,order.assigned_crew,'completed',f"Repaired {target}",evidence)

    def _cognition_order_envelope(self, order:MissionOrder)->dict[str,Any]:
        return {
            'mission_id':order.mission_id,
            'order_id':order.order_id,
            'commander_intent':order.commander_intent,
            'objective':order.objective,
            'mode':order.mode.value,
            'assigned_crew':order.assigned_crew,
            'required_capabilities':list(order.required_capabilities),
            'allowed_actions':list(order.allowed_actions),
            'forbidden_actions':list(order.forbidden_actions),
            'scope':list(order.scope),
            'risk_class':order.risk_class.value,
            'stop_conditions':list(order.stop_conditions),
        }

    def _assert_cognition_scope(self, order:MissionOrder, rel:str)->None:
        if not rel or Path(rel).is_absolute():
            raise CrewCognitionDenied(f"Crew cognition path is outside Mission scope: {rel}")
        root=self.gateway.root.resolve()
        target=(root/rel).resolve()
        try:
            target.relative_to(root)
        except ValueError as exc:
            raise CrewCognitionDenied(f"Crew cognition path escapes Vessel root: {rel}") from exc
        for scope_rel in order.scope or ('.',):
            scope=(root/scope_rel).resolve()
            try:
                scope.relative_to(root)
            except ValueError:
                continue
            if target==scope or target.is_relative_to(scope):
                return
        raise CrewCognitionDenied(f"Crew cognition path is outside Mission scope: {rel}")

    def _cognition_observation(self, order:MissionOrder, step:CrewCognitionStep)->tuple[dict[str,Any],dict[str,Any]]:
        if step.action in order.forbidden_actions or step.action not in order.allowed_actions:
            raise CrewCognitionDenied(f"Crew cognition action not granted by Mission Order: {step.action}")
        if step.action in {'fs_list','fs_read'}:
            assert step.path is not None
            self._assert_cognition_scope(order,step.path)
        if step.action=='fs_list':
            files=self.gateway.list_path(order,step.path or '.')
            visible=files[:100]
            provider={'action':'fs_list','path':step.path,'files':visible,'count':len(files),'truncated':len(files)>len(visible)}
            persistent={'action':'fs_list','path':step.path,'count':len(files),'visible_count':len(visible),
                        'sha256':hashlib.sha256(json.dumps(visible,sort_keys=True).encode()).hexdigest()}
            return provider,persistent
        if step.action=='fs_read':
            text=self.gateway.read_text(order,step.path or '.',limit=self.cognition_observation_chars)
            provider={'action':'fs_read','path':step.path,'content':text,'chars':len(text)}
            persistent={'action':'fs_read','path':step.path,'chars':len(text),'sha256':hashlib.sha256(text.encode()).hexdigest()}
            return provider,persistent
        if step.action=='test_run':
            result=self.gateway.run_tests(order)
            stdout=str(result.get('stdout') or '')[-self.cognition_observation_chars//2:]
            stderr=str(result.get('stderr') or '')[-self.cognition_observation_chars//2:]
            provider={'action':'test_run','returncode':result.get('returncode'),'stdout':stdout,'stderr':stderr}
            persistent={'action':'test_run','returncode':result.get('returncode'),
                        'stdout_sha256':hashlib.sha256(stdout.encode()).hexdigest(),
                        'stderr_sha256':hashlib.sha256(stderr.encode()).hexdigest()}
            return provider,persistent
        raise CrewCognitionDenied(f"Crew cognition action is outside the read-only seam: {step.action}")

    def _run_cognition(self, order:MissionOrder)->dict[str,Any]:
        provider=self.cognition_provider
        craft=_plain(order.parameters.get('_craft_context') or [])
        memory=_plain(order.parameters.get('_memory_context') or [])
        craft_meta=_plain(order.parameters.get('_craft_context_meta') or {})
        observations:list[dict[str,Any]]=[]
        evidence:list[Evidence]=[]
        test_runs=0
        for _ in range(self.cognition_max_steps):
            try:
                raw=provider.next_step(
                    order=_plain(self._cognition_order_envelope(order)),
                    craft_context=_plain(craft),
                    memory_context=_plain(memory),
                    observations=_plain(observations),
                )
            except (CrewCognitionError,ValueError,TypeError) as exc:
                return {'status':'degraded','error':str(exc),'evidence':evidence}
            try:
                step=CrewCognitionStep.from_mapping(raw)
            except CrewCognitionDenied as exc:
                return {'status':'denied','error':str(exc),'evidence':evidence}
            except (CrewCognitionError,ValueError,TypeError) as exc:
                return {'status':'degraded','error':str(exc),'evidence':evidence}
            if step.action=='finish':
                work_product=step.work_product or ''
                if len(work_product)>self.cognition_work_product_chars:
                    return {
                        'status':'degraded',
                        'error':f"Crew cognition work product exceeds bounded size: {len(work_product)} > {self.cognition_work_product_chars}",
                        'evidence':evidence,
                    }
                evidence.append(Evidence('crew_cognition',{
                    'provider':str(getattr(provider,'name','crew-cognition-provider')),
                    'work_product':work_product,
                    'craft_sha256':craft_meta.get('craft_sha256'),
                    'selected_headings':craft_meta.get('selected_headings') or [],
                    'selected_chars':craft_meta.get('selected_chars'),
                    'memory_ids':[item.get('memory_id') for item in memory if isinstance(item,dict) and item.get('memory_id') is not None],
                    'observation_count':len(observations),
                    'test_run_count':test_runs,
                    'mode':'read_only_inspect',
                }))
                return {'status':'completed','work_product':work_product,'evidence':evidence}
            if step.action=='test_run':
                if test_runs>=self.cognition_max_test_runs:
                    return {
                        'status':'denied',
                        'error':f"Crew cognition test_run budget exceeded: {self.cognition_max_test_runs}",
                        'evidence':evidence,
                    }
                test_runs+=1
            try:
                provider_observation,persistent=self._cognition_observation(order,step)
            except (CrewCognitionDenied,ToolDenied) as exc:
                return {'status':'denied','error':str(exc),'evidence':evidence}
            except (FileNotFoundError,IsADirectoryError,TimeoutError) as exc:
                return {'status':'degraded','error':str(exc),'evidence':evidence}
            observations.append(provider_observation)
            evidence.append(Evidence('crew_cognition_observation',persistent))
        return {
            'status':'degraded',
            'error':f"Crew cognition exceeded bounded step limit: {self.cognition_max_steps}",
            'evidence':evidence,
        }

    def _execute_deterministic(self, order:MissionOrder)->TourResult:
        evidence=[]
        try:
            if order.mode in {MissionMode.inspect,MissionMode.verify}:
                files=self.gateway.list_path(order,order.scope[0] if order.scope else '.')
                evidence.append(Evidence('inventory',{'scope':order.scope,'files':files,'count':len(files)}))
                test=None
                if 'test_run' in order.allowed_actions:
                    test=self.gateway.run_tests(order); evidence.append(Evidence('test_run',test))
                summary=f"Inspected {len(files)} files"
                if test is not None: summary += f"; tests returncode={test['returncode']}"
                status='completed' if test is None or test['returncode']==0 else 'exception'
                exc=None if status=='completed' else {'type':'verification_failure','recommendation':'Return to GorXu for diagnosis','evidence':'test_run'}
                return TourResult(order.order_id,order.assigned_crew,status,summary,evidence,exc)

            if order.mode is MissionMode.repair:
                op=order.parameters.get('operation')
                if op!='write_text':
                    return TourResult(order.order_id,order.assigned_crew,'exception','Repair requires an explicit supported operation',evidence,{'type':'unsupported_repair','recommendation':'GorXu must issue a narrower repair order'})
                return self._repair_write_text(order)

            op=order.parameters.get('operation')
            if op=='workspace_shell':
                result=self.gateway.workspace_shell(
                    order, str(order.parameters.get('script') or ''),
                    secret_env=order.parameters.get('secret_env') or {},
                )
                evidence.append(Evidence('workspace_execution',{**result,'side_effect_class':'private_workspace'}))
                if result['returncode']!=0:
                    return TourResult(order.order_id,order.assigned_crew,'exception','Isolated workspace command failed',evidence,
                                      {'type':'workspace_failure','recommendation':'Return to GorXu with workspace evidence'})
                return TourResult(order.order_id,order.assigned_crew,'completed','Completed isolated workspace execution',evidence)

            if op=='http_fetch':
                result=self.gateway.fetch_url(order,str(order.parameters.get('url') or ''))
                evidence.append(Evidence('network_fetch',{**result,'side_effect_class':'read_only_network','untrusted_content':True}))
                if int(result['status']) >= 400:
                    return TourResult(order.order_id,order.assigned_crew,'exception',f"Network fetch returned HTTP {result['status']}",evidence,
                                      {'type':'network_response_failure','recommendation':'Return to GorXu; do not broaden origin policy'})
                return TourResult(order.order_id,order.assigned_crew,'completed',f"Fetched granted origin {result['origin']}",evidence)

            if op=='browser_capture':
                result=self.gateway.browser_capture(order,str(order.parameters.get('url') or ''))
                evidence.append(Evidence('browser_capture',{**result,'side_effect_class':'private_evidence_capture','untrusted_content':True}))
                return TourResult(order.order_id,order.assigned_crew,'completed',f"Captured browser evidence for {result['origin']}",evidence)

            if op=='mcp_call':
                result=self.gateway.mcp_call(
                    order, str(order.parameters.get('adapter') or ''), str(order.parameters.get('tool') or ''),
                    dict(order.parameters.get('arguments') or {}),
                )
                evidence.append(Evidence('mcp_call',{**result,'side_effect_class':'external_adapter' if result.get('mutating') else 'read_only_adapter','untrusted_content':True}))
                return TourResult(order.order_id,order.assigned_crew,'completed',f"Called governed MCP adapter {result['adapter']}/{result['tool']}",evidence)

            files=self.gateway.list_path(order,order.scope[0] if order.scope else '.')
            evidence.append(Evidence('inventory',{'files':files[:100],'count':len(files)}))
            return TourResult(order.order_id,order.assigned_crew,'completed',f"Executed bounded mission context scan across {len(files)} files",evidence)
        except (ToolDenied,FileNotFoundError,IsADirectoryError,TimeoutError) as e:
            return TourResult(order.order_id,order.assigned_crew,'exception',str(e),evidence,{'type':type(e).__name__,'recommendation':'Return to GorXu; do not widen authority'})

    def execute(self, order:MissionOrder)->TourResult:
        # The first Crew-cognition slice is deliberately read-only Inspect only.
        # Verify, Repair, and Execute retain their existing deterministic paths.
        if self.cognition_provider is None or order.mode is not MissionMode.inspect:
            return self._execute_deterministic(order)
        run=self._run_cognition(order)
        prior=list(run.get('evidence') or [])
        if run['status']=='denied':
            prior.append(Evidence('crew_cognition_denied',{'error':run['error'],'mode':'read_only_inspect'}))
            return TourResult(
                order.order_id,order.assigned_crew,'exception',run['error'],prior,
                {'type':'crew_cognition_denied','recommendation':'Return to GorXu; do not widen Mission Order authority'},
            )
        if run['status']=='degraded':
            result=self._execute_deterministic(order)
            result.evidence=prior+result.evidence
            result.evidence.append(Evidence('crew_cognition_degraded',{
                'provider':str(getattr(self.cognition_provider,'name','crew-cognition-provider')),
                'error':run['error'],
                'fallback':'deterministic Crew executor',
            }))
            return result

        result=self._execute_deterministic(order)
        result.evidence.extend(prior)
        if result.status=='completed':
            result.summary += f"; Crew cognition: {run['work_product']}"
        return result
