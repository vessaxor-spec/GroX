from __future__ import annotations
import hashlib
from ..contracts import MissionOrder, MissionMode, TourResult, Evidence
from ..tools.gateway import ToolGateway, ToolDenied
from ..durable_state import DurableState

class CrewExecutor:
    def __init__(self, gateway:ToolGateway, durable:DurableState|None=None):
        self.gateway=gateway; self.store=durable

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
            test=self.gateway.run_tests(order); evidence.append(Evidence('test_run',test))
            if test['returncode']!=0:
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
                    except Exception as exc:
                        evidence.append(Evidence('mutation_rollback',{'idempotency_key':key,'status':'failed','error':str(exc)}))
                        return TourResult(order.order_id,order.assigned_crew,'exception','Repair verification failed and rollback could not safely reconcile target state',evidence,
                                          {'type':'mutation_state_diverged','irreversible':True,'rollback':'failed','recommendation':'Return to GorXu; do not overwrite divergent state'})
                else:
                    rollback='unavailable'
                return TourResult(order.order_id,order.assigned_crew,'exception','Repair applied but tests failed',evidence,
                                  {'type':'post_repair_test_failure','rollback':rollback,'recommendation':'Stop further mutation and return to GorXu'})
        if self.store is not None:
            self.store.update_mutation(key,'verified',after_sha256=self.gateway.current_hash(target))
        return TourResult(order.order_id,order.assigned_crew,'completed',f"Repaired {target}",evidence)

    def execute(self, order:MissionOrder)->TourResult:
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
