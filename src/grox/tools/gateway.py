from __future__ import annotations
from pathlib import Path
import hashlib, subprocess
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

    def hash_file(self, order:MissionOrder, rel:str):
        self._allowed(order,'fs_read'); p=self._resolve(rel)
        return hashlib.sha256(p.read_bytes()).hexdigest()

    def write_text(self, order:MissionOrder, rel:str, content:str):
        self._allowed(order,'fs_write'); p=self._resolve(rel)
        scopes=[self._resolve(s) for s in order.scope]
        if not any(p==s or (s.is_dir() and p.is_relative_to(s)) for s in scopes):
            raise ToolDenied(f"write target outside Mission scope: {rel}")
        p.parent.mkdir(parents=True,exist_ok=True); p.write_text(content,encoding='utf-8')
        return {"path":str(p.relative_to(self.root)),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size}

    def run_tests(self, order:MissionOrder):
        self._allowed(order,'test_run')
        cp=subprocess.run(['python','-m','unittest','discover','-s','tests','-v'],cwd=self.root,text=True,capture_output=True,timeout=90)
        return {"returncode":cp.returncode,"stdout":cp.stdout[-16000:],"stderr":cp.stderr[-16000:]}
