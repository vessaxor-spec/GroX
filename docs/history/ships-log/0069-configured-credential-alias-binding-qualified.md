# Ship's Log 0069 — Configured credential-alias binding qualified

**Date:** 2026-08-25

Issue #156 / PR #157 qualified the tenth bounded Live Environment Awareness exit: explicit non-secret credential-alias binding for one valid configured remote `openai` cognition resource.

`GROX_REASONER_CREDENTIAL_ALIAS` is now part of the explicit non-secret reasoning configuration allowlist. The binding surface validates that alias name as bounded metadata and attaches it to the exact existing configured cognition resource identity without changing that resource identity. Base configured cognition discovery still does not expose credential-alias metadata. Missing or malformed aliases fail closed, and `local-llama-cpp` resources are not promoted into credential-bound remote resources.

This qualification does not consult or enumerate `SecretBroker`, check whether the alias is available, read, materialize, hash, compare, persist, log, transform, or validate any credential value, perform network I/O, construct or bind a provider, invoke cognition, create a Mission, authorize work, promote readiness / qualification / selection / observation, perform fallback, or change routing. Configuration binding is not credential validity or authenticated provider/service readiness.

Red-before-green evidence is tests-only head `0e4eee47716829142dff320f3f006c88a648ce68`: GroX CI #533 / `32791378003` failed exactly on the intentionally missing `grox.credential_binding` module while Wheel bootstrap remained green.

Final PR #157 head `199ff6806e73afd799159cd2d77353e01aab90b4` passed exact-head GroX CI #541 / `32818899816` across Wheel bootstrap and Python 3.11–3.14 after a same-head rerun of one runner-local Python 3.12 Docker isolation anomaly; no source change was made for that anomaly. Successful Python 3.12 replacement job `97712960486` recorded Vessel Health 10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN, pytest 417 passed / 2 skipped / 477 subtests, unittest 419 OK / 2 skipped, critical mutations 23/23, health 7/7, reconstitution 9/9, operational drift 4/4, source provenance 6/6, and Post-Apex PASS. Permanent mutation `configured-credential-binding-exact-resource` was KILLED with source restored clean. Bounded review `5015795391` passed with no review threads.

CI-tested ready-state synthetic merge `735259e827be9ab428450c868a8833a2a51ce7c7` and guarded canonical merge `main@4401b78e33db964b6789ec42997bc32489ef095a` share exact tree `99c096cfb183044a17318999389ead7d06346868`; exact-tree equality passed.

Parent issue #115 remains open. This tenth surface does not establish that the configured binding's alias is presently represented in the broker; that separate exact-alias availability capability was qualified by issue #152 / PR #153. Credential validity, authenticated remote provider/service readiness, model quality / Mission-specific fitness, successful cognition semantics, arbitrary/unconfigured provider catalog discovery, broader authorized external-connection/application/process awareness, provider switching/fallback, adaptive routing, and any release/package/NCI/Apex/A8 advancement remain outside this qualification.
