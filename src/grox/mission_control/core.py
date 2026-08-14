from __future__ import annotations

import re

from ..contracts import MissionMode, RiskClass

_RISK_RANK = {
    RiskClass.low: 0,
    RiskClass.medium: 1,
    RiskClass.high: 2,
    RiskClass.critical: 3,
}

_INSPECT_HINTS = {"inspect", "audit", "review", "analyze", "analyse"}
_REPAIR_HINTS = {"repair", "fix", "modify", "write", "change"}
_NEGATORS = {"not", "never", "without", "avoid", "avoiding", "forbid", "forbidden"}
_SENSITIVE_TARGETS = {"production", "credential", "credentials", "secret", "secrets"}
_CRITICAL_ACTIONS = {"delete", "destroy", "wipe", "rotate", "revoke", "replace", "overwrite", "expose"}
_HIGH_ACTIONS = {"deploy", "shell"}
_HIGH_CONTEXT = {"network", "external", "security", "permission"}
_MEDIUM_ACTIONS = {"write", "repair", "modify", "change", "install", "update", "fix"}


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9_]+", text.lower().replace("-", " ").replace("/", " "))


def _negated(tokens: list[str], index: int) -> bool:
    previous = tokens[max(0, index - 3):index]
    return bool(set(previous) & _NEGATORS) or (len(previous) >= 2 and previous[-2:] == ["do", "not"])


class MissionControl:
    """Advisory/policy subsystem. It never commands Crew directly."""

    def _deterministic_risk(self, directive: str) -> RiskClass:
        tokens = _tokens(directive)
        token_set = set(tokens)
        sensitive = bool(token_set & _SENSITIVE_TARGETS)

        if "irreversible" in token_set:
            return RiskClass.critical

        active_critical = {
            token for index, token in enumerate(tokens)
            if token in _CRITICAL_ACTIONS and not _negated(tokens, index)
        }
        if active_critical and (sensitive or active_critical & {"destroy", "wipe", "overwrite"}):
            return RiskClass.critical

        active_high = {
            token for index, token in enumerate(tokens)
            if token in _HIGH_ACTIONS and not _negated(tokens, index)
        }
        if sensitive or active_high or token_set & _HIGH_CONTEXT:
            return RiskClass.high

        active_medium = {
            token for index, token in enumerate(tokens)
            if token in _MEDIUM_ACTIONS and not _negated(tokens, index)
        }
        if active_medium:
            return RiskClass.medium

        return RiskClass.low

    def assess_risk(self, directive: str, explicit: RiskClass | None = None) -> RiskClass:
        """Return the effective risk floor; explicit input may raise but never lower it."""
        deterministic = self._deterministic_risk(directive)
        if explicit is None:
            return deterministic
        return explicit if _RISK_RANK[explicit] > _RISK_RANK[deterministic] else deterministic

    def suggests_repair(self, directive: str) -> bool:
        """Return an advisory repair hint without granting mutation authority."""
        return bool(set(_tokens(directive)) & _REPAIR_HINTS)

    def infer_mode(self, directive: str, explicit: MissionMode | None = None) -> MissionMode:
        """Infer only non-mutating modes; Repair requires an explicit authority path."""
        if explicit is not None:
            return explicit
        words = set(_tokens(directive))
        if words & _INSPECT_HINTS:
            return MissionMode.inspect
        return MissionMode.execute

    def verification_required(self, mode: MissionMode, risk: RiskClass) -> bool:
        return mode is MissionMode.repair or risk in {RiskClass.medium, RiskClass.high, RiskClass.critical}

    def default_actions(self, mode: MissionMode) -> list[str]:
        if mode is MissionMode.inspect:
            return ["fs_list", "fs_read", "test_run"]
        if mode is MissionMode.verify:
            return ["fs_list", "fs_read", "test_run"]
        if mode is MissionMode.repair:
            return ["fs_list", "fs_read", "fs_write", "test_run"]
        return ["fs_list", "fs_read"]
