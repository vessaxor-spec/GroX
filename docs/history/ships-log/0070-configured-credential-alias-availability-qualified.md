# Ship's Log 0070 — Configured credential-alias availability qualified

**Date:** 2026-08-25

Issue #160 / PR #161 qualified the eleventh bounded Live Environment Awareness exit: composition of one valid configured remote `openai` cognition resource's exact non-secret credential-alias binding with exact secret-blind membership of that alias in the already-injected memory-only `SecretBroker`.

`ConfiguredCredentialAliasAvailability` preserves the exact configured resource ID, provider, model, endpoint, and alias metadata, then consults only the already-qualified `SecretAliasAwareness.inspect(alias)` / `SecretBroker.has_alias(alias)` predicate for that exact configured alias. Invalid, unbound, or `local-llama-cpp` bindings fail closed without consulting the broker.

This qualification does not enumerate aliases or read, return, hash, compare, persist, log, transform, materialize, or validate any secret value. It never calls `materialize_env`, performs no network request, constructs or binds no provider, invokes no cognition, creates no Mission, changes no authority, and promotes no readiness, qualification/fit, selection, or observation state. Exact alias membership does not prove that secret material is non-empty, current, valid, or usable, and it does not prove authenticated provider/service readiness or successful cognition. No Pilot API or Tool Gateway network surface was changed by this exit.

Red-before-green evidence is tests-only head `d2d16cc764177b1db50d16fac463b55fef6e32bf`: GroX CI #550 / `32820989293` kept Wheel bootstrap green while Python 3.11–3.14 failed exactly on the intentionally missing `grox.configured_credential_availability` module; Python 3.12 Vessel Health remained 10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN.

Final PR #161 head `ece4d05c3c9e1402968e2047adecaa8e60be7660` passed exact-head GroX CI #555 / `32821385793` across Wheel bootstrap and Python 3.11–3.14. Python 3.12 job `97720097426` recorded Vessel Health 10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN, pytest 421 passed / 2 skipped / 480 subtests, unittest 423 OK / 2 skipped, critical mutations 24/24, health 7/7, reconstitution 9/9, operational drift 4/4, source provenance 6/6, and Post-Apex PASS. Permanent mutation `configured-credential-availability-exact-alias` was KILLED with zero survivors and source restored clean. Bounded review `5016024391` passed with no review threads.

CI-tested ready-state synthetic merge `351bf54b84e57090b7cfc154640b9577c4391530` and guarded canonical merge `main@7ac5b8832d4c6e08a3c545a76c5125818461977f` share exact tree `adc4a4fd512eaa65794e7088c4567a25d65727fa`; exact-tree equality passed.

Parent issue #115 remains open. Actual credential validity, authenticated remote provider/service readiness, model quality / Mission-specific fitness, successful cognition semantics, arbitrary/unconfigured provider catalog discovery, broader authorized external-connection/application/process awareness, provider switching/fallback, adaptive routing, and any release/package/NCI/Apex/A8 advancement remain outside this qualification.
