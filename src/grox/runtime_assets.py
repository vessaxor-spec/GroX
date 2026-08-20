from __future__ import annotations

import json
from importlib import metadata
from pathlib import Path


DISTRIBUTION_NAME = "grox-vessel"
EXPECTED_STANDING_CREW = 82


class RuntimeAssetError(RuntimeError):
    """Raised when installed GroX runtime assets are missing or malformed."""


def validate_asset_root(asset_root: Path | str) -> Path:
    """Validate the immutable runtime bundle required to construct GorXu.

    This check is deliberately structural and fail-closed. It verifies the
    canonical policy/manifest files, the complete Standing Crew dossier set,
    matching deep-craft cards, and parseability/identity of every dossier.
    Runtime assets remain infrastructure beneath GorXu; validation does not
    activate models, Crew, or authority.
    """

    root = Path(asset_root).expanduser().resolve()
    policy = root / "configs" / "tool-policy.json"
    manifest = root / "configs" / "crew" / "company-manifest.json"
    dossiers_dir = root / "configs" / "crew" / "dossiers"
    specialists_dir = root / "configs" / "crew" / "specialists"

    required = (policy, manifest, dossiers_dir, specialists_dir)
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise RuntimeAssetError(
            "GroX packaged runtime assets are incomplete; missing: " + ", ".join(missing)
        )

    try:
        json.loads(policy.read_text(encoding="utf-8"))
        json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeAssetError(f"GroX packaged runtime metadata is malformed: {exc}") from exc

    dossiers = sorted(dossiers_dir.glob("*.json"))
    specialists = sorted(specialists_dir.glob("*.md"))
    if len(dossiers) != EXPECTED_STANDING_CREW:
        raise RuntimeAssetError(
            f"GroX packaged runtime must contain exactly {EXPECTED_STANDING_CREW} Standing Crew dossiers; "
            f"found {len(dossiers)}"
        )
    if len(specialists) != EXPECTED_STANDING_CREW:
        raise RuntimeAssetError(
            f"GroX packaged runtime must contain exactly {EXPECTED_STANDING_CREW} Standing Crew craft cards; "
            f"found {len(specialists)}"
        )

    dossier_ids = {path.stem for path in dossiers}
    specialist_ids = {path.stem for path in specialists}
    if dossier_ids != specialist_ids:
        missing_craft = sorted(dossier_ids - specialist_ids)
        orphan_craft = sorted(specialist_ids - dossier_ids)
        raise RuntimeAssetError(
            "GroX packaged Crew/craft identity mismatch: "
            f"missing_craft={missing_craft}; orphan_craft={orphan_craft}"
        )

    for path in dossiers:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeAssetError(f"Malformed packaged Crew dossier: {path}: {exc}") from exc
        if not isinstance(payload, dict):
            raise RuntimeAssetError(f"Malformed packaged Crew dossier object: {path}")
        crew_id = payload.get("crew_id")
        if crew_id != path.stem:
            raise RuntimeAssetError(
                f"Packaged Crew dossier identity mismatch: {path.name}: crew_id={crew_id!r}"
            )

    return root


def packaged_asset_root() -> Path:
    """Locate and validate the runtime assets installed by the GroX wheel."""

    try:
        dist = metadata.distribution(DISTRIBUTION_NAME)
    except metadata.PackageNotFoundError as exc:
        raise RuntimeAssetError(
            f"Installed GroX distribution is unavailable: {DISTRIBUTION_NAME}"
        ) from exc

    files = dist.files or ()
    suffix = "share/grox/configs/tool-policy.json"
    for item in files:
        normalized = str(item).replace("\\", "/")
        if not normalized.endswith(suffix):
            continue
        policy = Path(dist.locate_file(item)).resolve()
        return validate_asset_root(policy.parent.parent)

    raise RuntimeAssetError(
        "GroX packaged runtime assets are incomplete or unavailable; "
        "the installed distribution does not contain the required runtime asset bundle"
    )
