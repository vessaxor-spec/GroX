from __future__ import annotations
from ..contracts import TourResult

class IndependentVerifier:
    def verify(self, executor_id:str, verifier_id:str, result:TourResult)->tuple[bool,str]:
        if executor_id==verifier_id: return False,'Verifier is not independent from executor'
        if result.status!='completed': return False,f"Executor status is {result.status}"
        kinds={e.kind for e in result.evidence}
        if not kinds: return False,'No evidence supplied'
        tests=[e for e in result.evidence if e.kind=='test_run']
        if tests and any(e.content.get('returncode')!=0 for e in tests): return False,'Test evidence contains failure'
        return True,f"Independent evidence review passed ({', '.join(sorted(kinds))})"
