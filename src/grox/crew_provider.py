from __future__ import annotations

import json
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from .contracts import MissionMode, RiskClass


class CrewProviderBindingError(RuntimeError):
    """The requested Crew cognition provider cannot be safely bound."""


def bind_crew_cognition_provider(pilot: Any, provider: Any) -> str:
    """Bind one provider to the existing Pilot-owned Crew executor.

    Binding changes cognition availability only. It does not grant actions,
    capability, scope, Repair authority, routing authority, or verification
    authority; those remain enforced by existing GroX boundaries.
    """
    executor = getattr(pilot, "executor", None)
    if executor is None:
        raise CrewProviderBindingError("Pilot has no Crew executor")
    if provider is None or not callable(getattr(provider, "next_step", None)):
        raise CrewProviderBindingError("Crew cognition provider must expose callable next_step")
    name = getattr(provider, "name", None)
    if not isinstance(name, str) or not name.strip():
        raise CrewProviderBindingError("Crew cognition provider must expose a non-empty name")
    executor.cognition_provider = provider
    return name.strip()


def bound_crew_cognition_provider(pilot: Any) -> str | None:
    executor = getattr(pilot, "executor", None)
    provider = getattr(executor, "cognition_provider", None) if executor is not None else None
    name = getattr(provider, "name", None) if provider is not None else None
    return name.strip() if isinstance(name, str) and name.strip() else None


def _content(row: dict[str, Any]) -> dict[str, Any]:
    content = row.get("content")
    if isinstance(content, str):
        try:
            decoded = json.loads(content)
        except (json.JSONDecodeError, TypeError):
            return {}
        return decoded if isinstance(decoded, dict) else {}
    return dict(content) if isinstance(content, dict) else {}


def _safe_endpoint(endpoint: str) -> str | None:
    try:
        parsed = urlsplit(endpoint)
    except ValueError:
        return None
    if not parsed.scheme or not parsed.hostname:
        return None
    host = parsed.hostname
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    try:
        port = parsed.port
    except ValueError:
        return None
    netloc = host if port is None else f"{host}:{port}"
    return urlunsplit((parsed.scheme, netloc, parsed.path, "", ""))


def _provider_observability(provider: Any) -> dict[str, Any]:
    observed: dict[str, Any] = {}
    model = getattr(provider, "model", None)
    if isinstance(model, str) and model.strip():
        observed["model"] = model.strip()
    endpoint = getattr(provider, "endpoint", None)
    if isinstance(endpoint, str) and endpoint.strip():
        safe_endpoint = _safe_endpoint(endpoint.strip())
        if safe_endpoint is not None:
            observed["endpoint"] = safe_endpoint
    response_id_snapshot = getattr(provider, "response_id_snapshot", None)
    if callable(response_id_snapshot):
        response_id = response_id_snapshot()
        if isinstance(response_id, str) and response_id.strip():
            observed["response_id"] = response_id.strip()
    usage_snapshot = getattr(provider, "usage_snapshot", None)
    if callable(usage_snapshot):
        usage = usage_snapshot()
        if usage is not None:
            to_dict = getattr(usage, "to_dict", None)
            if callable(to_dict):
                usage = to_dict()
            if isinstance(usage, dict):
                observed["usage"] = dict(usage)
    disclosure_snapshot = getattr(provider, "disclosure_policy_snapshot", None)
    if callable(disclosure_snapshot):
        disclosure = disclosure_snapshot()
        if isinstance(disclosure, dict):
            observed["disclosure_policy"] = dict(disclosure)
    return observed


def qualify_bound_crew_cognition_provider(
    pilot: Any,
    *,
    directive: str,
    crew_id: str,
    scope: str = ".",
) -> dict[str, Any]:
    """Run and assess one provider-backed high-risk Inspect Mission.

    PASS proves that the currently bound provider completed the governed Crew
    cognition path under the existing GroX boundaries. It does *not* by itself
    prove that the provider was a live external/session model; that fact must be
    established by the host/operator evidence for the invocation environment.
    """
    provider_name = bound_crew_cognition_provider(pilot)
    if provider_name is None:
        raise CrewProviderBindingError("No Crew cognition provider is bound")
    provider = pilot.executor.cognition_provider
    if not isinstance(directive, str) or not directive.strip():
        raise ValueError("directive must be a non-empty string")
    if not isinstance(crew_id, str) or not crew_id.strip():
        raise ValueError("crew_id must be a non-empty string")

    result = pilot.command(
        directive.strip(),
        mode=MissionMode.inspect,
        risk=RiskClass.high,
        crew_id=crew_id.strip(),
        scope=scope,
    )
    mission = pilot.store.mission(result["mission_id"])
    evidence = list((mission or {}).get("evidence") or [])
    kinds = [row.get("kind") for row in evidence]
    cognition_rows = [row for row in evidence if row.get("kind") == "crew_cognition"]
    cognition = _content(cognition_rows[-1]) if cognition_rows else {}
    outcome = result.get("outcome") if isinstance(result.get("outcome"), dict) else {}
    verification = result.get("verification") if isinstance(result.get("verification"), dict) else {}

    checks = {
        "mission_completed": result.get("status") == "completed",
        "inspect_mode_preserved": result.get("mode") == MissionMode.inspect.value,
        "craft_selection_evidenced": "craft_selection" in kinds,
        "memory_selection_evidenced": "memory_selection" in kinds,
        "governed_observation_evidenced": "crew_cognition_observation" in kinds,
        "crew_work_product_evidenced": bool(cognition_rows) and bool(cognition),
        "provider_identity_matches": cognition.get("provider") == provider_name,
        "read_only_mode_evidenced": cognition.get("mode") == "read_only_inspect",
        "bounded_work_product": isinstance(cognition.get("work_product"), str)
        and len(cognition.get("work_product", "")) <= int(pilot.executor.cognition_work_product_chars),
        "no_cognition_denial": "crew_cognition_denied" not in kinds,
        "no_cognition_degradation": "crew_cognition_degraded" not in kinds,
        "no_mutation_evidence": "mutation" not in kinds and "mutation_rollback" not in kinds,
        "outcome_reports_no_mutation": outcome.get("mutation") is False,
        "independent_verification_passed": verification.get("ok") is True,
    }
    passed = all(checks.values())
    return {
        "schema": "grox-crew-cognition-provider-qualification-v1",
        "status": "PASS" if passed else "FAIL",
        "provider": provider_name,
        "provider_observability": _provider_observability(provider),
        "mission_id": result["mission_id"],
        "crew_id": result.get("crew"),
        "checks": checks,
        "evidence_kinds": sorted({str(kind) for kind in kinds if kind}),
        "live_provider_claim": False,
        "claim_boundary": (
            "PASS proves provider-backed execution through the bounded Inspect Crew cognition seam; "
            "the host/operator must separately establish that the bound provider invocation was a live model/session."
        ),
    }
