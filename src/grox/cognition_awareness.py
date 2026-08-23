from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from .native_model_runtime import LocalModelRuntime
from .openai_crew_cognition import OpenAICrewCognitionProvider
from .reasoning.openai_responses import OpenAIResponsesProvider
from .reasoning.session import SessionReasoningProvider
from .session_crew_cognition import SessionCrewCognitionProvider


_HOSTED_TYPES = (
    SessionReasoningProvider,
    SessionCrewCognitionProvider,
    OpenAIResponsesProvider,
    OpenAICrewCognitionProvider,
)


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

    The surface never scans for providers, reads credential values, invokes a
    callback/network endpoint, changes a binding, or performs provider selection.
    LocalModelRuntime-backed cognition remains owned by local runtime awareness.
    """

    schema = "grox-live-hosted-cognition-inventory-v1"
    resource_kind = "hosted_cognition_provider"

    def __init__(self, *, reasoner: Any = None, crew_provider: Any = None):
        self.reasoner = reasoner
        self.crew_provider = crew_provider

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
        is_session = isinstance(provider, (SessionReasoningProvider, SessionCrewCognitionProvider))
        is_remote = isinstance(provider, (OpenAIResponsesProvider, OpenAICrewCognitionProvider))

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
            readiness_reason = (
                "prior provider execution was observed, but current reachability and credential validity were not revalidated"
                if observed
                else "remote provider is configured but reachability and credential validity were not probed"
            )
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
            "details": details,
            "authority_changed": False,
            "auto_selection": False,
            "auto_invocation": False,
        }

    def inventory(self, *, policy: CognitionProviderPolicy | None = None) -> dict[str, Any]:
        if policy is not None and not isinstance(policy, CognitionProviderPolicy):
            raise TypeError("policy must be a CognitionProviderPolicy or null")
        resources: list[dict[str, Any]] = []
        delegated_local = 0
        candidates = (
            ("gorxu_reasoner", self.reasoner),
            ("crew_cognition", self.crew_provider),
        )
        for role, provider in candidates:
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
