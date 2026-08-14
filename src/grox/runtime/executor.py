from __future__ import annotations
from pathlib import Path
from ..contracts import MissionOrder, MissionMode, TourResult, Evidence
from ..tools.gateway import ToolGateway, ToolDenied

class CrewExecutor:
    def __init__(self, gateway:ToolGateway): self.gateway=gateway

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
                target=order.parameters['path']; content=order.parameters['content']
                before=None
                p=(self.gateway.root/target)
                if p.exists(): before=self.gateway.hash_file(order,target)
                result=self.gateway.write_text(order,target,content)
                evidence.append(Evidence('mutation',{'operation':'write_text','before_sha256':before,**result}))
                if 'test_run' in order.allowed_actions:
                    test=self.gateway.run_tests(order); evidence.append(Evidence('test_run',test))
                    if test['returncode']!=0:
                        return TourResult(order.order_id,order.assigned_crew,'exception','Repair applied but tests failed',evidence,{'type':'post_repair_test_failure','recommendation':'Stop further mutation and return to GorXu'})
                return TourResult(order.order_id,order.assigned_crew,'completed',f"Repaired {target}",evidence)

            files=self.gateway.list_path(order,order.scope[0] if order.scope else '.')
            evidence.append(Evidence('inventory',{'files':files[:100],'count':len(files)}))
            return TourResult(order.order_id,order.assigned_crew,'completed',f"Executed bounded mission context scan across {len(files)} files",evidence)
        except (ToolDenied,FileNotFoundError,IsADirectoryError) as e:
            return TourResult(order.order_id,order.assigned_crew,'exception',str(e),evidence,{'type':type(e).__name__,'recommendation':'Return to GorXu; do not widen authority'})
