# Ship's Log — Entry 0036

**Date:** 2026-08-16  
**Milestone:** Retired Crew state purged and reconstitution invariant hardened

## Commander decision

The Commander rejected retention of retired Crew as a sleeping operational risk. GroX will not preserve retired, archived, removed, or otherwise stale Crew identities in operational Crew state merely for continuity.

Historical Mission, Order, and Evidence records may retain factual references to Crew that existed at the time. Those records are audit history, not Crew authority and are not routable identities.

## Evidence and purge

The available private A2 checkpoint contained one stale Crew state row:

- `systems-architect`
- status: `retired`

The mounted private checkpoint was rebuilt after deleting that operational Crew row and vacuuming the SQLite database. Post-purge evidence:

- operational Crew rows: **82**
- retired Crew rows: **0**
- SQLite `PRAGMA integrity_check`: **ok**
- rebuilt inner state SHA-256: `85b30bf98fb083db0db406e9cf8ff44e7006d46f7dbabf75d1c571f803a0f0e8`
- rebuilt archive SHA-256: `6a7bc7ab076a026ac2a9b456ca22fb0bfa35160fb2760e63a7cfd851849aeec4`

## Vessel hardening

The post-Apex operational hardening branch now enforces the same rule during reconstitution:

- only source-defined standing dossiers may enter the active roster;
- retired or archived dossiers in the active dossier directory fail closed;
- Crew IDs or titles that claim an `orchestrator` identity fail closed, including retired, legacy, backup, or hidden-title variants;
- after the current source-defined roster is loaded, stale Crew operational rows are purged;
- Crew-scoped memory and adaptive performance data for stale Crew are purged with the identity;
- historical Mission, Order, and Evidence records remain as inert audit history;
- GorXu remains the sole operational orchestrator.

## Verification

GroX CI run `31933827452` on amendment head `bc1a806b4222c3d5643c846a7ee2f56dcd5ca04b` passed:

- Python 3.11 regression: PASS
- Python 3.12 regression: PASS
- wheel bootstrap portability: PASS
- pytest: **128 passed, 2 skipped**
- unittest: **130 OK, 2 skipped**

No Commander authority, GorXu authority, Division structure, capability grants, routing policy, or Apex qualification semantics were widened by this hardening.
