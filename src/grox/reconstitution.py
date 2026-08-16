from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

from .health import FAIL, PASS, UNKNOWN, WARN, HealthReport


FAST = "fast"
TARGETED = "targeted"
FULL = "full"

FULL_SURFACES: tuple[str, ...] = (
    "command_doctrine",
    "source_integrity",
    "operational_state",
    "persistence_binding",
    "authority_policy",
    "memory_state",
    "verification_boundary",
    "environment_capabilities",
    "mission_recovery",
    "cognitive_context",
)

MANDATORY_SURFACES: tuple[str, ...] = (
    "command_doctrine",
    "source_integrity",
    "authority_policy",
    "cognitive_context",
)

DOMAIN_SURFACE = {
    "command": "command_doctrine",
    "operations": "operational_state",
    "persistence": "persistence_binding",
    "authority": "authority_policy",
    "memory": "memory_state",
    "source": "source_integrity",
    "verification": "verification_boundary",
    "environment": "environment_capabilities",
    "recovery": "mission_recovery",
}


@dataclass(frozen=True, slots=True)
class ReconstitutionPlan:
    mode: str
    reasons: tuple[str, ...]
    load_surfaces: tuple[str, ...]
    generated_from_health: str
    full_surface_count: int = len(FULL_SURFACES)

    @property
    def planned_surface_count(self) -> int:
        return len(self.load_surfaces)

    @property
    def avoided_surface_count(self) -> int:
        return max(0, self.full_surface_count - self.planned_surface_count)

    @property
    def structural_reduction_ratio(self) -> float:
        if not self.full_surface_count:
            return 0.0
        return round(self.avoided_surface_count / self.full_surface_count, 4)

    def to_dict(self) -> dict:
        data = asdict(self)
        data.update(
            planned_surface_count=self.planned_surface_count,
            avoided_surface_count=self.avoided_surface_count,
            structural_reduction_ratio=self.structural_reduction_ratio,
        )
        return data


class ReconstitutionPlanner:
    """Choose evidence-loading scope without changing recovery semantics.

    This planner is advisory/read-only. It consumes a live VesselHealth report
    and explicit host/source facts. FULL is the fail-closed default whenever
    mandatory evidence is missing, unsafe, or ambiguous. FAST and TARGETED only
    reduce which context/evidence surfaces must be loaded after the underlying
    health checks have already passed their own authority/integrity boundaries.
    """

    def plan(
        self,
        health: HealthReport,
        *,
        fresh_host: bool = False,
        source_changed: bool = False,
    ) -> ReconstitutionPlan:
        checks = {check.check_id: check for check in health.checks}
        full_reasons: list[str] = []

        if fresh_host:
            full_reasons.append("fresh host requires full source/state and recovery reconstitution")
        if source_changed:
            full_reasons.append("source changed since prior operating context")

        critical_failures = sorted(
            check.check_id for check in health.checks if check.critical and check.status == FAIL
        )
        if critical_failures:
            full_reasons.append(f"critical health failure(s): {', '.join(critical_failures)}")

        recovery = checks.get("recovery_readiness")
        if recovery is None or recovery.status != PASS:
            full_reasons.append(
                "recovery readiness is not positively PASS"
                if recovery is None
                else f"recovery readiness is {recovery.status}"
            )

        operational = checks.get("operational_state")
        inflight = self._inflight_count(operational.evidence if operational else None)
        if inflight:
            full_reasons.append(f"{inflight} active/interrupted/unresolved Mission or graph record(s) require full recovery")

        source_repo = checks.get("source_repository")
        if source_repo and source_repo.status == WARN:
            full_reasons.append("source repository is dirty or otherwise degraded")

        persistence = checks.get("persistence_readiness")
        if persistence and persistence.status in {FAIL, WARN}:
            full_reasons.append(f"persistence readiness is {persistence.status}")

        mandatory_ids = (
            "command_integrity",
            "operational_state",
            "authority_integrity",
            "memory_integrity",
            "source_version",
            "verification_readiness",
        )
        not_positive = [
            check_id
            for check_id in mandatory_ids
            if checks.get(check_id) is None or checks[check_id].status != PASS
        ]
        if not_positive:
            full_reasons.append(f"mandatory health evidence not positively PASS: {', '.join(not_positive)}")

        if full_reasons:
            return ReconstitutionPlan(
                FULL,
                tuple(dict.fromkeys(full_reasons)),
                FULL_SURFACES,
                health.generated_at,
            )

        targeted_checks = [
            check
            for check in health.checks
            if check.status in {WARN, UNKNOWN} and check.check_id not in {"recovery_readiness"}
        ]
        if targeted_checks:
            surfaces = self._ordered_surfaces(
                (*MANDATORY_SURFACES, *(DOMAIN_SURFACE.get(check.domain, "cognitive_context") for check in targeted_checks))
            )
            reasons = tuple(
                f"{check.check_id} is {check.status}: {check.detail}" for check in targeted_checks
            )
            return ReconstitutionPlan(TARGETED, reasons, surfaces, health.generated_at)

        # FAST requires positive source-repository evidence as well. A missing or
        # UNKNOWN Git/source binding is not equivalent to a current binding.
        if source_repo is None or source_repo.status != PASS:
            detail = "source repository evidence missing" if source_repo is None else f"source repository is {source_repo.status}"
            surfaces = self._ordered_surfaces((*MANDATORY_SURFACES, "source_integrity"))
            return ReconstitutionPlan(TARGETED, (detail,), surfaces, health.generated_at)

        return ReconstitutionPlan(
            FAST,
            ("all mandatory health evidence is positively PASS and no unsafe in-flight state is present",),
            MANDATORY_SURFACES,
            health.generated_at,
        )

    @staticmethod
    def _ordered_surfaces(surfaces: Iterable[str]) -> tuple[str, ...]:
        requested = set(surfaces)
        return tuple(surface for surface in FULL_SURFACES if surface in requested)

    @staticmethod
    def _inflight_count(evidence: dict | None) -> int:
        if not isinstance(evidence, dict):
            return 0
        mission_status = evidence.get("mission_status") or {}
        graph_status = evidence.get("graph_node_status") or {}
        mission_active = sum(
            int(mission_status.get(status, 0) or 0)
            for status in ("running", "interrupted", "needs_pilot_decision")
        )
        graph_active = sum(
            int(graph_status.get(status, 0) or 0)
            for status in ("running", "interrupted")
        )
        return mission_active + graph_active
