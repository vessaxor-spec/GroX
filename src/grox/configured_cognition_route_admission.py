from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from .configured_cognition_fallback import (
    ConfiguredCognitionFallback,
    ConfiguredCognitionFallbackCandidate,
    ConfiguredCognitionFallbackPolicy,
    ConfiguredCognitionFallbackPolicyError,
)
from .configured_cognition_fitness import ConfiguredCognitionMissionFitness
from .configured_credential_use_authorization import (
    ConfiguredCredentialUseAuthorization,
    ConfiguredCredentialUseAuthorizationError,
)
from .configured_openai_cognition import ConfiguredOpenAICognition
from .tools.gateway import ToolDenied


class ConfiguredCognitionRouteAdmissionError(RuntimeError):
    """No safe current-gate route can be admitted from the explicit envelope."""

    def __init__(self, message: str, *, rejections: Mapping[str, str] | None = None):
        super().__init__(message)
        self.rejections = MappingProxyType(dict(rejections or {}))


@dataclass(frozen=True, slots=True)
class ConfiguredCognitionRouteAdmissionResult:
    """Volatile non-authoritative preflight over explicit cognition candidates."""

    candidate_order: tuple[str, ...]
    admitted_resource_ids: tuple[str, ...]
    rejected_reasons: Mapping[str, str]
    mission_id: str
    placement: str
    _admitted_candidates: tuple[ConfiguredCognitionFallbackCandidate, ...] = field(
        repr=False,
        compare=False,
    )

    @property
    def admitted_candidates(self) -> tuple[ConfiguredCognitionFallbackCandidate, ...]:
        """Return only the original independently governed candidates that passed preflight."""
        return self._admitted_candidates

    def evidence(self) -> dict[str, Any]:
        return {
            "schema": "grox-configured-cognition-route-admission-v1",
            "candidate_order": list(self.candidate_order),
            "admitted_resource_ids": list(self.admitted_resource_ids),
            "rejected_reasons": dict(self.rejected_reasons),
            "mission_id": self.mission_id,
            "placement": self.placement,
            "route_admitted": bool(self.admitted_resource_ids),
            "current_control_plane_revalidated": True,
            "provider_readiness_claim": False,
            "historical_success_used_as_current_readiness": False,
            "ready": False,
            "selected": False,
            "observed": False,
            "ranking_enabled": False,
            "learning_enabled": False,
            "adaptive_scoring_enabled": False,
            "candidate_expansion": False,
            "secret_materialized": False,
            "credential_inspected": False,
            "network_invoked": False,
            "provider_constructed": False,
            "cognition_invoked": False,
            "fallback_invoked": False,
            "mission_created": False,
            "authority_changed": False,
        }


class ConfiguredCognitionRouteAdmission:
    """Admit explicit configured-cognition candidates under current control-plane truth.

    This is deliberately not provider readiness and not selection. It reuses the
    existing exact configured credential-use authorization contract and the
    existing Tool Gateway action/URL gates without materializing a secret or
    performing network I/O. Supplied successful cognition and Mission-fit
    evidence are checked only for exact identity continuity; they are never
    promoted into a fresh provider-readiness claim.
    """

    def __init__(
        self,
        candidates: Sequence[ConfiguredCognitionFallbackCandidate],
        policy: ConfiguredCognitionFallbackPolicy,
    ):
        if not isinstance(policy, ConfiguredCognitionFallbackPolicy):
            raise TypeError("policy must be a ConfiguredCognitionFallbackPolicy")
        if not isinstance(candidates, Sequence) or isinstance(candidates, (str, bytes)):
            raise TypeError("candidates must be a sequence")
        frozen = tuple(candidates)
        if not all(isinstance(candidate, ConfiguredCognitionFallbackCandidate) for candidate in frozen):
            raise TypeError("every candidate must be a ConfiguredCognitionFallbackCandidate")

        # Reuse the already-qualified fallback envelope validator only for its
        # pure structural/identity checks. Construction performs no selection,
        # secret materialization, provider construction, network I/O or cognition.
        try:
            ConfiguredCognitionFallback(frozen, policy)
        except ConfiguredCognitionFallbackPolicyError as exc:
            raise ConfiguredCognitionRouteAdmissionError(
                "configured cognition route envelope is structurally unsafe"
            ) from exc

        by_id = {candidate.resource_id: candidate for candidate in frozen}
        self._candidates = MappingProxyType(by_id)
        self._policy = policy

    @staticmethod
    def _qualification_identity_exact(candidate: ConfiguredCognitionFallbackCandidate) -> bool:
        qualification = candidate.qualification
        fitness = candidate.fitness
        order = candidate.order
        parameters = order.parameters
        return (
            order.sealed
            and qualification.mission_id == order.mission_id
            and qualification.order_id == order.order_id
            and fitness.mission_id == order.mission_id
            and fitness.order_id == order.order_id
            and fitness.resource_id == qualification.resource_id
            and fitness.provider_kind == qualification.provider_kind == "openai"
            and fitness.model == qualification.model
            and fitness.endpoint == qualification.endpoint == ConfiguredOpenAICognition.official_responses_endpoint
            and fitness.credential_alias == qualification.credential_alias
            and fitness.placement == ConfiguredCognitionMissionFitness.placement
            and fitness.qualified_fit
            and parameters.get("operation") == ConfiguredOpenAICognition.operation
            and parameters.get("resource_id") == qualification.resource_id
            and parameters.get("provider_kind") == qualification.provider_kind
            and parameters.get("model") == qualification.model
            and parameters.get("endpoint") == qualification.endpoint
            and parameters.get("credential_alias") == qualification.credential_alias
        )

    @staticmethod
    def _authorization_item_exact(
        candidate: ConfiguredCognitionFallbackCandidate,
        item: Mapping[str, Any],
    ) -> bool:
        qualification = candidate.qualification
        return (
            item.get("resource_id") == qualification.resource_id
            and item.get("provider_kind") == qualification.provider_kind
            and item.get("model") == qualification.model
            and item.get("endpoint") == qualification.endpoint
            and item.get("credential_alias") == qualification.credential_alias
        )

    def _current_rejection_reason(
        self,
        candidate: ConfiguredCognitionFallbackCandidate,
    ) -> str | None:
        if not self._qualification_identity_exact(candidate):
            return "qualification_identity_mismatch"

        try:
            authorization = ConfiguredCredentialUseAuthorization(
                candidate.config,
                candidate.gateway,
            ).inventory(
                order=candidate.order,
                expected_operation=ConfiguredOpenAICognition.operation,
            )
        except ConfiguredCredentialUseAuthorizationError:
            return "credential_authorization_context_invalid"

        resources = authorization.get("resources") or []
        if authorization.get("status") != "ok" or len(resources) != 1:
            return "current_config_binding_unavailable"
        item = resources[0]
        if not self._authorization_item_exact(candidate, item):
            return "current_config_identity_changed"
        if item.get("credential_alias_available") is not True:
            return "credential_alias_unavailable"
        if item.get("credential_use_authorized") is not True:
            return "credential_use_not_authorized"

        gateway = candidate.gateway
        order = candidate.order
        try:
            gateway._allowed(order, "cognition_invoke")
        except (ToolDenied, TypeError, ValueError):
            return "cognition_invoke_not_authorized"
        try:
            gateway._allowed(order, "net_fetch")
        except (ToolDenied, TypeError, ValueError):
            return "network_not_authorized"
        if not gateway.policy.network_enabled:
            return "network_disabled_by_host_policy"
        try:
            origin, parsed = gateway._assert_url(order, candidate.qualification.endpoint)
        except (ToolDenied, TypeError, ValueError):
            return "endpoint_scope_not_authorized"
        if (
            origin != "https://api.openai.com"
            or parsed.path != "/v1/responses"
            or parsed.query
            or parsed.fragment
        ):
            return "endpoint_identity_mismatch"
        return None

    def plan(self) -> ConfiguredCognitionRouteAdmissionResult:
        admitted: list[ConfiguredCognitionFallbackCandidate] = []
        rejected: dict[str, str] = {}
        for resource_id in self._policy.candidate_order:
            candidate = self._candidates[resource_id]
            reason = self._current_rejection_reason(candidate)
            if reason is None:
                admitted.append(candidate)
            else:
                rejected[resource_id] = reason

        if not admitted:
            raise ConfiguredCognitionRouteAdmissionError(
                "no explicit configured cognition candidate passes current route-admission gates",
                rejections=rejected,
            )

        mission_id = admitted[0].order.mission_id
        admitted_ids = tuple(candidate.resource_id for candidate in admitted)
        return ConfiguredCognitionRouteAdmissionResult(
            candidate_order=self._policy.candidate_order,
            admitted_resource_ids=admitted_ids,
            rejected_reasons=MappingProxyType(dict(rejected)),
            mission_id=mission_id,
            placement=ConfiguredCognitionMissionFitness.placement,
            _admitted_candidates=tuple(admitted),
        )
