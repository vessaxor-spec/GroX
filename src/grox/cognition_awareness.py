from __future__ import annotations

from collections.abc import Callable, MutableMapping
from dataclasses import dataclass
import hashlib
import re
from time import monotonic
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from .contracts import MissionOrder
from .native_model_runtime import LocalModelRuntime
from .openai_crew_cognition import OpenAICrewCognitionProvider
from .reasoning.openai_responses import OpenAIResponsesProvider
from .reasoning.session import SessionReasoningProvider
from .session_crew_cognition import SessionCrewCognitionProvider
from .tools.gateway import ToolDenied, ToolGateway
from .tools.policy import PolicyError, normalize_origin


_HOSTED_TYPES = (
    SessionReasoningProvider,
    SessionCrewCognitionProvider,
    OpenAIResponsesProvider,
    OpenAICrewCognitionProvider,
)
_REMOTE_TYPES = (OpenAIResponsesProvider, OpenAICrewCognitionProvider)
_SESSION_TYPES = (SessionReasoningProvider, SessionCrewCognitionProvider)


class CognitionTransportAuthorizationError(PermissionError):
    """The bounded cognition transport probe lacks exact sealed authority."""


def _validate_ids(values: frozenset[str], *, field: str) -> frozenset[str]:
    normalized: set[str] = set()
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must contain only non-empty resource IDs")
        normalized.add(value.strip())
    return frozenset(normalized)


@dataclass(frozen=True, slots=True)
class CognitionProviderPolicy:
    """Explicit awareness policy for exact hosted cognition resource identities.

    Policy records never discover, bind, ready, qualify, or invoke a provider.
    Authorization and qualification remain independent inputs.
    """

    authorized_ids: frozenset[str] = frozenset()
    qualified_ids: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        object.__setattr__(self, "authorized_ids", _validate_ids(self.authorized_ids, field="authorized_ids"))
        object.__setattr__(self, "qualified_ids", _validate_ids(self.qualified_ids, field="qualified_ids"))


def _safe_identity(value: Any, *, fallback: str) -> str:
    if not isinstance(value, str):
        return fallback
    value = value.strip()
    if not value or len(value) > 160:
        return fallback
    if not re.fullmatch(r"[A-Za-z0-9_.:/ +@-]+", value):
        return fallback
    return value


def _safe_endpoint(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = urlsplit(value.strip())
        port = parsed.port
    except ValueError:
        return None
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
        return None
    host = parsed.hostname.lower()
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    default = 80 if parsed.scheme.lower() == "http" else 443
    netloc = host if port in {None, default} else f"{host}:{port}"
    path = parsed.path or "/"
    return urlunsplit((parsed.scheme.lower(), netloc, path, "", ""))


def _provider_origin(provider: Any) -> str | None:
    endpoint = getattr(provider, "endpoint", None)
    if not isinstance(endpoint, str) or not endpoint.strip():
        return None
    try:
        return normalize_origin(endpoint.strip())
    except (PolicyError, ValueError):
        return None


def _provider_name(provider: Any) -> str:
    return _safe_identity(getattr(provider, "name", None), fallback=type(provider).__name__)


def _provider_model(provider: Any) -> str | None:
    value = getattr(provider, "model", None)
    if not isinstance(value, str) or not value.strip():
        value = getattr(provider, "model_id", None)
    if not isinstance(value, str) or not value.strip():
        return None
    return _safe_identity(value, fallback="identity-redacted")


def _resource_id(*, role: str, provider: Any) -> str:
    name = _provider_name(provider)
    model = _provider_model(provider) or ""
    class_id = f"{type(provider).__module__}.{type(provider).__name__}"
    basis = f"{role}|{name}|{model}|{class_id}"
    digest = hashlib.sha256(basis.encode("utf-8")).hexdigest()[:12]
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:48] or "provider"
    return f"cognition:{role}:{slug}:{digest}"


def _usage_identity(provider: Any) -> dict[str, str] | None:
    getter = getattr(provider, "usage_snapshot", None)
    if not callable(getter):
        return None
    try:
        usage = getter()
    except (AttributeError, TypeError, ValueError):
        return None
    if usage is None:
        return None
    if hasattr(usage, "to_dict") and callable(usage.to_dict):
        try:
            raw = usage.to_dict()
        except (AttributeError, TypeError, ValueError):
            raw = None
    elif isinstance(usage, dict):
        raw = usage
    else:
        raw = {
            "provider": getattr(usage, "provider", None),
            "model": getattr(usage, "model", None),
        }
    if not isinstance(raw, dict):
        return None
    observed: dict[str, str] = {}
    provider_name = raw.get("provider")
    model = raw.get("model")
    if isinstance(provider_name, str) and provider_name.strip():
        observed["provider"] = _safe_identity(provider_name, fallback="identity-redacted")
    if isinstance(model, str) and model.strip():
        observed["model"] = _safe_identity(model, fallback="identity-redacted")
    return observed or None


def _response_observed(provider: Any) -> bool:
    getter = getattr(provider, "response_id_snapshot", None)
    if not callable(getter):
        return False
    try:
        value = getter()
    except (AttributeError, TypeError, ValueError):
        return False
    return isinstance(value, str) and bool(value.strip())


def _disclosure_snapshot(provider: Any) -> dict[str, Any] | None:
    getter = getattr(provider, "disclosure_policy_snapshot", None)
    if not callable(getter):
        return None
    try:
        raw = getter()
    except (AttributeError, TypeError, ValueError):
        return None
    if not isinstance(raw, dict):
        return None
    allowed = {
        "sha256",
        "allowed_scope_count",
        "allow_order_text",
        "allow_craft",
        "allow_memory",
        "allowed_observation_actions",
    }
    return {key: raw[key] for key in allowed if key in raw}


def _session_ready(provider: Any) -> bool:
    if isinstance(provider, SessionReasoningProvider):
        return callable(getattr(provider, "_responder", None))
    if isinstance(provider, SessionCrewCognitionProvider):
        return callable(getattr(provider, "_responder", None))
    return False


class CognitionProviderAwareness:
    """Fresh privacy-safe awareness over already-bound hosted cognition providers.

    Passive inventory never scans for providers, reads credential values, invokes
    callbacks/network endpoints, changes bindings, or performs provider selection.
    A separate explicitly authorized refresh may observe only current transport
    reachability for an already-bound remote origin through the existing A5 Tool
    Gateway. Transport evidence never establishes provider readiness or fitness.
    """

    schema = "grox-live-hosted-cognition-inventory-v1"
    resource_kind = "hosted_cognition_provider"

    def __init__(
        self,
        *,
        reasoner: Any = None,
        crew_provider: Any = None,
        gateway: ToolGateway | None = None,
        transport_observations: MutableMapping[str, Any] | None = None,
        clock: Callable[[], float] = monotonic,
        transport_freshness_seconds: float = 60.0,
    ):
        if gateway is not None and not isinstance(gateway, ToolGateway):
            raise TypeError("gateway must be a ToolGateway or null")
        if not callable(clock):
            raise TypeError("clock must be callable")
        if isinstance(transport_freshness_seconds, bool) or not isinstance(
            transport_freshness_seconds, (int, float)
        ):
            raise TypeError("transport_freshness_seconds must be numeric")
        if transport_freshness_seconds <= 0:
            raise ValueError("transport_freshness_seconds must be positive")
        self.reasoner = reasoner
        self.crew_provider = crew_provider
        self.gateway = gateway
        self.transport_observations = transport_observations if transport_observations is not None else {}
        self.clock = clock
        self.transport_freshness_seconds = float(transport_freshness_seconds)

    def _candidates(self) -> tuple[tuple[str, Any], ...]:
        return (
            ("gorxu_reasoner", self.reasoner),
            ("crew_cognition", self.crew_provider),
        )

    def _transport_snapshot(self, *, resource_id: str, is_remote: bool) -> dict[str, Any]:
        if not is_remote:
            return {
                "transport_reachable": False,
                "transport_fresh": False,
                "transport_status": "not_applicable",
                "transport_http_status": None,
                "transport_age_seconds": None,
            }
        raw = self.transport_observations.get(resource_id)
        if not isinstance(raw, dict):
            return {
                "transport_reachable": False,
                "transport_fresh": False,
                "transport_status": "unproven",
                "transport_http_status": None,
                "transport_age_seconds": None,
            }
        observed_at = raw.get("observed_at")
        if isinstance(observed_at, bool) or not isinstance(observed_at, (int, float)):
            return {
                "transport_reachable": False,
                "transport_fresh": False,
                "transport_status": "unproven",
                "transport_http_status": None,
                "transport_age_seconds": None,
            }
        age = max(0.0, float(self.clock()) - float(observed_at))
        if age > self.transport_freshness_seconds:
            return {
                "transport_reachable": False,
                "transport_fresh": False,
                "transport_status": "stale",
                "transport_http_status": None,
                "transport_age_seconds": age,
            }
        reachable = raw.get("reachable") is True
        http_status = raw.get("http_status")
        if isinstance(http_status, bool) or not isinstance(http_status, int):
            http_status = None
        return {
            "transport_reachable": reachable,
            "transport_fresh": True,
            "transport_status": "reachable" if reachable else "unreachable",
            "transport_http_status": http_status if reachable else None,
            "transport_age_seconds": age,
        }

    def _snapshot(
        self,
        *,
        role: str,
        provider: Any,
        policy: CognitionProviderPolicy | None,
    ) -> dict[str, Any] | None:
        if provider is None or not isinstance(provider, _HOSTED_TYPES):
            return None
        runtime = getattr(provider, "runtime", None)
        if isinstance(runtime, LocalModelRuntime):
            return None

        resource_id = _resource_id(role=role, provider=provider)
        authorized = resource_id in policy.authorized_ids if policy is not None else False
        qualification_recorded = resource_id in policy.qualified_ids if policy is not None else False
        observed_identity = _usage_identity(provider)
        observed = observed_identity is not None or _response_observed(provider)
        is_session = isinstance(provider, _SESSION_TYPES)
        is_remote = isinstance(provider, _REMOTE_TYPES)
        transport_evidence = self._transport_snapshot(resource_id=resource_id, is_remote=is_remote)

        if is_session:
            ready = _session_ready(provider)
            readiness_status = "host_session_bound" if ready else "host_session_contract_unavailable"
            readiness_reason = (
                "required in-process host callback is bound; callback was not invoked"
                if ready
                else "required in-process host callback is unavailable"
            )
            transport = "host_session"
        elif is_remote:
            ready = False
            readiness_status = "remote_reachability_unproven"
            if transport_evidence["transport_fresh"]:
                readiness_reason = (
                    "current origin transport was observed separately, but credential, provider, and model readiness remain unproven"
                )
            elif observed:
                readiness_reason = (
                    "prior provider execution was observed, but current provider readiness and credential validity were not revalidated"
                )
            else:
                readiness_reason = "remote provider is configured but provider readiness and credential validity were not probed"
            transport = "remote_https"
        else:  # pragma: no cover - _HOSTED_TYPES keeps this bounded.
            return None

        details: dict[str, Any] = {
            "provider": _provider_name(provider),
            "transport": transport,
        }
        model = _provider_model(provider)
        if model is not None:
            details["model"] = model
        endpoint = _safe_endpoint(getattr(provider, "endpoint", None))
        if endpoint is not None:
            details["endpoint"] = endpoint
        disclosure = _disclosure_snapshot(provider)
        if disclosure is not None:
            details["disclosure_policy"] = disclosure

        return {
            "resource_id": resource_id,
            "resource_kind": self.resource_kind,
            "role": role,
            "discovered": True,
            "authorized": authorized,
            "ready": ready,
            "readiness_status": readiness_status,
            "readiness_reason": readiness_reason,
            "qualification_recorded": qualification_recorded,
            "qualified_fit": bool(ready and qualification_recorded),
            "selected": True,
            "selection_source": "existing_pilot_binding",
            "observed": observed,
            "observed_identity": dict(observed_identity) if observed_identity is not None else None,
            **transport_evidence,
            "details": details,
            "authority_changed": False,
            "auto_selection": False,
            "auto_invocation": False,
        }

    def _remote_binding(self, resource_id: str) -> tuple[Any, str]:
        if not isinstance(resource_id, str) or not resource_id.strip():
            raise CognitionTransportAuthorizationError("resource_id must identify one currently bound remote cognition resource")
        for role, provider in self._candidates():
            if provider is None or not isinstance(provider, _REMOTE_TYPES):
                continue
            runtime = getattr(provider, "runtime", None)
            if isinstance(runtime, LocalModelRuntime):
                continue
            current_id = _resource_id(role=role, provider=provider)
            if current_id != resource_id:
                continue
            origin = _provider_origin(provider)
            if origin is None:
                raise CognitionTransportAuthorizationError("bound remote cognition endpoint has no safe HTTP(S) origin")
            return provider, origin
        raise CognitionTransportAuthorizationError("resource_id is not a currently bound remote cognition resource")

    def _authorize_transport_refresh(self, *, resource_id: str, order: MissionOrder, origin: str) -> None:
        if not isinstance(order, MissionOrder):
            raise CognitionTransportAuthorizationError("transport refresh requires a MissionOrder")
        if not order.sealed:
            raise CognitionTransportAuthorizationError("transport refresh requires an already sealed Mission Order")
        if "net_fetch" in order.forbidden_actions or "net_fetch" not in order.allowed_actions:
            raise CognitionTransportAuthorizationError("sealed Mission Order does not grant net_fetch")
        if order.parameters.get("operation") != "cognition_transport_probe":
            raise CognitionTransportAuthorizationError("sealed Mission Order operation must be cognition_transport_probe")
        if order.parameters.get("resource_id") != resource_id:
            raise CognitionTransportAuthorizationError("sealed Mission Order does not bind this cognition resource_id")

        raw_origins = order.parameters.get("allowed_origins") or ()
        if not isinstance(raw_origins, (list, tuple)) or not all(
            isinstance(value, str) and bool(value.strip()) for value in raw_origins
        ):
            raise CognitionTransportAuthorizationError("sealed Mission Order allowed_origins are invalid")
        try:
            order_origins = frozenset(normalize_origin(value) for value in raw_origins)
        except PolicyError as exc:
            raise CognitionTransportAuthorizationError(str(exc)) from exc
        if origin not in order_origins:
            raise CognitionTransportAuthorizationError("bound cognition origin is not granted by the sealed Mission Order")

        if self.gateway is None:
            raise CognitionTransportAuthorizationError("no governed Tool Gateway is bound for transport refresh")
        if not self.gateway.policy.network_enabled:
            raise CognitionTransportAuthorizationError("network capability is disabled by host policy")
        if origin not in self.gateway.policy.allowed_origins:
            raise CognitionTransportAuthorizationError("bound cognition origin is outside host Gateway policy")

    def refresh_transport(self, *, resource_id: str, order: MissionOrder) -> dict[str, Any]:
        """Refresh only volatile origin-transport evidence for one bound remote resource.

        This method never seals an Order, sends provider credentials/cognition
        payloads, persists evidence, changes provider bindings, or asserts remote
        provider readiness. Runtime network work is delegated exclusively to the
        existing Tool Gateway after exact authority is prevalidated.
        """
        _, origin = self._remote_binding(resource_id)
        self._authorize_transport_refresh(resource_id=resource_id, order=order, origin=origin)
        assert self.gateway is not None  # established by authorization above

        observed_at = float(self.clock())
        try:
            response = self.gateway.fetch_url(order, origin + "/")
        except (ToolDenied, TimeoutError, OSError):
            self.transport_observations[resource_id] = {
                "observed_at": observed_at,
                "reachable": False,
                "http_status": None,
            }
        else:
            status = response.get("status") if isinstance(response, dict) else None
            self.transport_observations[resource_id] = {
                "observed_at": observed_at,
                "reachable": True,
                "http_status": status if isinstance(status, int) and not isinstance(status, bool) else None,
            }

        refreshed = self.inventory()["resources"]
        for item in refreshed:
            if item["resource_id"] == resource_id:
                return item
        raise CognitionTransportAuthorizationError("bound cognition resource changed during transport refresh")

    def inventory(self, *, policy: CognitionProviderPolicy | None = None) -> dict[str, Any]:
        if policy is not None and not isinstance(policy, CognitionProviderPolicy):
            raise TypeError("policy must be a CognitionProviderPolicy or null")
        resources: list[dict[str, Any]] = []
        delegated_local = 0
        for role, provider in self._candidates():
            if provider is not None and isinstance(getattr(provider, "runtime", None), LocalModelRuntime):
                delegated_local += 1
                continue
            snapshot = self._snapshot(role=role, provider=provider, policy=policy)
            if snapshot is not None:
                resources.append(snapshot)
        return {
            "schema": self.schema,
            "resources": resources,
            "local_runtime_delegated_count": delegated_local,
            "authority_changed": False,
            "auto_selection": False,
            "auto_invocation": False,
        }
