# Standing Crew Roster

**Current released baseline:** GroX `v0.7.1@f7ed57dc9dac2eb9de7857fffb743ecdf27f05f2` / **82 Standing Crew**. Canonical source continues on `main`.

## Company model

GroX operates a standing-company model. Crew are durable organizational identities that sleep between Missions and wake into fresh tour context under bounded Mission Orders from Pilot GorXu.

The current company contains **81 specialist-inspired domain Crew** plus **1 native independent verifier**, for **82 standing dossiers**.

Only source-defined standing dossiers are operational Crew. Retired, archived, removed, or otherwise stale Crew identities are not retained as sleeping operational state. Roster reconstitution purges stale Crew state, Crew-scoped memory, and adaptive performance data that do not belong to the current source-defined company.

Historical Mission, Order, and Evidence records may retain factual references to prior Crew for auditability, but those records are not Crew identities and cannot be routed or reactivated.

## Command boundary

No Crew member is an orchestrator. Pilot GorXu remains the sole operational orchestrator. Crew IDs and titles that claim an `orchestrator` identity are rejected, including retired, archived, backup, legacy, or other semantic variants. Crew may analyze, execute, verify, report blockers, and propose better paths, but may not widen their own authority or establish a parallel command path.

## Division attendance

| Division | Standing Crew |
|---|---:|
| Strategy | 17 |
| Engineering | 14 |
| Intelligence | 13 |
| Assurance | 12 |
| Platform | 10 |
| Physical Systems | 7 |
| Operations | 5 |
| Verification | 3 |
| Systems | 1 |
| **Total** | **82** |

## Standing doctrine

Every domain Crew dossier carries the same Vessel-level invariants:

- serve Commander intent through Pilot GorXu;
- never self-authorize scope or establish a parallel command path;
- separate competence from Mission authority;
- adapt when evidence changes and report materially better or safer paths before affected mutation;
- verify current authoritative sources for time-sensitive domain claims;
- prefer reproducible evidence and explicit uncertainty over unsupported confidence.

## Roster integrity

The company manifest is stored at `configs/crew/company-manifest.json`. Contract tests enforce:

- 81 specialist-inspired Crew are present;
- the native independent verifier is present;
- the orchestration role is not recruited;
- semantic `orchestrator` identity variants are rejected by Crew ID and title;
- retired and archived dossiers cannot enter the active roster;
- stale operational Crew state is purged at reconstitution;
- no duplicate Crew IDs exist;
- the bootstrap architecture overlap has been removed;
- all domain Crew carry native standing orders and risk posture metadata.
