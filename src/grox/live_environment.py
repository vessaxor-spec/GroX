from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable, Mapping

from .native_model_runtime import LocalModelRuntime, ModelReadiness


class ResourcePolicyError(ValueError):
    """A live-resource policy is malformed or ambiguous."""


class ResourceSelectionError(RuntimeError):
    """No currently observable resource satisfies the bounded policy gates."""


class ResourceObservationError(RuntimeError):
    """An executed resource could not be durably recorded as observed."""


def _normalized_ids(values: frozenset[str], *, label: str) -> frozenset[str]:
    normalized: set[str] = set()
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ResourcePolicyError(f"{label} entries must be non-empty strings")
        normalized.add(value.strip())
    return frozenset(normalized)


@dataclass(frozen=True, slots=True)
class ResourcePolicy:
    """Explicit non-authoritative policy inputs for one bounded selection.

    Authorization and qualification are deliberately supplied separately from
    discovery/readiness. Registry membership, connectivity, and capability do
    not add entries to either set. Candidate order is the complete fallback
    envelope: resources outside it are never silently considered.
    """

    authorized_ids: frozenset[str]
    qualified_ids: frozenset[str]
    candidate_order: tuple[str, ...]

    def __post_init__(self) -> None:
        authorized = _normalized_ids(self.authorized_ids, label="authorized_ids")
        qualified = _normalized_ids(self.qualified_ids, label="qualified_ids")
        candidates: list[str] = []
        seen: set[str] = set()
        for value in self.candidate_order:
            if not isinstance(value, str) or not value.strip():
                raise ResourcePolicyError("candidate_order entries must be non-empty strings")
            resource_id = value.strip()
            if resource_id in seen:
                raise ResourcePolicyError(f"candidate_order contains duplicate resource: {resource_id}")
            seen.add(resource_id)
            candidates.append(resource_id)
        if not candidates:
            raise ResourcePolicyError("candidate_order must explicitly contain at least one resource")
        object.__setattr__(self, "authorized_ids", authorized)
        object.__setattr__(self, "qualified_ids", qualified)
        object.__setattr__(self, "candidate_order", tuple(candidates))


@dataclass(frozen=True, slots=True)
class LiveResourceSnapshot:
    resource_id: str
    resource_kind: str
    placement: str
    discovered: bool
    authorized: bool
    ready: bool
    qualified_fit: bool
    selected: bool
    observed: bool
    readiness_status: str
    readiness_reason: str
    backend: str | None
    artifact_sha256: str | None
    active: bool
    hardware: Mapping[str, Any]
    observed_identity: Mapping[str, Any] | None = None

    @property
    def selectable(self) -> bool:
        return self.discovered and self.authorized and self.ready and self.qualified_fit

    def to_dict(self) -> dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "resource_kind": self.resource_kind,
            "placement": self.placement,
            "discovered": self.discovered,
            "authorized": self.authorized,
            "ready": self.ready,
            "qualified_fit": self.qualified_fit,
            "selected": self.selected,
            "observed": self.observed,
            "selectable": self.selectable,
            "readiness_status": self.readiness_status,
            "readiness_reason": self.readiness_reason,
            "backend": self.backend,
            "artifact_sha256": self.artifact_sha256,
            "active": self.active,
            "hardware": dict(self.hardware),
            "observed_identity": dict(self.observed_identity) if self.observed_identity is not None else None,
        }


@dataclass(frozen=True, slots=True)
class LiveResourceInventory:
    resources: tuple[LiveResourceSnapshot, ...]
    placement: str
    authority_changed: bool = False
    auto_activation: bool = False

    schema = "grox-live-environment-inventory-v1"

    def get(self, resource_id: str) -> LiveResourceSnapshot:
        for resource in self.resources:
            if resource.resource_id == resource_id:
                return resource
        raise KeyError(resource_id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "placement": self.placement,
            "resources": [resource.to_dict() for resource in self.resources],
            "authority_changed": self.authority_changed,
            "auto_activation": self.auto_activation,
        }


class LiveEnvironmentAwareness:
    """Fresh, bounded awareness over GroX's existing local model runtime.

    This first slice is intentionally local-model only. It does not discover
    arbitrary host resources, grant authority, qualify models, load models, or
    replace Pilot routing. Selection is volatile and constrained to the exact
    ResourcePolicy supplied by the caller.
    """

    resource_kind = "local_cognition_model"

    def __init__(
        self,
        runtime: LocalModelRuntime,
        *,
        observation_recorder: Callable[..., Any] | None = None,
    ):
        if not isinstance(runtime, LocalModelRuntime):
            raise TypeError("runtime must be a LocalModelRuntime")
        if observation_recorder is not None and not callable(observation_recorder):
            raise TypeError("observation_recorder must be callable or null")
        self.runtime = runtime
        self._observation_recorder = observation_recorder
        self._selected: dict[str, str] = {}
        self._observed: dict[tuple[str, str], dict[str, Any]] = {}

    @staticmethod
    def _artifact_is_present(path: str | None) -> bool:
        if not path:
            return False
        try:
            return Path(path).is_file()
        except OSError:
            return False

    def _snapshot(
        self,
        model_id: str,
        policy: ResourcePolicy,
        *,
        placement: str,
    ) -> LiveResourceSnapshot:
        manifest = self.runtime.registry.get(model_id)
        readiness = self.runtime.readiness(model_id)
        discovered = self._artifact_is_present(readiness.artifact_path) or model_id in self.runtime.active_models()
        authorized = model_id in policy.authorized_ids
        ready = readiness.status is ModelReadiness.AVAILABLE
        qualified_fit = model_id in policy.qualified_ids and placement in manifest.placements
        selected = self._selected.get(placement) == model_id and discovered and authorized and ready and qualified_fit
        observed_identity = self._observed.get((placement, model_id))
        return LiveResourceSnapshot(
            resource_id=model_id,
            resource_kind=self.resource_kind,
            placement=placement,
            discovered=discovered,
            authorized=authorized,
            ready=ready,
            qualified_fit=qualified_fit,
            selected=selected,
            observed=observed_identity is not None,
            readiness_status=readiness.status.value,
            readiness_reason=readiness.reason,
            backend=readiness.backend,
            artifact_sha256=readiness.artifact_sha256,
            active=readiness.active,
            hardware=readiness.hardware.to_dict(),
            observed_identity=dict(observed_identity) if observed_identity is not None else None,
        )

    def inventory(self, policy: ResourcePolicy, *, placement: str) -> LiveResourceInventory:
        """Rediscover current local-model state without activating anything."""
        if not isinstance(policy, ResourcePolicy):
            raise TypeError("policy must be a ResourcePolicy")
        if not isinstance(placement, str) or not placement.strip():
            raise ValueError("placement must be a non-empty string")
        normalized_placement = placement.strip()
        resources = tuple(
            self._snapshot(model_id, policy, placement=normalized_placement)
            for model_id in self.runtime.registry.ids()
        )
        return LiveResourceInventory(resources=resources, placement=normalized_placement)

    def select(self, policy: ResourcePolicy, *, placement: str) -> LiveResourceSnapshot:
        """Select the first fully gated resource in the explicit fallback order.

        Selection is a volatile Pilot-side decision only. It never loads or
        activates the model and never changes Commander or Mission authority.
        """
        inventory = self.inventory(policy, placement=placement)
        by_id = {resource.resource_id: resource for resource in inventory.resources}
        self._selected.pop(inventory.placement, None)
        blockers: list[str] = []
        for resource_id in policy.candidate_order:
            resource = by_id.get(resource_id)
            if resource is None:
                blockers.append(f"{resource_id}: not represented in the local model registry")
                continue
            missing: list[str] = []
            if not resource.discovered:
                missing.append("not_discovered")
            if not resource.authorized:
                missing.append("not_authorized")
            if not resource.ready:
                missing.append("not_ready")
            if not resource.qualified_fit:
                missing.append("not_qualified_fit")
            if missing:
                blockers.append(f"{resource_id}: {','.join(missing)}")
                continue
            self._selected[inventory.placement] = resource_id
            return replace(resource, selected=True)
        detail = "; ".join(blockers[:8]) or "no candidates supplied"
        raise ResourceSelectionError(f"no policy-eligible live resource for {inventory.placement}: {detail}")

    def invoke_selected(
        self,
        selection: LiveResourceSnapshot,
        policy: ResourcePolicy,
        *,
        payload: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Invoke an already explicitly loaded selected resource and observe it.

        The existing LocalModelRuntime remains the load/invocation authority.
        This method revalidates current gates immediately before invocation and
        records only identity/configuration that the runtime actually exposes.
        """
        if not isinstance(selection, LiveResourceSnapshot):
            raise TypeError("selection must be a LiveResourceSnapshot")
        if not isinstance(payload, Mapping):
            raise TypeError("payload must be a mapping")
        current = self.inventory(policy, placement=selection.placement).get(selection.resource_id)
        if self._selected.get(selection.placement) != selection.resource_id or not current.selectable:
            self._selected.pop(selection.placement, None)
            raise ResourceSelectionError(
                f"selected resource is no longer policy-eligible: {selection.resource_id}"
            )
        invocation = self.runtime.invoke(
            selection.resource_id,
            placement=selection.placement,
            payload=payload,
        )
        if invocation.get("model_id") != selection.resource_id:
            raise ResourceSelectionError("runtime invocation returned a different model identity")
        if invocation.get("placement") != selection.placement:
            raise ResourceSelectionError("runtime invocation returned a different placement")
        if invocation.get("authority_changed") is not False:
            raise ResourceSelectionError("runtime invocation reported an authority change")

        identity: dict[str, Any] = {}
        for field in (
            "model_id",
            "model_kind",
            "backend",
            "placement",
            "artifact_sha256",
            "authority_changed",
        ):
            if field in invocation:
                identity[field] = invocation[field]
        identity["hardware"] = self.runtime.hardware.to_dict()
        if self._observation_recorder is not None:
            try:
                self._observation_recorder(
                    resource_id=selection.resource_id,
                    resource_kind=self.resource_kind,
                    placement=selection.placement,
                    identity=dict(identity),
                )
            except Exception as exc:
                raise ResourceObservationError(
                    f"observation persistence failed for {selection.resource_id}: "
                    f"{type(exc).__name__}: {exc}"
                ) from exc
        self._observed[(selection.placement, selection.resource_id)] = dict(identity)
        return {
            "schema": "grox-live-resource-execution-v1",
            "resource_id": selection.resource_id,
            "resource_kind": self.resource_kind,
            "execution_identity": identity,
            "output": dict(invocation.get("output") or {}),
            "authority_changed": False,
        }

    def reconstitute(self, policy: ResourcePolicy, *, placement: str) -> dict[str, Any]:
        """Clear volatile awareness and rediscover current runtime truth."""
        runtime_report = self.runtime.reconstitute()
        self._selected.clear()
        self._observed.clear()
        refreshed = self.inventory(policy, placement=placement)
        return {
            "schema": "grox-live-environment-reconstitution-v1",
            "runtime": runtime_report,
            "inventory": refreshed,
            "auto_activation": False,
            "authority_changed": False,
        }
