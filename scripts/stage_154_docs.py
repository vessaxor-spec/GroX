from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one target, found {count}: {old[:100]!r}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


def append_once(path: str, marker: str, block: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if marker in text:
        raise SystemExit(f"{path}: block already present: {marker}")
    p.write_text(text.rstrip() + "\n\n" + block.rstrip() + "\n", encoding="utf-8")


# README current-state synchronization.
replace_once(
    "README.md",
    "**IN PROGRESS — eight bounded exits QUALIFIED**",
    "**IN PROGRESS — nine bounded exits QUALIFIED**",
)
replace_once(
    "README.md",
    "configured remote cognition connection-policy awareness (#144/#145), and configured local llama.cpp readiness awareness (#148/#149). Parent #115 remains open;",
    "configured remote cognition connection-policy awareness (#144/#145), configured local llama.cpp readiness awareness (#148/#149), and governed secret-alias availability awareness (#152/#153). Parent #115 remains open;",
)
replace_once(
    "README.md",
    "- **21/21** current critical-invariant mutations killed; the original Stage 1 qualification remains historically **12/12**, with nine later Live Environment Awareness authority/evidence mutations extending the current matrix;",
    "- **22/22** current critical-invariant mutations killed; the original Stage 1 qualification remains historically **12/12**, with ten later Live Environment Awareness authority/evidence mutations extending the current matrix;",
)

# Architecture current-state synchronization and strict ninth boundary.
replace_once(
    "docs/architecture/ARCHITECTURE.md",
    "and eight bounded Live Environment Awareness exits qualified:",
    "and nine bounded Live Environment Awareness exits qualified:",
)
replace_once(
    "docs/architecture/ARCHITECTURE.md",
    "configured remote cognition connection-policy awareness, and configured local llama.cpp readiness awareness. These source advances",
    "configured remote cognition connection-policy awareness, configured local llama.cpp readiness awareness, and governed secret-alias availability awareness. These source advances",
)
replace_once(
    "docs/architecture/ARCHITECTURE.md",
    "Current protected source qualifies eight bounded surfaces:",
    "Current protected source qualifies nine bounded surfaces:",
)
replace_once(
    "docs/architecture/ARCHITECTURE.md",
    "configured remote cognition connection-policy awareness (#144/#145), and configured local llama.cpp readiness awareness (#148/#149).",
    "configured remote cognition connection-policy awareness (#144/#145), configured local llama.cpp readiness awareness (#148/#149), and governed secret-alias availability awareness (#152/#153).",
)
local_para = "The configured-local readiness surface is likewise explicit and non-activating. For one valid supported configured `local-llama-cpp` cognition resource, it reuses the existing GroX model registry/runtime/backend readiness primitives to check exact model registration and artifact integrity, current host constraints, and the exact configured llama.cpp executable against the pinned supported build. The only local process probe is the existing bounded `llama.cpp --version` support check. `ready=True` remains strictly separate from Mission authorization, qualification/fit, selection, and observation; the surface never loads a model, invokes cognition, touches network or credentials, binds a provider, creates a Mission, performs fallback, or changes routing."
secret_para = "The governed secret-alias availability surface is deliberately secret-blind. For one exact alias already represented in the host-injected memory-only `SecretBroker`, it reports only exact alias membership through `has_alias(alias)`. It never enumerates aliases or returns, hashes, compares, persists, logs, transforms, materializes, or validates a secret value; a default empty broker fails closed. It performs no environment/filesystem/keychain scan, network request, provider construction or binding, cognition invocation, or Mission creation. Alias availability never implies Mission authorization, credential validity, readiness, qualification/fit, selection, observation, fallback, or routing."
replace_once(
    "docs/architecture/ARCHITECTURE.md",
    local_para + "\n\nThe remote transport refresh is deliberately narrow.",
    local_para + "\n\n" + secret_para + "\n\nThe remote transport refresh is deliberately narrow.",
)

# Roadmap current state, mutation count, and ninth qualification evidence.
replace_once(
    "docs/stewardship/ROADMAP.md",
    "qualified configured remote cognition connection-policy awareness exit, and qualified configured local llama.cpp readiness awareness exit**.",
    "qualified configured remote cognition connection-policy awareness exit, qualified configured local llama.cpp readiness awareness exit, and qualified governed secret-alias availability awareness exit**.",
)
replace_once(
    "docs/stewardship/ROADMAP.md",
    "- 21 high-consequence production invariants continuously mutation-proven; the original Stage 1 12/12 record remains historical and nine later Live Environment Awareness authority/evidence mutations extend the current matrix.",
    "- 22 high-consequence production invariants continuously mutation-proven; the original Stage 1 12/12 record remains historical and ten later Live Environment Awareness authority/evidence mutations extend the current matrix.",
)
roadmap_evidence = "- **Live Environment Awareness governed secret-alias availability exit is QUALIFIED:** issue #152 / PR #153 add secret-blind awareness for one exact alias already represented in the host-injected memory-only `SecretBroker`. `SecretBroker.has_alias(alias)` exposes only exact membership; the awareness surface does not enumerate aliases or return/hash/compare/persist/log/transform/materialize/validate secret values. A default empty broker fails closed and a materialization-trap regression proves awareness never calls `materialize_env`. No environment/filesystem/keychain scan, network request, provider construction/binding, cognition invocation, Mission creation, readiness/fitness promotion, selection, observation, fallback, or routing occurs. Exact-head CI #523 / `32789939644` passed Wheel plus Python 3.11–3.14 on head `c077711ca1527595116f99a3e33b3cd0f688c85f`; Python 3.12 recorded Vessel Health 10/0/0/0, pytest 410 passed / 2 skipped / 473 subtests, unittest 412 OK / 2 skipped, critical mutations 22/22 plus 7/7 + 9/9 + 4/4 + 6/6 killed, and Post-Apex PASS. The permanent `secret-alias-exact-binding` mutation was killed. Bounded review `5013569847` passed with no threads. CI-tested synthetic merge `8dacf2e840b36e4eb6501b28d1ce88db986b34cc` and guarded canonical merge `main@8cc67b660bca51002fac0f125e2a7bc76f198599` share exact tree `b620add8465575cc7695a7cdb5b314a97decfeeb`. Actual credential validity, authenticated remote provider/service readiness, model quality / Mission-specific fitness, successful cognition semantics, arbitrary/unconfigured provider catalog discovery, broader external-connection/application/process awareness, provider switching/fallback, and adaptive routing remain unqualified. Parent #115 remains open."
replace_once(
    "docs/stewardship/ROADMAP.md",
    "\n## Apex critical path\n",
    "\n" + roadmap_evidence + "\n\n## Apex critical path\n",
)

# Doctrine status, canonical qualified state, sequencing, and ninth evidence.
replace_once(
    "docs/stewardship/ROADMAP_LIVE_ENVIRONMENT_AWARENESS_001.md",
    "**Status:** ROADMAP-BOUND / IMPLEMENTATION IN PROGRESS / LOCAL-RUNTIME + GOVERNED TOOL GATEWAY + BOUND HOSTED COGNITION + BOUND REMOTE TRANSPORT FRESHNESS + BOUND REMOTE ENDPOINT-SURFACE FRESHNESS + SUPPORTED CONFIGURED COGNITION DISCOVERY + CONFIGURED REMOTE CONNECTION POLICY AWARENESS + CONFIGURED LOCAL LLAMA.CPP READINESS EXITS QUALIFIED",
    "**Status:** ROADMAP-BOUND / IMPLEMENTATION IN PROGRESS / LOCAL-RUNTIME + GOVERNED TOOL GATEWAY + BOUND HOSTED COGNITION + BOUND REMOTE TRANSPORT FRESHNESS + BOUND REMOTE ENDPOINT-SURFACE FRESHNESS + SUPPORTED CONFIGURED COGNITION DISCOVERY + CONFIGURED REMOTE CONNECTION POLICY AWARENESS + CONFIGURED LOCAL LLAMA.CPP READINESS + GOVERNED SECRET-ALIAS AVAILABILITY EXITS QUALIFIED",
)
replace_once(
    "docs/stewardship/ROADMAP_LIVE_ENVIRONMENT_AWARENESS_001.md",
    "These exits still do **not** establish ambient application/process scanning, arbitrary tool discovery, arbitrary/unconfigured remote/cloud provider catalog discovery, authenticated provider/service readiness, credential validity, broader authorized external-connection discovery, model existence/availability/fitness, broader operational capability awareness, switching/fallback, or adaptive startup/resource routing.",
    "Issue #152 / PR #153 additionally qualify **governed secret-alias availability awareness** for one exact alias already represented in the host-injected memory-only `SecretBroker`. The surface reports only exact alias membership, does not enumerate aliases, and never returns, hashes, compares, persists, logs, transforms, materializes, or validates a secret value. A default empty broker fails closed and a materialization-trap regression proves awareness never calls `materialize_env`. Alias availability remains below and separate from Mission authorization, credential validity, readiness, qualification/fit, selection, observation, provider binding, cognition success, fallback, and routing. These exits still do **not** establish ambient application/process scanning, arbitrary tool discovery, arbitrary/unconfigured remote/cloud provider catalog discovery, authenticated provider/service readiness, actual credential validity, broader authorized external-connection discovery, model quality / Mission-specific fitness, broader operational capability awareness, switching/fallback, or adaptive startup/resource routing.",
)
replace_once(
    "docs/stewardship/ROADMAP_LIVE_ENVIRONMENT_AWARENESS_001.md",
    "Broader issue #115 remains open.",
    "The governed secret-alias availability exit is **QUALIFIED** through issue #152 / PR #153 and establishes only secret-blind exact-alias membership in an already host-injected memory-only broker; it neither materializes nor validates credentials and promotes no later awareness state. Broader issue #115 remains open.",
)
doctrine_evidence = "**Governed secret-alias availability qualification evidence:** issue #152 / PR #153 qualified the ninth bounded awareness exit. Red-before-green tests-only head `f01a12df9bb36ec10ccd85b6db349cd9cf5c1c70` kept the wheel path green while Python regression failed exactly on the intentionally missing `grox.secret_awareness` module. Final head `c077711ca1527595116f99a3e33b3cd0f688c85f` passed exact-head GroX CI #523 / `32789939644` across Wheel + Python 3.11–3.14; Python 3.12 recorded Health 10/0/0/0, pytest 410 passed / 2 skipped / 473 subtests, unittest 412 OK / 2 skipped, critical mutations 22/22 plus health 7/7, reconstitution 9/9, operational drift 4/4, source provenance 6/6, and Post-Apex PASS. Permanent mutation `secret-alias-exact-binding` was KILLED. Bounded review `5013569847` passed with no review threads. CI-tested synthetic merge `8dacf2e840b36e4eb6501b28d1ce88db986b34cc` and guarded canonical merge `main@8cc67b660bca51002fac0f125e2a7bc76f198599` share exact tree `b620add8465575cc7695a7cdb5b314a97decfeeb`; exact-tree equality PASS. This evidence qualifies only exact governed alias availability and does not qualify secret materialization, credential validity, authenticated remote readiness, model quality/Mission fitness, successful cognition semantics, broader catalog/application discovery, switching/fallback, adaptive routing, or any release/package/NCI/Apex/A8 advancement."
append_once(
    "docs/stewardship/ROADMAP_LIVE_ENVIRONMENT_AWARENESS_001.md",
    "**Governed secret-alias availability qualification evidence:**",
    doctrine_evidence,
)

# Progress tracker canonical source, regression state, ninth section, and next direction.
replace_once("docs/stewardship/progress-tracker.md", "**Status date:** 2026-08-24", "**Status date:** 2026-08-25")
replace_once(
    "docs/stewardship/progress-tracker.md",
    "**Current verified canonical source after configured local llama.cpp readiness awareness qualification:** `main@b477b785104f2931efb22172eea87e22a602346d`",
    "**Current verified canonical source after governed secret-alias availability qualification:** `main@8cc67b660bca51002fac0f125e2a7bc76f198599`",
)
replace_once(
    "docs/stewardship/progress-tracker.md",
    "**Current verified canonical tree:** `3524a24da5b16d90885b10dfbd227e0f019713d2`",
    "**Current verified canonical tree:** `b620add8465575cc7695a7cdb5b314a97decfeeb`",
)
replace_once(
    "docs/stewardship/progress-tracker.md",
    "pytest **404 passed, 2 skipped, 470 subtests**; unittest **406 OK, 2 skipped**; mutations **21/21**, **7/7**, **9/9**, **4/4**, **6/6** killed",
    "pytest **410 passed, 2 skipped, 473 subtests**; unittest **412 OK, 2 skipped**; mutations **22/22**, **7/7**, **9/9**, **4/4**, **6/6** killed",
)
replace_once(
    "docs/stewardship/progress-tracker.md",
    "CONFIGURED REMOTE CONNECTION POLICY AWARENESS + CONFIGURED LOCAL LLAMA.CPP READINESS EXITS QUALIFIED**",
    "CONFIGURED REMOTE CONNECTION POLICY AWARENESS + CONFIGURED LOCAL LLAMA.CPP READINESS + GOVERNED SECRET-ALIAS AVAILABILITY EXITS QUALIFIED**",
)
replace_once(
    "docs/stewardship/progress-tracker.md",
    "Continue issue #115 beyond the eight qualified bounded exits",
    "Continue issue #115 beyond the nine qualified bounded exits",
)
progress_section = """## Live Environment Awareness — governed secret-alias availability awareness — issue #152 / PR #153

**Status: COMPLETE — QUALIFIED — CANONICAL MERGED AND EXACT-TREE VERIFIED.**

Qualified boundary:

- applies only to one exact alias already represented in the host-injected memory-only `SecretBroker`;
- `SecretBroker.has_alias(alias)` reports exact membership only and exposes no alias enumeration or secret material;
- awareness never returns, hashes, compares, persists, logs, transforms, materializes, or validates a secret value;
- a materialization-trap regression proves awareness does not call `materialize_env`, while the default empty broker fails closed;
- no environment/filesystem/keychain/credential-store scan, network request, provider construction/binding, cognition invocation, Mission creation, fallback, or routing occurs;
- `authorized`, `ready`, `qualified_fit`, `selected`, and `observed` remain false; alias availability is not credential validity or provider readiness.

Qualification evidence:

- red-before-green tests-only head `f01a12df9bb36ec10ccd85b6db349cd9cf5c1c70`: wheel remained green while Python regression failed exactly because `grox.secret_awareness` was absent;
- final PR #153 head `c077711ca1527595116f99a3e33b3cd0f688c85f`;
- exact-head GroX CI #523 / `32789939644`: PASS Wheel + Python 3.11–3.14;
- Python 3.12: Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**; pytest **410 passed, 2 skipped, 473 subtests**; unittest **412 OK, 2 skipped**; critical mutations **22/22**; health **7/7**; reconstitution **9/9**; operational drift **4/4**; source provenance **6/6**; Post-Apex PASS;
- permanent mutation `secret-alias-exact-binding`: KILLED;
- bounded review `5013569847`: PASS with no review threads;
- CI-tested synthetic merge `8dacf2e840b36e4eb6501b28d1ce88db986b34cc`, tree `b620add8465575cc7695a7cdb5b314a97decfeeb`;
- guarded canonical merge `main@8cc67b660bca51002fac0f125e2a7bc76f198599`, same tree;
- synthetic-to-canonical tree equality: **PASS**;
- issue #152 closed completed; parent #115 remains **OPEN**.

Still unqualified: actual credential validity, authenticated remote provider/service readiness, model quality / Mission-specific fitness, successful cognition semantics, arbitrary/unconfigured provider catalogs, broader external-connection/application/process awareness, provider switching/fallback, and adaptive routing. No release/package/NCI/Apex/A8 advancement occurred.

"""
replace_once(
    "docs/stewardship/progress-tracker.md",
    "## Live Environment Awareness — configured local llama.cpp readiness awareness — issue #148 / PR #149\n",
    progress_section + "## Live Environment Awareness — configured local llama.cpp readiness awareness — issue #148 / PR #149\n",
)

# Critical invariant matrix: preserve historical Stage-1 12/12 and extend only the current matrix.
replace_once(
    "docs/verification/CRITICAL_INVARIANT_MUTATION_MATRIX.md",
    "Protected source later extended the same permanent harness with nine additional high-consequence Live Environment Awareness authority/evidence mutations. The current matrix is therefore **21/21 KILLED**; this extension does not rewrite the original Stage 1 run.",
    "Protected source later extended the same permanent harness with ten additional high-consequence Live Environment Awareness authority/evidence mutations. The current matrix is therefore **22/22 KILLED**; this extension does not rewrite the original Stage 1 run.",
)
row21 = "| 21 | Configured local cognition readiness must never imply Mission authorization | change configured-local readiness `authorized` from false to true in `src/grox/configured_local_readiness.py` | `ConfiguredLocalCognitionReadinessTests.test_ready_state_never_implies_authorization` | KILLED |"
row22 = "| 22 | Secret-alias availability must remain bound to the exact requested alias rather than any broker secret | replace exact alias membership in `src/grox/tools/secrets.py` with `bool(self._secrets)` | `SecretAliasAwarenessTests.test_absent_alias_fails_closed_without_enumerating_other_aliases` | KILLED |"
replace_once(
    "docs/verification/CRITICAL_INVARIANT_MUTATION_MATRIX.md",
    row21 + "\n\nLatest exact-head evidence",
    row21 + "\n" + row22 + "\n\nLatest exact-head evidence",
)
old_latest = "Latest exact-head evidence is PR #149 CI #502 / `32777798243`: Python 3.12 killed **21/21** critical mutations with zero survivors while all health, reconstitution, operational-drift, source-provenance, and Post-Apex gates remained green. The #16 mutation remains `cognition-transport-presealed-authority`; #17 is `cognition-transport-origin-binding`; #18 is `cognition-endpoint-exact-binding`; #19 is `configured-cognition-discovery-state-separation`; #20 is `configured-connection-exact-resource-binding`; #21 is `configured-local-readiness-authorization-separation`. The original Stage 1 **12/12** qualification remains preserved above as historical evidence."
new_latest = "Latest exact-head evidence is PR #153 CI #523 / `32789939644`: Python 3.12 killed **22/22** critical mutations with zero survivors while all health, reconstitution, operational-drift, source-provenance, and Post-Apex gates remained green. The #16 mutation remains `cognition-transport-presealed-authority`; #17 is `cognition-transport-origin-binding`; #18 is `cognition-endpoint-exact-binding`; #19 is `configured-cognition-discovery-state-separation`; #20 is `configured-connection-exact-resource-binding`; #21 is `configured-local-readiness-authorization-separation`; #22 is `secret-alias-exact-binding`. The original Stage 1 **12/12** qualification remains preserved above as historical evidence."
replace_once("docs/verification/CRITICAL_INVARIANT_MUTATION_MATRIX.md", old_latest, new_latest)

# Fail closed on stale current-state markers after the transform.
checks = {
    "README.md": ["eight bounded exits QUALIFIED", "**21/21** current critical-invariant"],
    "docs/architecture/ARCHITECTURE.md": ["eight bounded Live Environment Awareness exits qualified", "qualifies eight bounded surfaces"],
    "docs/stewardship/progress-tracker.md": ["beyond the eight qualified bounded exits", "mutations **21/21**"],
    "docs/verification/CRITICAL_INVARIANT_MUTATION_MATRIX.md": ["current matrix is therefore **21/21 KILLED**", "PR #149 CI #502 / `32777798243`: Python 3.12 killed **21/21**"],
}
for path, stale in checks.items():
    text = Path(path).read_text(encoding="utf-8")
    for needle in stale:
        if needle in text:
            raise SystemExit(f"{path}: stale current-state marker remains: {needle}")

print("stage-154 docs transform PASS")
