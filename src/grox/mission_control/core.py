from __future__ import annotations
from ..contracts import RiskClass, MissionMode

RISK_WORDS={
 RiskClass.critical:{'production','credential','credentials','secret','secrets','irreversible','destroy','wipe'},
 RiskClass.high:{'delete','deploy','network','external','shell','security','permission'},
 RiskClass.medium:{'write','repair','modify','change','install','update'},
}

class MissionControl:
    """Advisory/policy subsystem. It never commands Crew directly."""
    def assess_risk(self, directive:str, explicit:RiskClass|None=None)->RiskClass:
        if explicit: return explicit
        words=set(directive.lower().replace('/',' ').replace('-',' ').split())
        for level in (RiskClass.critical,RiskClass.high,RiskClass.medium):
            if words & RISK_WORDS[level]: return level
        return RiskClass.low

    def infer_mode(self, directive:str, explicit:MissionMode|None=None)->MissionMode:
        if explicit: return explicit
        d=directive.lower()
        if any(w in d for w in ('inspect','audit','review','analyze','analyse')): return MissionMode.inspect
        if any(w in d for w in ('repair','fix','modify','write','change')): return MissionMode.repair
        return MissionMode.execute

    def verification_required(self, mode:MissionMode, risk:RiskClass)->bool:
        return mode is MissionMode.repair or risk in {RiskClass.medium,RiskClass.high,RiskClass.critical}

    def default_actions(self, mode:MissionMode)->list[str]:
        if mode is MissionMode.inspect: return ['fs_list','fs_read','test_run']
        if mode is MissionMode.verify: return ['fs_list','fs_read','test_run']
        if mode is MissionMode.repair: return ['fs_list','fs_read','fs_write','test_run']
        return ['fs_list','fs_read']
