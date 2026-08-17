from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json, re
from typing import Iterable
from ..state import StateStore

FORBIDDEN_IDS={"gorxu","pilot","mission-control","mission_control","orchestrator","agents-orchestrator"}


def _forbidden_command_identity(crew_id: str, title: str) -> bool:
    cid = crew_id.strip().lower()
    normalized_title = re.sub(r"[\s_]+", "-", title.strip().lower())
    if cid in FORBIDDEN_IDS or normalized_title in FORBIDDEN_IDS:
        return True
    # GorXu is the sole operational orchestrator. Reject semantic variants such
    # as stale-orchestrator, backup-orchestrator, or a hidden Orchestrator title.
    return "orchestrator" in cid or "orchestrator" in normalized_title


def _purge_stale_operational_crew(store: StateStore, active_ids: set[str]) -> None:
    if not active_ids:
        return
    rows = store.db.execute("SELECT crew_id FROM crew_state").fetchall()
    stale_ids = sorted({str(row["crew_id"]) for row in rows} - active_ids)
    if not stale_ids:
        return
    placeholders = ",".join("?" for _ in stale_ids)
    # Purge operational identity, memory, and adaptive telemetry. Historical
    # Mission/Order/Evidence rows remain as audit evidence and cannot route Crew.
    store.db.execute(f"DELETE FROM crew_state WHERE crew_id IN ({placeholders})", stale_ids)
    store.db.execute(
        f"DELETE FROM memories WHERE scope='crew' AND crew_id IN ({placeholders})",
        stale_ids,
    )
    store.db.execute(f"DELETE FROM crew_performance WHERE crew_id IN ({placeholders})", stale_ids)
    store.db.commit()


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
        dossier_dir=Path(dossier_dir)
        self.store=store; self._crew={}; self._domains={}
        self._dossier_dir=dossier_dir
        self._specialist_dir=dossier_dir.parent/'specialists'
        for p in sorted(dossier_dir.glob('*.json')):
            raw=json.loads(p.read_text())
            cid=raw['crew_id']
            title=raw['title']
            status=str(raw.get('status', 'standing')).strip().lower()
            if status != 'standing':
                raise ValueError(f"non-standing Crew dossier is not allowed in the active roster: {cid} ({status})")
            if _forbidden_command_identity(cid, title):
                raise ValueError(f"forbidden Crew command identity: {cid} / {title}")
            d=CrewDossier(cid,raw['division'],title,frozenset(raw['capabilities']),frozenset(raw.get('tags',[])),bool(raw.get('verification')))
            self._crew[cid]=d
            # Domains are descriptive cognitive-discovery metadata only. They are
            # never eligibility, capability, Mission authority, or Repair grants.
            domains=raw.get('domains') or raw.get('skills') or raw.get('tags',[])
            self._domains[cid]=tuple(str(value).strip() for value in domains if str(value).strip())
        if store is not None:
            for cid in sorted(self._crew):
                store.ensure_crew(cid)
            _purge_stale_operational_crew(store, set(self._crew))

    def get(self, crew_id:str)->CrewDossier:
        return self._crew[crew_id]

    def cognitive_directory(self)->list[dict[str, object]]:
        """Return a compact 82-Crew discovery surface for GorXu cognition.

        The directory intentionally omits capabilities and expanded routing tags.
        Those remain local deterministic eligibility/routing inputs. Descriptive
        domains can help cognition recommend a Crew ID but can never grant authority.
        """
        return [
            {
                'crew_id':d.crew_id,
                'division':d.division,
                'title':d.title,
                'domains':list(self._domains.get(d.crew_id,())),
                'verification':d.verification,
            }
            for d in sorted(self._crew.values(),key=lambda crew:crew.crew_id)
        ]

    def craft_card(self, crew_id:str)->str:
        """Return canonical craft depth for an active Standing Crew identity.

        The dossier remains the machine-readable eligibility/capability source.
        Reading craft never grants capabilities, Mission authority, or Repair permission.
        """
        self.get(crew_id)
        path=self._specialist_dir/f"{crew_id}.md"
        if not path.is_file():
            raise LookupError(f"No specialist craft card for active Crew {crew_id}")
        return path.read_text(encoding='utf-8')

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
