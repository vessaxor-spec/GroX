from __future__ import annotations
from pathlib import Path
import hashlib, os, subprocess, tempfile
from ..contracts import MissionOrder, MissionMode

class ToolDenied(PermissionError): pass

class ToolGateway:
    def __init__(self, vessel_root: Path): self.root=vessel_root.resolve()

    def _resolve(self, rel:str)->Path:
        p=(self.root/rel).resolve()
        try: p.relative_to(self.root)
        except ValueError: raise ToolDenied(f"path escapes Vessel root: {rel}")
        return p

    def _allowed(self, order:MissionOrder, action:str):
        if action in order.forbidden_actions: raise ToolDenied(f"action explicitly forbidden: {action}")
        if action not in order.allowed_actions: raise ToolDenied(f"action not granted by Mission Order: {action}")
        if order.mode in {MissionMode.inspect,MissionMode.verify} and action in {'fs_write'}:
            raise ToolDenied(f"{order.mode.value} mode cannot mutate")

    def list_path(self, order:MissionOrder, rel:str='.'):
        self._allowed(order,'fs_list'); p=self._resolve(rel)
        if p.is_file(): return [str(p.relative_to(self.root))]
        out=[]
        for x in sorted(p.rglob('*')):
            if '.git' in x.parts or '__pycache__' in x.parts or x.name.endswith('.sqlite3'): continue
            if x.is_file(): out.append(str(x.relative_to(self.root)))
            if len(out)>=500: break
        return out

    def read_text(self, order:MissionOrder, rel:str, limit:int=200000):
        self._allowed(order,'fs_read'); p=self._resolve(rel)
        text=p.read_text(encoding='utf-8',errors='replace')
        return text[:limit]

    def capture_text(self, order:MissionOrder, rel:str, limit:int=262144):
        self._allowed(order,'fs_read'); p=self._resolve(rel)
        if not p.exists(): return {'exists':False,'content':None,'sha256':None}
        if p.is_dir(): raise IsADirectoryError(rel)
        raw=p.read_bytes()
        if len(raw)>limit: raise ToolDenied(f"rollback capture exceeds {limit} bytes: {rel}")
        try: text=raw.decode('utf-8')
        except UnicodeDecodeError as exc: raise ToolDenied(f"rollback capture requires UTF-8 text: {rel}") from exc
        return {'exists':True,'content':text,'sha256':hashlib.sha256(raw).hexdigest()}

    def hash_file(self, order:MissionOrder, rel:str):
        self._allowed(order,'fs_read'); p=self._resolve(rel)
        return hashlib.sha256(p.read_bytes()).hexdigest()

    def current_hash(self, rel:str):
        p=self._resolve(rel)
        if not p.exists(): return None
        if p.is_dir(): raise IsADirectoryError(rel)
        return hashlib.sha256(p.read_bytes()).hexdigest()

    def _assert_write_scope(self, order:MissionOrder, p:Path, rel:str):
        scopes=[self._resolve(s) for s in order.scope]
        if not any(p==s or (s.is_dir() and p.is_relative_to(s)) for s in scopes):
            raise ToolDenied(f"write target outside Mission scope: {rel}")

    def write_text(self, order:MissionOrder, rel:str, content:str):
        self._allowed(order,'fs_write'); p=self._resolve(rel); self._assert_write_scope(order,p,rel)
        p.parent.mkdir(parents=True,exist_ok=True)
        fd,tmp=tempfile.mkstemp(prefix=f'.{p.name}.grox-',dir=p.parent)
        try:
            with os.fdopen(fd,'w',encoding='utf-8') as fh:
                fh.write(content); fh.flush(); os.fsync(fh.fileno())
            os.replace(tmp,p)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)
        return {"path":str(p.relative_to(self.root)),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size}

    def rollback_text(self, order:MissionOrder, rel:str, *, existed:bool, content:str|None, expected_current_sha256:str|None):
        self._allowed(order,'fs_write'); p=self._resolve(rel); self._assert_write_scope(order,p,rel)
        current=self.current_hash(rel)
        if current!=expected_current_sha256:
            raise ToolDenied(f"rollback target diverged from journaled mutation: {rel}")
        if not existed:
            if p.exists(): p.unlink()
            return {'path':rel,'restored':'absent','sha256':None}
        if content is None: raise ToolDenied(f"rollback content missing: {rel}")
        result=self.write_text(order,rel,content)
        return {'path':rel,'restored':'content','sha256':result['sha256']}

    def run_tests(self, order:MissionOrder):
        self._allowed(order,'test_run')
        timeout=max(1,min(90,int(order.parameters.get('_graph_max_seconds',90))))
        try:
            cp=subprocess.run(['python','-m','unittest','discover','-s','tests','-v'],cwd=self.root,text=True,capture_output=True,timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError(f'test run exceeded {timeout}s') from exc
        return {"returncode":cp.returncode,"stdout":cp.stdout[-16000:],"stderr":cp.stderr[-16000:]}
