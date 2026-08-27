from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from .configured_openai_cognition import (
    ConfiguredOpenAICognition,
    ConfiguredOpenAICognitionResult,
)
from .contracts import MissionOrder


class ConfiguredCognitionFitnessError(RuntimeError):
    """Configured cognition fitness could not be evaluated safely."""


@dataclass(frozen=True, slots=True)
class ConfiguredCognitionFitnessResult:
    """Deterministic fitness evidence for one bounded cognition placement."""

    status: str
    resource_id: str
    provider_kind: str
    model: str
    endpoint: str
    credential_alias: str
    mission_id: str
    order_id: str
    placement: str
    checks: Mapping[str, bool]

    @property
    def qualified_fit(self) -> bool:
        return self.status == "PASS" and all(self.checks.values())

    def evidence(self) -> dict[str, Any]:
        return {
            "schema": "grox-configured-cognition-fitness-v1",
            "status": self.status,
            "resource_id": self.resource_id,
            "provider_kind": self.provider_kind,
            "model": self.model,
            "endpoint": self.endpoint,
            "credential_alias": self.credential_alias,
            "mission_id": self.mission_id,
            "order_id": self.order_id,
            "placement": self.placement,
            "checks": dict(self.checks),
            "qualified_fit": self.qualified_fit,
            "fitness_scope": "mission_interpretation_only",
            "general_model_quality_claim": False,
            "crew_cognition_fit_claim": False,
            "routing_fit_claim": False,
            "fallback_fit_claim": False,
            "cognition_invoked": False,
            "secret_materialized": False,
            "network_invoked": False,
            "selected": False,
            "observed": False,
            "mission_created": False,
            "authority_changed": False,
            "auto_selection": False,
        }


class ConfiguredCognitionMissionFitness:
    """Qualify one successful configured cognition result for Mission interpretation.

    The evaluator is deliberately pure: it performs no network I/O, secret access,
    provider invocation, selection, observation, or Mission creation. PASS means
    only that the exact successful configured cognition result satisfies GroX's
    deterministic contract for the `mission_interpretation` placement.
    """

    placement = "mission_interpretation"
    max_roster_entries = 200
    max_options = 16
    max_option_name_chars = 160
    max_option_rationale_chars = 4_000
    max_objective_chars = 20_000

    @classmethod
    def evaluate(
        cls,
        result: ConfiguredOpenAICognitionResult,
        *,
        order: MissionOrder,
        roster: list[dict[str, Any]],
    ) -> ConfiguredCognitionFitnessResult:
        if not isinstance(result, ConfiguredOpenAICognitionResult):
            raise TypeError("result must be a ConfiguredOpenAICognitionResult")
        if not isinstance(order, MissionOrder):
            raise TypeError("order must be a MissionOrder")
        if not order.sealed:
            raise ConfiguredCognitionFitnessError(
                "configured cognition fitness requires the already sealed source Mission Order"
            )
        if not isinstance(roster, list) or len(roster) > cls.max_roster_entries:
            raise ConfiguredCognitionFitnessError("configured cognition fitness requires a bounded roster")

        roster_ids: set[str] = set()
        for row in roster:
            if not isinstance(row, Mapping):
                raise ConfiguredCognitionFitnessError("roster entries must be mappings")
            crew_id = row.get("crew_id")
            if not isinstance(crew_id, str) or not crew_id.strip():
                raise ConfiguredCognitionFitnessError("every roster entry requires a non-empty crew_id")
            crew_id = crew_id.strip()
            if crew_id in roster_ids:
                raise ConfiguredCognitionFitnessError(f"duplicate roster crew_id: {crew_id}")
            roster_ids.add(crew_id)

        interpretation = result.interpretation
        source_evidence = result.evidence()
        parameters = order.parameters
        option_names = [option.name for option in interpretation.options]
        candidate_ids = list(interpretation.candidate_crew_ids)
        option_crew_ids = [crew_id for option in interpretation.options for crew_id in option.crew_ids]

        exact_order_identity = (
            result.mission_id == order.mission_id
            and result.order_id == order.order_id
            and parameters.get("operation") == ConfiguredOpenAICognition.operation
            and parameters.get("resource_id") == result.resource_id
            and parameters.get("provider_kind") == result.provider_kind
            and parameters.get("model") == result.model
            and parameters.get("endpoint") == result.endpoint
            and parameters.get("credential_alias") == result.credential_alias
        )
        roster_constrained = all(
            crew_id in roster_ids for crew_id in candidate_ids + option_crew_ids
        )
        bounded_strategy = (
            1 <= len(interpretation.options) <= cls.max_options
            and len(option_names) == len(set(option_names))
            and all(
                isinstance(option.name, str)
                and bool(option.name.strip())
                and len(option.name) <= cls.max_option_name_chars
                and isinstance(option.rationale, str)
                and bool(option.rationale.strip())
                and len(option.rationale) <= cls.max_option_rationale_chars
                and len(option.crew_ids) <= cls.max_roster_entries
                and len(option.crew_ids) == len(set(option.crew_ids))
                for option in interpretation.options
            )
            and len(candidate_ids) <= cls.max_roster_entries
            and len(candidate_ids) == len(set(candidate_ids))
        )
        recommendation_valid = (
            bool(interpretation.recommended_option)
            and interpretation.recommended_option in set(option_names)
        )
        source_state_separation = (
            source_evidence.get("cognition_succeeded") is True
            and source_evidence.get("ready") is True
            and source_evidence.get("qualified_fit") is False
            and source_evidence.get("selected") is False
            and source_evidence.get("observed") is False
            and source_evidence.get("authority_changed") is False
            and source_evidence.get("raw_response_returned") is False
        )
        checks = {
            "exact_order_identity": exact_order_identity,
            "official_openai_identity": (
                result.provider_kind == "openai"
                and result.endpoint == ConfiguredOpenAICognition.official_responses_endpoint
            ),
            "commander_intent_exact": interpretation.commander_intent == order.commander_intent,
            "response_model_consistent": (
                result.response_model is None or result.response_model == result.model
            ),
            "objective_bounded": (
                isinstance(interpretation.objective, str)
                and bool(interpretation.objective.strip())
                and len(interpretation.objective) <= cls.max_objective_chars
            ),
            "strategy_bounded": bounded_strategy,
            "recommendation_valid": recommendation_valid,
            "crew_references_roster_constrained": roster_constrained,
            "source_cognition_state_separated": source_state_separation,
        }
        frozen_checks = MappingProxyType(dict(checks))
        passed = all(frozen_checks.values())
        return ConfiguredCognitionFitnessResult(
            status="PASS" if passed else "FAIL",
            resource_id=result.resource_id,
            provider_kind=result.provider_kind,
            model=result.model,
            endpoint=result.endpoint,
            credential_alias=result.credential_alias,
            mission_id=result.mission_id,
            order_id=result.order_id,
            placement=cls.placement,
            checks=frozen_checks,
        )
