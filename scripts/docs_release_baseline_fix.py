from pathlib import Path

SHA = "71ffd60769d81b5b249dac4eca56333ff27e26d0"
TAG = "v0.7.0"


def patch(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text()
    count = text.count(old)
    assert count == 1, f"{path}: expected one match, found {count}: {old!r}"
    p.write_text(text.replace(old, new, 1))


patch(
    "AI_INSTRUCTIONS.md",
    f"**Current qualified baseline:** `{TAG}` / `main@{SHA}` / **APEX QUALIFIED** / **82 Standing Crew**.",
    f"**Current qualified release baseline:** `{TAG}@{SHA}` / **APEX QUALIFIED** / **82 Standing Crew**. Canonical source continues on `main`.",
)
patch(
    "docs/architecture/ARCHITECTURE.md",
    f"**Qualified baseline:** GroX `{TAG}` at `main@{SHA}`. GorXu is **APEX QUALIFIED** with **82 Standing Crew**. A1–A7 are qualified for the current project-hosted operating model.",
    f"**Qualified release baseline:** GroX `{TAG}@{SHA}`. Canonical source continues on `main`. GorXu is **APEX QUALIFIED** with **82 Standing Crew**. A1–A7 are qualified for the current project-hosted operating model.",
)
patch(
    "docs/architecture/PERSISTENCE_ARCHITECTURE.md",
    f"**Qualified baseline:** `{TAG}` / `main@{SHA}`. Snapshot source binding, ancestor compatibility control, and fail-closed unrelated-source restore are part of the Apex regression boundary.",
    f"**Qualified release baseline:** `{TAG}@{SHA}`. Canonical source continues on `main`. Snapshot source binding, ancestor compatibility control, and fail-closed unrelated-source restore are part of the Apex regression boundary.",
)
patch(
    "docs/stewardship/CREW_ROSTER.md",
    f"**Current baseline:** GroX `{TAG}` / `main@{SHA}` / **82 Standing Crew**.",
    f"**Current released baseline:** GroX `{TAG}@{SHA}` / **82 Standing Crew**. Canonical source continues on `main`.",
)
patch(
    "docs/stewardship/SANDBOX_COMMISSIONING.md",
    f"**Current released baseline:** GroX `{TAG}` / `main@{SHA}` / **APEX QUALIFIED** / **82 Standing Crew**.",
    f"**Current released baseline:** GroX `{TAG}@{SHA}` / **APEX QUALIFIED** / **82 Standing Crew**. Canonical source continues on `main`.",
)
patch(
    "docs/stewardship/APEX_ORCHESTRATOR_PLAN.md",
    f"**Release baseline:** `{TAG}` at `main@{SHA}`",
    f"**Release baseline:** `{TAG}@{SHA}`; canonical source continues on `main`",
)
patch(
    "docs/stewardship/APEX_ORCHESTRATOR_PLAN.md",
    f"release `{TAG}` is pinned to canonical `main@{SHA}`.",
    f"release `{TAG}` is pinned to `{SHA}` while canonical source continues on `main`.",
)
patch(
    "docs/stewardship/ROADMAP.md",
    f"release `{TAG}` now points to canonical `main@{SHA}`.",
    f"release `{TAG}` is pinned to `{SHA}` while canonical source continues on `main`.",
)
patch(
    "docs/stewardship/progress-tracker.md",
    f"**Canonical source:** `main@{SHA}`",
    f"**Canonical source branch:** `main`\n**Released qualified source:** `{TAG}@{SHA}`",
)
patch(
    "docs/stewardship/progress-tracker.md",
    f"release `{TAG}` is published from canonical `main@{SHA}`;",
    f"release `{TAG}` is pinned to `{SHA}` and canonical source continues on `main`;",
)
patch(
    "docs/history/ships-log/0034-v0.7.0-apex-baseline-released.md",
    f"GroX release `{TAG}` is pinned to canonical source `main@{SHA}`.",
    f"GroX release `{TAG}` is pinned to source commit `{SHA}`; canonical source continues on `main`.",
)
