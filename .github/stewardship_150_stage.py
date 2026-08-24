from pathlib import Path


def read(path: str) -> str:
    return Path(path).read_text()


def write(path: str, text: str) -> None:
    Path(path).write_text(text)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one target, found {count}")
    return text.replace(old, new, 1)


# README
p = "README.md"
t = read(p)
t = replace_once(t, "**IN PROGRESS — seven bounded exits QUALIFIED**", "**IN PROGRESS — eight bounded exits QUALIFIED**", "README exit count")
t = replace_once(t, "configured remote cognition connection-policy awareness (#144/#145)", "configured remote cognition connection-policy awareness (#144/#145), and configured local llama.cpp readiness awareness (#148/#149)", "README eighth surface")
t = replace_once(t, "credential validity, authenticated provider/service readiness, model availability/fitness, arbitrary/unconfigured provider catalog discovery, broader external-connection/application/process awareness, and adaptive routing remain unqualified.", "credential validity, authenticated remote provider/service readiness, model quality / Mission-specific fitness, successful cognition semantics, arbitrary/unconfigured provider catalog discovery, broader external-connection/application/process awareness, provider switching/fallback, and adaptive routing remain unqualified.", "README remaining gaps")
t = replace_once(t, "- **20/20** current critical-invariant mutations killed; the original Stage 1 qualification remains historically **12/12**, with eight later Live Environment Awareness authority/evidence mutations extending the current matrix;", "- **21/21** current critical-invariant mutations killed; the original Stage 1 qualification remains historically **12/12**, with nine later Live Environment Awareness authority/evidence mutations extending the current matrix;", "README mutation count")
write(p, t)

# Architecture
p = "docs/architecture/ARCHITECTURE.md"
t = read(p)
t = replace_once(t, "seven bounded Live Environment Awareness exits qualified", "eight bounded Live Environment Awareness exits qualified", "architecture opening count")
t = replace_once(t, "and configured remote cognition connection-policy awareness.", "configured remote cognition connection-policy awareness, and configured local llama.cpp readiness awareness.", "architecture opening list")
t = replace_once(t, "No state automatically implies the next. Current protected source qualifies seven bounded surfaces:", "No state automatically implies the next. Current protected source qualifies eight bounded surfaces:", "architecture surface count")
needle = "configured remote cognition connection-policy awareness (#144/#145)."
t = replace_once(t, needle, "configured remote cognition connection-policy awareness (#144/#145), and configured local llama.cpp readiness awareness (#148/#149).", "architecture qualified list")
marker = "The configured-connection policy-awareness surface is also deliberately non-operational."
idx = t.find(marker)
if idx < 0:
    raise SystemExit("architecture configured-connection paragraph marker missing")
end = t.find("\n\n", idx)
if end < 0:
    raise SystemExit("architecture configured-connection paragraph end missing")
paragraph = "\n\nThe configured-local readiness surface is likewise explicit and non-activating. For one valid supported configured `local-llama-cpp` cognition resource, it reuses the existing GroX model registry/runtime/backend readiness primitives to check exact model registration and artifact integrity, current host constraints, and the exact configured llama.cpp executable against the pinned supported build. The only local process probe is the existing bounded `llama.cpp --version` support check. `ready=True` remains strictly separate from Mission authorization, qualification/fit, selection, and observation; the surface never loads a model, invokes cognition, touches network or credentials, binds a provider, creates a Mission, performs fallback, or changes routing."
t = t[:end] + paragraph + t[end:]
write(p, t)

# Roadmap
p = "docs/stewardship/ROADMAP.md"
t = read(p)
t = replace_once(t, "qualified supported configured cognition-resource discovery exit, and qualified configured remote cognition connection-policy awareness exit**.", "qualified supported configured cognition-resource discovery exit, qualified configured remote cognition connection-policy awareness exit, and qualified configured local llama.cpp readiness awareness exit**.", "roadmap current position")
t = replace_once(t, "- 20 high-consequence production invariants continuously mutation-proven; the original Stage 1 12/12 record remains historical and eight later Live Environment Awareness authority/evidence mutations extend the current matrix.", "- 21 high-consequence production invariants continuously mutation-proven; the original Stage 1 12/12 record remains historical and nine later Live Environment Awareness authority/evidence mutations extend the current matrix.", "roadmap mutation count")
start = t.find("- **Live Environment Awareness configured remote cognition connection-policy awareness exit is QUALIFIED:**")
if start < 0:
    raise SystemExit("roadmap configured-connection qualification bullet missing")
end = t.find("\n- **", start + 5)
if end < 0:
    end = t.find("\n## ", start)
if end < 0:
    raise SystemExit("roadmap configured-connection bullet end missing")
bullet = """
- **Live Environment Awareness configured local llama.cpp readiness awareness exit is QUALIFIED:** issue #148 / PR #149 add explicit non-activating readiness awareness for one valid supported configured `local-llama-cpp` cognition resource. The surface reuses existing `ModelRegistry`, `LocalModelRuntime.readiness()`, and `LlamaCppCLIBackend.supports()` primitives to check exact configured model registration/artifact integrity, host constraints, and the exact configured llama.cpp executable against the pinned supported build. The only local process probe is the existing bounded `llama.cpp --version` support check; no model load, cognition invocation, network/download, credential inspection, provider binding, Mission creation, authorization, qualification/fit, selection, observation, fallback, or routing occurs. Exact-head CI #502 / `32777798243` passed Wheel plus Python 3.11–3.14 on head `575c05ade14a36e664d90e5e7c0a73fb9999cc76`; Python 3.12 recorded Vessel Health 10/0/0/0, pytest 404 passed / 2 skipped / 470 subtests, unittest 406 / 2 skipped, critical mutations 21/21 plus 7/7 + 9/9 + 4/4 + 6/6 killed, and Post-Apex PASS. CI-tested synthetic merge `01f1864410569ab8d45c0e18aa890fa0beb1a954` and guarded canonical merge `main@b477b785104f2931efb22172eea87e22a602346d` share exact tree `3524a24da5b16d90885b10dfbd227e0f019713d2`. The permanent `configured-local-readiness-authorization-separation` mutation was killed. Parent #115 remains open; credential validity, authenticated remote provider/service readiness, model quality / Mission-specific fitness, successful cognition semantics, arbitrary/unconfigured provider catalog discovery, broader external-connection/application/process awareness, provider switching/fallback, and adaptive routing remain unqualified.
"""
t = t[:end] + bullet + t[end:]
write(p, t)

# Live Environment Awareness doctrine
p = "docs/stewardship/ROADMAP_LIVE_ENVIRONMENT_AWARENESS_001.md"
t = read(p)
t = replace_once(t, "**Status:** ROADMAP-BOUND / IMPLEMENTATION IN PROGRESS / LOCAL-RUNTIME + GOVERNED TOOL GATEWAY + BOUND HOSTED COGNITION + BOUND REMOTE TRANSPORT FRESHNESS + BOUND REMOTE ENDPOINT-SURFACE FRESHNESS + SUPPORTED CONFIGURED COGNITION DISCOVERY + CONFIGURED REMOTE CONNECTION POLICY AWARENESS EXITS QUALIFIED", "**Status:** ROADMAP-BOUND / IMPLEMENTATION IN PROGRESS / LOCAL-RUNTIME + GOVERNED TOOL GATEWAY + BOUND HOSTED COGNITION + BOUND REMOTE TRANSPORT FRESHNESS + BOUND REMOTE ENDPOINT-SURFACE FRESHNESS + SUPPORTED CONFIGURED COGNITION DISCOVERY + CONFIGURED REMOTE CONNECTION POLICY AWARENESS + CONFIGURED LOCAL LLAMA.CPP READINESS EXITS QUALIFIED", "doctrine status")
tail = "These exits still do **not** establish ambient application/process scanning, arbitrary tool discovery, arbitrary/unconfigured remote/cloud provider catalog discovery, authenticated provider/service readiness, credential validity, broader authorized external-connection discovery, model existence/availability/fitness, broader operational capability awareness, switching/fallback, or adaptive startup/resource routing."
addition = "Issue #148 / PR #149 additionally qualify **configured local llama.cpp readiness awareness** for one valid supported configured `local-llama-cpp` resource. This explicit readiness surface reuses existing GroX registry/runtime/backend primitives to check exact configured model registration/artifact integrity, host constraints, and the exact configured llama.cpp executable against the pinned supported build. The only local process probe is the bounded existing `llama.cpp --version` support check. `ready=True` remains below and separate from authorization, qualification/fit, selection, and observation; no model load, cognition invocation, provider binding, Mission creation, network/download, credential inspection, fallback, or routing occurs. "
t = replace_once(t, tail, addition + tail, "doctrine canonical readiness boundary")
seq = "Broader issue #115 remains open."
seq_add = "The configured local llama.cpp readiness-awareness exit is **QUALIFIED** through issue #148 / PR #149 and establishes only explicit current non-activating local readiness for one valid supported configured resource using existing registry/runtime/backend checks and the bounded exact executable `--version` probe; authorization, qualification/fit, selection, observation, model activation, cognition invocation, provider binding, fallback, and routing remain separate. "
t = replace_once(t, seq, seq_add + seq, "doctrine sequencing readiness")
marker = "**Configured remote cognition connection-policy awareness qualification evidence:**"
start = t.find(marker)
if start < 0:
    raise SystemExit("doctrine configured-connection evidence marker missing")
nxt = t.find("\n**", start + len(marker))
if nxt < 0:
    nxt = t.find("\n## ", start)
if nxt < 0:
    raise SystemExit("doctrine evidence insertion point missing")
evidence = """
**Configured local llama.cpp readiness awareness qualification evidence:** issue #148 / PR #149 qualified the eighth bounded awareness exit. Red-before-green tests-only head `059211970cd7d70864c2cb25e1a4170c8fbbcba1` kept Wheel green while Python 3.11–3.14 failed only on the intentionally missing `grox.configured_local_readiness` module and Python 3.12 Health remained 10/0/0/0. Final head `575c05ade14a36e664d90e5e7c0a73fb9999cc76` passed exact-head GroX CI #502 / `32777798243` across Wheel + Python 3.11–3.14; Python 3.12 recorded Health 10/0/0/0, pytest 404 passed / 2 skipped / 470 subtests, unittest 406 / 2 skipped, critical mutations 21/21 plus health 7/7, reconstitution 9/9, operational drift 4/4, source provenance 6/6, and Post-Apex PASS. Permanent mutation `configured-local-readiness-authorization-separation` was KILLED. Bounded review `5012611510` passed with no review threads. CI-tested synthetic merge `01f1864410569ab8d45c0e18aa890fa0beb1a954` and guarded canonical merge `main@b477b785104f2931efb22172eea87e22a602346d` share exact tree `3524a24da5b16d90885b10dfbd227e0f019713d2`; exact-tree equality PASS. This evidence qualifies readiness only for the exact supported configured local resource and does not qualify credentials, remote authenticated readiness, model quality/Mission fitness, successful cognition semantics, arbitrary catalog discovery, ambient process scanning, switching/fallback, adaptive routing, or any release/package/NCI/Apex/A8 advancement.
"""
t = t[:nxt] + evidence + t[nxt:]
write(p, t)

# Progress tracker
p = "docs/stewardship/progress-tracker.md"
t = read(p)
t = replace_once(t, "**Current verified canonical source after configured remote cognition connection-policy awareness qualification:** `main@ef88cf34ea6732b65cf2ca461d06076d6af1221b`", "**Current verified canonical source after configured local llama.cpp readiness awareness qualification:** `main@b477b785104f2931efb22172eea87e22a602346d`", "tracker canonical source")
t = replace_once(t, "**Current verified canonical tree:** `1480d54f15a4713a083e53cb7174ed8c6c244adf`", "**Current verified canonical tree:** `3524a24da5b16d90885b10dfbd227e0f019713d2`", "tracker canonical tree")
t = replace_once(t, "**Current verified regression:** Python **3.11–3.14 + Wheel bootstrap PASS**; Python 3.12 Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**; pytest **399 passed, 2 skipped, 470 subtests**; unittest **401 OK, 2 skipped**; mutations **20/20**, **7/7**, **9/9**, **4/4**, **6/6** killed; integrated Post-Apex PASS", "**Current verified regression:** Python **3.11–3.14 + Wheel bootstrap PASS**; Python 3.12 Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**; pytest **404 passed, 2 skipped, 470 subtests**; unittest **406 OK, 2 skipped**; mutations **21/21**, **7/7**, **9/9**, **4/4**, **6/6** killed; integrated Post-Apex PASS", "tracker regression")
t = replace_once(t, "SUPPORTED CONFIGURED COGNITION DISCOVERY + CONFIGURED REMOTE CONNECTION POLICY AWARENESS EXITS QUALIFIED**", "SUPPORTED CONFIGURED COGNITION DISCOVERY + CONFIGURED REMOTE CONNECTION POLICY AWARENESS + CONFIGURED LOCAL LLAMA.CPP READINESS EXITS QUALIFIED**", "tracker strategic status")
old_next = "**Next bounded implementation:** **Continue issue #115 beyond the seven qualified bounded exits using the smallest repository-native evidence-backed surface. Credential validity, authenticated provider/service readiness, model existence/availability/fitness, arbitrary/unconfigured provider catalog discovery, broader authorized external-connection awareness, ambient application/process awareness, provider switching/fallback, and adaptive provider/resource routing remain unqualified; adaptive routing must not outrun those gates.**"
new_next = "**Next bounded implementation:** **Continue issue #115 beyond the eight qualified bounded exits using the smallest repository-native evidence-backed surface. Credential validity, authenticated remote provider/service readiness, model quality / Mission-specific fitness, successful cognition semantics, arbitrary/unconfigured provider catalog discovery, broader authorized external-connection awareness, ambient application/process awareness, provider switching/fallback, and adaptive provider/resource routing remain unqualified; adaptive routing must not outrun those gates.**"
t = replace_once(t, old_next, new_next, "tracker next implementation")
marker = "## Live Environment Awareness — configured remote cognition connection-policy awareness — issue #144 / PR #145"
if t.count(marker) != 1:
    raise SystemExit(f"tracker insertion marker count={t.count(marker)}")
section = """## Live Environment Awareness — configured local llama.cpp readiness awareness — issue #148 / PR #149

**Status: COMPLETE — QUALIFIED — CANONICAL MERGED AND EXACT-TREE VERIFIED.**

Qualified boundary:

- applies only to one valid supported configured `local-llama-cpp` cognition resource already represented by passive configured cognition discovery;
- reuses existing `ModelRegistry`, `LocalModelRuntime.readiness()`, and `LlamaCppCLIBackend.supports()` primitives to check exact configured model registration/artifact integrity, current host constraints, and the exact configured llama.cpp executable against the pinned supported build;
- the only local process probe is the existing bounded `llama.cpp --version` support check;
- no model load, cognition invocation, network/download, credential inspection, provider binding, Mission creation, authorization, qualification/fit, selection, observation, fallback, or routing occurs;
- `ready=True` means only non-activating current local runtime readiness for that exact configured resource; `authorized`, `qualified_fit`, `selected`, and `observed` remain false;
- malformed or missing separated layout, model store, registration, artifact/integrity, executable/build, or host/backend support fails closed.

Qualification evidence:

- red-before-green tests-only head `059211970cd7d70864c2cb25e1a4170c8fbbcba1`: Wheel PASS; Python 3.11–3.14 red only because `grox.configured_local_readiness` was absent while Python 3.12 Health remained 10/0/0/0;
- final PR #149 head `575c05ade14a36e664d90e5e7c0a73fb9999cc76`;
- exact-head GroX CI #502 / `32777798243`: PASS Wheel + Python 3.11–3.14; NCI-3 correctly skipped;
- Python 3.12: Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**; pytest **404 passed, 2 skipped, 470 subtests**; unittest **406 OK, 2 skipped**; critical mutations **21/21**; health **7/7**; reconstitution **9/9**; operational drift **4/4**; source provenance **6/6**; Post-Apex PASS;
- permanent mutation `configured-local-readiness-authorization-separation`: KILLED;
- bounded review `5012611510`: PASS with no review threads;
- CI-tested synthetic merge `01f1864410569ab8d45c0e18aa890fa0beb1a954`, tree `3524a24da5b16d90885b10dfbd227e0f019713d2`;
- guarded canonical merge `main@b477b785104f2931efb22172eea87e22a602346d`, same tree;
- synthetic-to-canonical tree equality: **PASS**;
- issue #148 closed completed; parent #115 remains **OPEN**.

Still unqualified: credential validity, authenticated remote provider/service readiness, model quality / Mission-specific fitness, successful cognition semantics, arbitrary/unconfigured provider catalogs, broader external-connection/application/process awareness, provider switching/fallback, and adaptive routing. No release/package/NCI/Apex/A8 advancement occurred.

"""
t = t.replace(marker, section + marker, 1)
write(p, t)

# Critical invariant mutation matrix
p = "docs/verification/CRITICAL_INVARIANT_MUTATION_MATRIX.md"
t = read(p)
t = replace_once(t, "Protected source later extended the same permanent harness with eight additional high-consequence Live Environment Awareness authority/evidence mutations. The current matrix is therefore **20/20 KILLED**;", "Protected source later extended the same permanent harness with nine additional high-consequence Live Environment Awareness authority/evidence mutations. The current matrix is therefore **21/21 KILLED**;", "mutation matrix extension count")
row20 = "| 20 | Configured remote connection authorization must remain bound to the exact discovered resource identity | disable the exact configured resource-ID mismatch rejection in `src/grox/configured_connection_awareness.py` | `ConfiguredConnectionPolicyAwarenessTests.test_wrong_resource_id_never_authorizes_connection` | KILLED |"
if t.count(row20) != 1:
    raise SystemExit("mutation matrix row20 missing or duplicated")
row21 = "| 21 | Configured local cognition readiness must never imply Mission authorization | change configured-local readiness `authorized` from false to true in `src/grox/configured_local_readiness.py` | `ConfiguredLocalCognitionReadinessTests.test_ready_state_never_implies_authorization` | KILLED |"
t = t.replace(row20, row20 + "\n" + row21, 1)
old_latest = "Latest exact-head evidence is PR #145 CI #491 / `32775200609`: Python 3.12 killed **20/20** critical mutations with zero survivors while all health, reconstitution, operational-drift, source-provenance, and Post-Apex gates remained green. The #16 mutation remains `cognition-transport-presealed-authority`; #17 is `cognition-transport-origin-binding`; #18 is `cognition-endpoint-exact-binding`; #19 is `configured-cognition-discovery-state-separation`; #20 is `configured-connection-exact-resource-binding`. The original Stage 1 **12/12** qualification remains preserved above as historical evidence."
new_latest = "Latest exact-head evidence is PR #149 CI #502 / `32777798243`: Python 3.12 killed **21/21** critical mutations with zero survivors while all health, reconstitution, operational-drift, source-provenance, and Post-Apex gates remained green. The #16 mutation remains `cognition-transport-presealed-authority`; #17 is `cognition-transport-origin-binding`; #18 is `cognition-endpoint-exact-binding`; #19 is `configured-cognition-discovery-state-separation`; #20 is `configured-connection-exact-resource-binding`; #21 is `configured-local-readiness-authorization-separation`. The original Stage 1 **12/12** qualification remains preserved above as historical evidence."
t = replace_once(t, old_latest, new_latest, "mutation latest evidence")
write(p, t)

# Append-only Ship's Log 0067
log = Path("docs/history/ships-log/0067-configured-local-llama-readiness-qualified.md")
if log.exists():
    raise SystemExit("Ship Log 0067 already exists")
log.write_text("""# Ship's Log 0067 — Configured local llama.cpp readiness qualified

**Date:** 2026-08-24

Issue #148 / PR #149 qualified the eighth bounded Live Environment Awareness exit: explicit non-activating readiness awareness for one valid supported configured `local-llama-cpp` cognition resource.

The surface reuses GroX's existing model registry, local runtime readiness, and pinned llama.cpp backend-support primitives. For a valid supported configured local resource it may verify exact registration and artifact integrity, current host constraints, and the exact configured llama.cpp executable against the pinned supported build. The only local process probe is the bounded existing `llama.cpp --version` support check.

Readiness remains a separate state. `ready=True` does not imply Mission authorization, qualification/fit, selection, observation, provider binding, model activation, cognition success, fallback, or routing. The surface performs no model load, cognition invocation, network/download, credential inspection, or Mission creation and fails closed when required local layout/model/backend evidence is absent or invalid.

Qualification evidence is PR #149 final head `575c05ade14a36e664d90e5e7c0a73fb9999cc76`, GroX CI #502 / `32777798243`, Python 3.12 Health 10/0/0/0, pytest 404 passed / 2 skipped / 470 subtests, unittest 406 OK / 2 skipped, critical mutations 21/21, health 7/7, reconstitution 9/9, operational drift 4/4, source provenance 6/6, and Post-Apex PASS. The permanent `configured-local-readiness-authorization-separation` mutation was killed. Bounded review `5012611510` passed with no threads.

CI-tested synthetic merge `01f1864410569ab8d45c0e18aa890fa0beb1a954` and guarded canonical merge `main@b477b785104f2931efb22172eea87e22a602346d` share exact tree `3524a24da5b16d90885b10dfbd227e0f019713d2`; exact-tree equality passed.

Parent issue #115 remains open. Credential validity, authenticated remote provider/service readiness, model quality / Mission-specific fitness, successful cognition semantics, arbitrary/unconfigured provider catalog discovery, broader external-connection/application/process awareness, provider switching/fallback, adaptive routing, and any release/package/NCI/Apex/A8 advancement remain outside this qualification.
""")
