from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json, re
from typing import Iterable
from ..state import StateStore

FORBIDDEN_IDS={"gorxu","pilot","mission-control","mission_control","orchestrator","agents-orchestrator"}

@dataclass(frozen=True, slots=True)
class CrewDossier:
    crew_id:str
    division:str
    title:str
    capabilities:frozenset[str]
    tags:frozenset[str]
    verification:bool=False

class CrewRoster:
    def __init__(self, dossier_dir: Path, store: StateStore | None = None):
        self.store=store; self._crew={}
        for p in sorted(dossier_dir.glob('*.json')):
            raw=json.loads(p.read_text())
            cid=raw['crew_id']
            if cid in FORBIDDEN_IDS: raise ValueError(f"forbidden Crew id: {cid}")
            d=CrewDossier(cid,raw['division'],raw['title'],frozenset(raw['capabilities']),frozenset(raw.get('tags',[])),bool(raw.get('verification')))
            self._crew[cid]=d
            if store is not None:
                store.ensure_crew(cid)

    def get(self, crew_id:str)->CrewDossier:
        return self._crew[crew_id]

    def all(self)->list[CrewDossier]: return list(self._crew.values())

    def select(self, objective:str, required:Iterable[str]=(), exclude:Iterable[str]=(), verifier:bool=False)->CrewDossier:
        required=set(required); excluded=set(exclude); words=set(re.findall(r"[a-z0-9_-]+", objective.lower()))
        candidates=[]
        for d in self._crew.values():
            if d.crew_id in excluded: continue
            if verifier and not d.verification: continue
            if required and not required.issubset(d.capabilities): continue
            score=len(words & d.tags)*4 + len(required & d.capabilities)*3
            candidates.append((score,len(d.capabilities),d.crew_id,d))
        if not candidates:
            raise LookupError(f"No standing Crew covers required capabilities: {sorted(required)}")
        candidates.sort(key=lambda x:(-x[0],-x[1],x[2]))
        return candidates[0][3]
