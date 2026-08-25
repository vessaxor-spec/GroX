from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    assert count == 1, f"{path}: expected one match, found {count}: {old[:120]!r}"
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


# README.md
replace_once(
    "README.md",
    "| Live Environment Awareness | **IN PROGRESS — nine bounded exits QUALIFIED**: local runtime (#119/#120), governed Tool Gateway (#122/#123), bound hosted/session cognition awareness (#125/#126), governed bound-remote origin transport freshness (#128/#129), exact bound-remote endpoint-surface freshness (#136/#137), passive supported configured cognition-resource discovery (#140/#141), configured remote cognition connection-policy awareness (#144/#145), configured local llama.cpp readiness awareness (#148/#149), and governed secret-alias availability awareness (#152/#153). Parent #115 remains open; credential validity, authenticated remote provider/service readiness, model quality / Mission-specific fitness, successful cognition semantics, arbitrary/unconfigured provider catalog discovery, broader external-connection/application/process awareness, provider switching/fallback, and adaptive routing remain unqualified. |",
    "| Live Environment Awareness | **IN PROGRESS — ten bounded exits QUALIFIED**: local runtime (#119/#120), governed Tool Gateway (#122/#123), bound hosted/session cognition awareness (#125/#126), governed bound-remote origin transport freshness (#128/#129), exact bound-remote endpoint-surface freshness (#136/#137), passive supported configured cognition-resource discovery (#140/#141), configured remote cognition connection-policy awareness (#144/#145), configured local llama.cpp readiness awareness (#148/#149), governed secret-alias availability awareness (#152/#153), and configured cognition credential-alias binding awareness (#156/#157). Parent #115 remains open; credential validity, authenticated remote provider/service readiness, model quality / Mission-specific fitness, successful cognition semantics, arbitrary/unconfigured provider catalog discovery, broader external-connection/application/process awareness, provider switching/fallback, and adaptive routing remain unqualified. |",
)
replace_once(
    "README.md",
    "- **22/22** current critical-invariant mutations killed; the original Stage 1 qualification remains historically **12/12**, with ten later Live Environment Awareness authority/evidence mutations extending the current matrix;",
    "- **23/23** current critical-invariant mutations killed; the original Stage 1 qualification remains historically **12/12**, with eleven later Live Environment Awareness authority/evidence mutations extending the current matrix;",
)

# docs/architecture/ARCHITECTURE.md
replace_once(
    "docs/architecture/ARCHITECTURE.md",
    "and nine bounded Live Environment Awareness exits qualified: local runtime, governed Tool Gateway capability awareness, already-bound hosted/session cognition awareness, already-bound remote origin transport freshness, already-bound exact endpoint-surface freshness, passive supported configured cognition-resource discovery, configured remote cognition connection-policy awareness, configured local llama.cpp readiness awareness, and governed secret-alias availability awareness.",
    "and ten bounded Live Environment Awareness exits qualified: local runtime, governed Tool Gateway capability awareness, already-bound hosted/session cognition awareness, already-bound remote origin transport freshness, already-bound exact endpoint-surface freshness, passive supported configured cognition-resource discovery, configured remote cognition connection-policy awareness, configured local llama.cpp readiness awareness, governed secret-alias availability awareness, and configured cognition credential-alias binding awareness.",
)
replace_once(
    "docs/architecture/ARCHITECTURE.md",
    "No state automatically implies the next. Current protected source qualifies nine bounded surfaces: defined local runtime awareness (#119/#120), passive governed Tool Gateway capability awareness (#122/#123), awareness of hosted/session cognition already bound to GorXu/Crew seats (#125/#126), explicit current-session **origin transport freshness** for an already-bound remote cognition resource (#128/#129), exact endpoint-surface freshness for that already-bound remote class (#136/#137), passive supported configured cognition-resource discovery (#140/#141), configured remote cognition connection-policy awareness (#144/#145), configured local llama.cpp readiness awareness (#148/#149), and governed secret-alias availability awareness (#152/#153).",
    "No state automatically implies the next. Current protected source qualifies ten bounded surfaces: defined local runtime awareness (#119/#120), passive governed Tool Gateway capability awareness (#122/#123), awareness of hosted/session cognition already bound to GorXu/Crew seats (#125/#126), explicit current-session **origin transport freshness** for an already-bound remote cognition resource (#128/#129), exact endpoint-surface freshness for that already-bound remote class (#136/#137), passive supported configured cognition-resource discovery (#140/#141), configured remote cognition connection-policy awareness (#144/#145), configured local llama.cpp readiness awareness (#148/#149), governed secret-alias availability awareness (#152/#153), and configured cognition credential-alias binding awareness (#156/#157).",
)
replace_once(
    "docs/architecture/ARCHITECTURE.md",
    "The governed secret-alias availability surface is deliberately secret-blind. For one exact alias already represented in the host-injected memory-only `SecretBroker`, it reports only exact alias membership through `has_alias(alias)`. It never enumerates aliases or returns, hashes, compares, persists, logs, transforms, materializes, or validates a secret value; a default empty broker fails closed. It performs no environment/filesystem/keychain scan, network request, provider construction or binding, cognition invocation, or Mission creation. Alias availability never implies Mission authorization, credential validity, readiness, qualification/fit, selection, observation, fallback, or routing.\n\nThe remote transport refresh is deliberately narrow.",
    "The governed secret-alias availability surface is deliberately secret-blind. For one exact alias already represented in the host-injected memory-only `SecretBroker`, it reports only exact alias membership through `has_alias(alias)`. It never enumerates aliases or returns, hashes, compares, persists, logs, transforms, materializes, or validates a secret value; a default empty broker fails closed. It performs no environment/filesystem/keychain scan, network request, provider construction or binding, cognition invocation, or Mission creation. Alias availability never implies Mission authorization, credential validity, readiness, qualification/fit, selection, observation, fallback, or routing.\n\nThe configured credential-alias binding surface is explicit non-secret metadata only. For one valid configured remote `openai` cognition resource, `GROX_REASONER_CREDENTIAL_ALIAS` binds a validated alias name to the exact existing configured cognition resource identity while base discovery continues to omit credential-alias metadata. Missing or malformed aliases fail closed, and `local-llama-cpp` resources are not promoted. The surface does not consult or enumerate `SecretBroker`, check alias availability, read or materialize a secret value, validate credentials, perform network/provider/cognition/Mission activity, authorize work, promote readiness/qualification/selection/observation, perform fallback, or change routing.\n\nThe remote transport refresh is deliberately narrow.",
)

# docs/stewardship/ROADMAP.md
replace_once(
    "docs/stewardship/ROADMAP.md",
    "qualified configured local llama.cpp readiness awareness exit, and qualified governed secret-alias availability awareness exit**.",
    "qualified configured local llama.cpp readiness awareness exit, qualified governed secret-alias availability awareness exit, and qualified configured cognition credential-alias binding awareness exit**.",
)
replace_once(
    "docs/stewardship/ROADMAP.md",
    "- 22 high-consequence production invariants continuously mutation-proven; the original Stage 1 12/12 record remains historical and ten later Live Environment Awareness authority/evidence mutations extend the current matrix.",
    "- 23 high-consequence production invariants continuously mutation-proven; the original Stage 1 12/12 record remains historical and eleven later Live Environment Awareness authority/evidence mutations extend the current matrix.",
)
roadmap = Path("docs/stewardship/ROADMAP.md")
roadmap_text = roadmap.read_text(encoding="utf-8")
assert "configured cognition credential-alias binding awareness exit is QUALIFIED" not in roadmap_text
roadmap_anchor = "\n## Apex critical path\n"
assert roadmap_text.count(roadmap_anchor) == 1
roadmap_bullet = "\n- **Live Environment Awareness configured cognition credential-alias binding awareness exit is QUALIFIED:** issue #156 / PR #157 add explicit non-secret alias metadata binding for one valid configured remote `openai` cognition resource. `GROX_REASONER_CREDENTIAL_ALIAS` is read only through the explicit non-secret configuration allowlist, validated as bounded metadata, and bound to the exact existing configured cognition resource identity without changing that identity or exposing the alias through base discovery. Missing or malformed aliases fail closed; `local-llama-cpp` resources are not promoted. The surface does not consult or enumerate `SecretBroker`, check alias availability, inspect/materialize/validate credential values, perform network/provider/cognition/Mission activity, authorize work, promote readiness/fitness/selection/observation, perform fallback, or change routing. Red-before-green head `0e4eee47716829142dff320f3f006c88a648ce68` produced CI #533 / `32791378003`, failing exactly on the intentionally missing `grox.credential_binding` module while Wheel bootstrap remained green. Final head `199ff6806e73afd799159cd2d77353e01aab90b4` passed exact-head GroX CI #541 / `32818899816` across Wheel + Python 3.11–3.14 after a same-head rerun of one runner-local Python 3.12 Docker isolation anomaly with no source change; successful replacement job `97712960486` recorded Health 10/0/0/0, pytest 417 passed / 2 skipped / 477 subtests, unittest 419 OK / 2 skipped, critical mutations 23/23 plus 7/7 + 9/9 + 4/4 + 6/6 killed, and Post-Apex PASS. Permanent mutation `configured-credential-binding-exact-resource` was killed with source restored clean. Bounded review `5015795391` passed with no threads. CI-tested ready-state synthetic merge `735259e827be9ab428450c868a8833a2a51ce7c7` and guarded canonical merge `main@4401b78e33db964b6789ec42997bc32489ef095a` share exact tree `99c096cfb183044a17318999389ead7d06346868`; exact-tree equality PASS. Credential validity, authenticated remote provider/service readiness, model quality / Mission-specific fitness, successful cognition semantics, arbitrary/unconfigured provider catalogs, broader external-connection/application/process awareness, switching/fallback, and adaptive routing remain unqualified. Parent #115 remains open.\n"
roadmap.write_text(roadmap_text.replace(roadmap_anchor, roadmap_bullet + roadmap_anchor, 1), encoding="utf-8")

# docs/stewardship/ROADMAP_LIVE_ENVIRONMENT_AWARENESS_001.md
replace_once(
    "docs/stewardship/ROADMAP_LIVE_ENVIRONMENT_AWARENESS_001.md",
    "**Status:** ROADMAP-BOUND / IMPLEMENTATION IN PROGRESS / LOCAL-RUNTIME + GOVERNED TOOL GATEWAY + BOUND HOSTED COGNITION + BOUND REMOTE TRANSPORT FRESHNESS + BOUND REMOTE ENDPOINT-SURFACE FRESHNESS + SUPPORTED CONFIGURED COGNITION DISCOVERY + CONFIGURED REMOTE CONNECTION POLICY AWARENESS + CONFIGURED LOCAL LLAMA.CPP READINESS + GOVERNED SECRET-ALIAS AVAILABILITY EXITS QUALIFIED",
    "**Status:** ROADMAP-BOUND / IMPLEMENTATION IN PROGRESS / LOCAL-RUNTIME + GOVERNED TOOL GATEWAY + BOUND HOSTED COGNITION + BOUND REMOTE TRANSPORT FRESHNESS + BOUND REMOTE ENDPOINT-SURFACE FRESHNESS + SUPPORTED CONFIGURED COGNITION DISCOVERY + CONFIGURED REMOTE CONNECTION POLICY AWARENESS + CONFIGURED LOCAL LLAMA.CPP READINESS + GOVERNED SECRET-ALIAS AVAILABILITY + CONFIGURED CREDENTIAL-ALIAS BINDING EXITS QUALIFIED",
)
replace_once(
    "docs/stewardship/ROADMAP_LIVE_ENVIRONMENT_AWARENESS_001.md",
    "Alias availability remains below and separate from Mission authorization, credential validity, readiness, qualification/fit, selection, observation, provider binding, cognition success, fallback, and routing. These exits still do **not** establish",
    "Alias availability remains below and separate from Mission authorization, credential validity, readiness, qualification/fit, selection, observation, provider binding, cognition success, fallback, and routing. Issue #156 / PR #157 additionally qualify **configured cognition credential-alias binding awareness** for one valid configured remote `openai` cognition resource. `GROX_REASONER_CREDENTIAL_ALIAS` is explicit non-secret metadata bound to the exact existing configured cognition resource identity; base discovery continues to omit it. Missing or malformed aliases fail closed and local resources are not promoted. The binding surface does not consult or enumerate `SecretBroker`, check alias availability, inspect/materialize/validate credential values, perform network/provider/cognition/Mission activity, authorize work, or promote readiness/qualification/selection/observation, fallback, or routing. These exits still do **not** establish",
)
replace_once(
    "docs/stewardship/ROADMAP_LIVE_ENVIRONMENT_AWARENESS_001.md",
    "The governed secret-alias availability exit is **QUALIFIED** through issue #152 / PR #153 and establishes only secret-blind exact-alias membership in an already host-injected memory-only broker; it neither materializes nor validates credentials and promotes no later awareness state. Broader issue #115 remains open.",
    "The governed secret-alias availability exit is **QUALIFIED** through issue #152 / PR #153 and establishes only secret-blind exact-alias membership in an already host-injected memory-only broker; it neither materializes nor validates credentials and promotes no later awareness state. The configured cognition credential-alias binding exit is **QUALIFIED** through issue #156 / PR #157 and establishes only explicit non-secret alias metadata bound to the exact configured remote cognition resource identity; it does not consult the broker, prove alias availability, inspect or validate credential values, perform authenticated provider activity, or promote any later awareness state. Broader issue #115 remains open.",
)
doctrine = Path("docs/stewardship/ROADMAP_LIVE_ENVIRONMENT_AWARENESS_001.md")
doctrine_text = doctrine.read_text(encoding="utf-8")
assert "**Configured cognition credential-alias binding qualification evidence:**" not in doctrine_text
assert doctrine_text.rstrip().endswith("This evidence qualifies only exact governed alias availability and does not qualify secret materialization, credential validity, authenticated remote readiness, model quality/Mission fitness, successful cognition semantics, broader catalog/application discovery, switching/fallback, adaptive routing, or any release/package/NCI/Apex/A8 advancement.")
doctrine_block = "\n\n**Configured cognition credential-alias binding qualification evidence:** issue #156 / PR #157 qualified the tenth bounded awareness exit. Red-before-green tests-only head `0e4eee47716829142dff320f3f006c88a648ce68` kept Wheel bootstrap green while Python regression failed exactly on the intentionally missing `grox.credential_binding` module in GroX CI #533 / `32791378003`. Final head `199ff6806e73afd799159cd2d77353e01aab90b4` passed exact-head GroX CI #541 / `32818899816` across Wheel + Python 3.11–3.14 after a same-head rerun of one runner-local Python 3.12 Docker isolation anomaly; no source change was made for that anomaly. Successful replacement Python 3.12 job `97712960486` recorded Health 10/0/0/0, pytest 417 passed / 2 skipped / 477 subtests, unittest 419 OK / 2 skipped, critical mutations 23/23 plus health 7/7, reconstitution 9/9, operational drift 4/4, source provenance 6/6, and Post-Apex PASS. Permanent mutation `configured-credential-binding-exact-resource` was KILLED with source restored clean. Bounded review `5015795391` passed with no review threads. CI-tested ready-state synthetic merge `735259e827be9ab428450c868a8833a2a51ce7c7` and guarded canonical merge `main@4401b78e33db964b6789ec42997bc32489ef095a` share exact tree `99c096cfb183044a17318999389ead7d06346868`; exact-tree equality PASS. This evidence qualifies only explicit non-secret alias metadata bound to the exact configured remote cognition resource identity. Alias availability for that binding, credential validity, authenticated provider/service readiness, model quality/Mission fitness, successful cognition semantics, broader catalog/application discovery, switching/fallback, adaptive routing, and any release/package/NCI/Apex/A8 advancement remain unqualified."
doctrine.write_text(doctrine_text.rstrip() + doctrine_block + "\n", encoding="utf-8")

# docs/stewardship/progress-tracker.md
replace_once(
    "docs/stewardship/progress-tracker.md",
    "**Current verified canonical source after governed secret-alias availability qualification:** `main@8cc67b660bca51002fac0f125e2a7bc76f198599`",
    "**Current verified canonical source after configured cognition credential-alias binding qualification:** `main@4401b78e33db964b6789ec42997bc32489ef095a`",
)
replace_once(
    "docs/stewardship/progress-tracker.md",
    "**Current verified canonical tree:** `b620add8465575cc7695a7cdb5b314a97decfeeb`",
    "**Current verified canonical tree:** `99c096cfb183044a17318999389ead7d06346868`",
)
replace_once(
    "docs/stewardship/progress-tracker.md",
    "**Current verified regression:** Python **3.11–3.14 + Wheel bootstrap PASS**; Python 3.12 Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**; pytest **410 passed, 2 skipped, 473 subtests**; unittest **412 OK, 2 skipped**; mutations **22/22**, **7/7**, **9/9**, **4/4**, **6/6** killed; integrated Post-Apex PASS",
    "**Current verified regression:** Python **3.11–3.14 + Wheel bootstrap PASS**; Python 3.12 Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**; pytest **417 passed, 2 skipped, 477 subtests**; unittest **419 OK, 2 skipped**; mutations **23/23**, **7/7**, **9/9**, **4/4**, **6/6** killed; integrated Post-Apex PASS",
)
replace_once(
    "docs/stewardship/progress-tracker.md",
    "**Current strategic program:** **Native Cognition Independence Program 001 — IMPLEMENTATION IN PROGRESS; NCI-1 + NCI-2 + NCI-3 QUALIFIED; LIVE ENVIRONMENT AWARENESS IN PROGRESS; LOCAL-RUNTIME + GOVERNED TOOL GATEWAY + BOUND HOSTED COGNITION + BOUND REMOTE TRANSPORT FRESHNESS + BOUND REMOTE ENDPOINT-SURFACE FRESHNESS + SUPPORTED CONFIGURED COGNITION DISCOVERY + CONFIGURED REMOTE CONNECTION POLICY AWARENESS + CONFIGURED LOCAL LLAMA.CPP READINESS + GOVERNED SECRET-ALIAS AVAILABILITY EXITS QUALIFIED**",
    "**Current strategic program:** **Native Cognition Independence Program 001 — IMPLEMENTATION IN PROGRESS; NCI-1 + NCI-2 + NCI-3 QUALIFIED; LIVE ENVIRONMENT AWARENESS IN PROGRESS; LOCAL-RUNTIME + GOVERNED TOOL GATEWAY + BOUND HOSTED COGNITION + BOUND REMOTE TRANSPORT FRESHNESS + BOUND REMOTE ENDPOINT-SURFACE FRESHNESS + SUPPORTED CONFIGURED COGNITION DISCOVERY + CONFIGURED REMOTE CONNECTION POLICY AWARENESS + CONFIGURED LOCAL LLAMA.CPP READINESS + GOVERNED SECRET-ALIAS AVAILABILITY + CONFIGURED CREDENTIAL-ALIAS BINDING EXITS QUALIFIED**",
)
replace_once(
    "docs/stewardship/progress-tracker.md",
    "**Next bounded implementation:** **Continue issue #115 beyond the nine qualified bounded exits using the smallest repository-native evidence-backed surface.",
    "**Next bounded implementation:** **Continue issue #115 beyond the ten qualified bounded exits using the smallest repository-native evidence-backed surface.",
)
tracker = Path("docs/stewardship/progress-tracker.md")
tracker_text = tracker.read_text(encoding="utf-8")
tracker_anchor = "\n## Live Environment Awareness — governed secret-alias availability awareness — issue #152 / PR #153\n"
assert tracker_text.count(tracker_anchor) == 1
assert "configured cognition credential-alias binding awareness — issue #156 / PR #157" not in tracker_text
tracker_section = "\n## Live Environment Awareness — configured cognition credential-alias binding awareness — issue #156 / PR #157\n\n**Status: COMPLETE — QUALIFIED — CANONICAL MERGED AND EXACT-TREE VERIFIED.**\n\nQualified boundary:\n\n- applies only to one valid configured remote `openai` cognition resource and one explicitly configured non-secret `GROX_REASONER_CREDENTIAL_ALIAS`;\n- the alias name is validated as bounded metadata and bound to the exact existing configured cognition resource identity without changing that identity;\n- base configured cognition discovery continues to omit credential-alias metadata;\n- missing or malformed aliases fail closed and `local-llama-cpp` resources are not promoted;\n- the surface does not consult or enumerate `SecretBroker`, check alias availability, read/materialize/inspect/validate credential values, perform network/provider/cognition activity, create a Mission, authorize work, promote readiness/qualification/selection/observation, perform fallback, or change routing.\n\nQualification evidence:\n\n- red-before-green tests-only head `0e4eee47716829142dff320f3f006c88a648ce68`: GroX CI #533 / `32791378003` kept Wheel bootstrap green while Python regression failed exactly because `grox.credential_binding` was absent;\n- final PR #157 head `199ff6806e73afd799159cd2d77353e01aab90b4`;\n- exact-head GroX CI #541 / `32818899816`: PASS Wheel + Python 3.11–3.14 after a same-head rerun of one runner-local Python 3.12 Docker isolation anomaly; no source change was made for that anomaly;\n- successful Python 3.12 replacement job `97712960486`: Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**; pytest **417 passed, 2 skipped, 477 subtests**; unittest **419 OK, 2 skipped**; critical mutations **23/23**; health **7/7**; reconstitution **9/9**; operational drift **4/4**; source provenance **6/6**; Post-Apex PASS; source restored clean;\n- permanent mutation `configured-credential-binding-exact-resource`: KILLED;\n- bounded review `5015795391`: PASS with no review threads;\n- CI-tested ready-state synthetic merge `735259e827be9ab428450c868a8833a2a51ce7c7`, tree `99c096cfb183044a17318999389ead7d06346868`;\n- guarded canonical merge `main@4401b78e33db964b6789ec42997bc32489ef095a`, same tree;\n- synthetic-to-canonical tree equality: **PASS**;\n- issue #156 closed completed; parent #115 remains **OPEN**.\n\nStill unqualified: configured-alias availability composition, actual credential validity, authenticated remote provider/service readiness, model quality / Mission-specific fitness, successful cognition semantics, arbitrary/unconfigured provider catalogs, broader authorized external-connection/application/process awareness, provider switching/fallback, and adaptive routing. No release/package/NCI/Apex/A8 advancement occurred.\n"
tracker.write_text(tracker_text.replace(tracker_anchor, tracker_section + tracker_anchor, 1), encoding="utf-8")

# docs/verification/CRITICAL_INVARIANT_MUTATION_MATRIX.md
replace_once(
    "docs/verification/CRITICAL_INVARIANT_MUTATION_MATRIX.md",
    "Protected source later extended the same permanent harness with ten additional high-consequence Live Environment Awareness authority/evidence mutations. The current matrix is therefore **22/22 KILLED**; this extension does not rewrite the original Stage 1 run.",
    "Protected source later extended the same permanent harness with eleven additional high-consequence Live Environment Awareness authority/evidence mutations. The current matrix is therefore **23/23 KILLED**; this extension does not rewrite the original Stage 1 run.",
)
replace_once(
    "docs/verification/CRITICAL_INVARIANT_MUTATION_MATRIX.md",
    "| 22 | Secret-alias availability must remain bound to the exact requested alias rather than any broker secret | replace exact alias membership in `src/grox/tools/secrets.py` with `bool(self._secrets)` | `SecretAliasAwarenessTests.test_absent_alias_fails_closed_without_enumerating_other_aliases` | KILLED |\n",
    "| 22 | Secret-alias availability must remain bound to the exact requested alias rather than any broker secret | replace exact alias membership in `src/grox/tools/secrets.py` with `bool(self._secrets)` | `SecretAliasAwarenessTests.test_absent_alias_fails_closed_without_enumerating_other_aliases` | KILLED |\n| 23 | Configured credential-alias binding must preserve the exact configured cognition resource identity | replace the bound `resource_id` in `src/grox/credential_binding.py` with a different configured-resource identity | `ConfiguredCredentialBindingTests.test_valid_remote_binding_preserves_exact_resource_identity` | KILLED |\n",
)
replace_once(
    "docs/verification/CRITICAL_INVARIANT_MUTATION_MATRIX.md",
    "Latest exact-head evidence is PR #153 CI #523 / `32789939644`: Python 3.12 killed **22/22** critical mutations with zero survivors while all health, reconstitution, operational-drift, source-provenance, and Post-Apex gates remained green. The #16 mutation remains `cognition-transport-presealed-authority`; #17 is `cognition-transport-origin-binding`; #18 is `cognition-endpoint-exact-binding`; #19 is `configured-cognition-discovery-state-separation`; #20 is `configured-connection-exact-resource-binding`; #21 is `configured-local-readiness-authorization-separation`; #22 is `secret-alias-exact-binding`. The original Stage 1 **12/12** qualification remains preserved above as historical evidence.",
    "Latest exact-head evidence is PR #157 CI #541 / `32818899816`: after a same-head rerun of one runner-local Python 3.12 Docker isolation anomaly with no source change, successful replacement job `97712960486` killed **23/23** critical mutations with zero survivors and `source_restored_clean=true` while all health, reconstitution, operational-drift, source-provenance, and Post-Apex gates remained green. The #16 mutation remains `cognition-transport-presealed-authority`; #17 is `cognition-transport-origin-binding`; #18 is `cognition-endpoint-exact-binding`; #19 is `configured-cognition-discovery-state-separation`; #20 is `configured-connection-exact-resource-binding`; #21 is `configured-local-readiness-authorization-separation`; #22 is `secret-alias-exact-binding`; #23 is `configured-credential-binding-exact-resource`. The original Stage 1 **12/12** qualification remains preserved above as historical evidence.",
)

# Hygiene assertions: exact current-state markers, historical Stage 1 preserved.
assert "IN PROGRESS — ten bounded exits QUALIFIED" in Path("README.md").read_text(encoding="utf-8")
assert "Current protected source qualifies ten bounded surfaces" in Path("docs/architecture/ARCHITECTURE.md").read_text(encoding="utf-8")
assert "23 high-consequence production invariants" in Path("docs/stewardship/ROADMAP.md").read_text(encoding="utf-8")
assert "CONFIGURED CREDENTIAL-ALIAS BINDING EXITS QUALIFIED" in Path("docs/stewardship/ROADMAP_LIVE_ENVIRONMENT_AWARENESS_001.md").read_text(encoding="utf-8")
assert "beyond the ten qualified bounded exits" in Path("docs/stewardship/progress-tracker.md").read_text(encoding="utf-8")
mutation_final = Path("docs/verification/CRITICAL_INVARIANT_MUTATION_MATRIX.md").read_text(encoding="utf-8")
assert "mutation proof: **12/12 KILLED**" in mutation_final
assert "current matrix is therefore **23/23 KILLED**" in mutation_final
assert "| 23 | Configured credential-alias binding" in mutation_final
