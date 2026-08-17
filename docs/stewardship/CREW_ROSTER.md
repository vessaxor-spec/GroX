# Standing Crew Roster

**Current released baseline:** GroX `v0.7.1@f7ed57dc9dac2eb9de7857fffb743ecdf27f05f2` / **82 Standing Crew**. Canonical source continues on `main`.

## Company model

GroX operates a standing-company model. Crew are durable organizational identities that sleep between Missions and wake into fresh tour context under bounded Mission Orders from Pilot GorXu.

The current company contains **81 specialist-inspired domain Crew** plus **1 native independent verifier**, for **82 Standing Crew**.

Standing Crew identity has two deliberately separate canonical layers:

- `configs/crew/dossiers/<crew_id>.json` is the machine-readable operational dossier. It defines active roster membership, Division, title, capability eligibility, routing tags, verification eligibility, risk posture where present, standing status, and bounded domain/skill metadata used to make deterministic routing more descriptive.
- `configs/crew/specialists/<crew_id>.md` is the canonical craft specification. It defines the Crew member's deep professional identity, purpose, domain context, responsibilities, non-responsibilities and handoffs, inputs, outputs, safety boundaries, operating protocols, collaboration patterns, examples, freshness posture, and GroX operational binding.

The split is intentional. A craft card makes a Crew member a meaningful specialist; it does **not** grant capabilities, Mission authority, Repair permission, routing priority, or command authority. Those remain governed by the existing GroX runtime and active Mission Order.

Only source-defined standing dossiers are operational Crew. Retired, archived, removed, or otherwise stale Crew identities are not retained as sleeping operational state. Roster reconstitution purges stale Crew state, Crew-scoped memory, and adaptive performance data that do not belong to the current source-defined company.

Historical Mission, Order, and Evidence records may retain factual references to prior Crew for auditability, but those records are not Crew identities and cannot be routed or reactivated.

## Craft source and adaptation

The 81 specialist-inspired craft cards are full-depth adaptations of the matching specialist cards from `vessaxor-spec/The-ever-evolving-orchestration-`, pinned to source revision `fab4cb1d16e6ed210bdf5555d8fbbe45a609e415` for the craft Repair.

The adaptation rule is preservation-first:

- retain the detailed specialist craft rather than compressing it into routing labels;
- preserve source provenance in each card, including source revision, source path, and source-content SHA-256;
- remove source-only allocation/routing sections rather than importing an external command model;
- rewrite forbidden orchestration handoffs through Pilot GorXu;
- add missing structural headings where a source card expresses equivalent depth without that exact heading;
- add GroX-native command, authority, mutation, exception, verification, and freshness boundaries;
- never recruit `agents-orchestrator` or another orchestrator-like Crew identity.

The source cards are inputs to the craft Repair, not a runtime dependency. GroX owns the materialized craft library in `configs/crew/specialists/`.

The native `independent-verifier` card is authored directly for GroX at equivalent depth. It explicitly defines verifier independence, attributable evidence, PASS/FAIL rules, non-self-activation, verify-only read-only behavior, and the rule that an executor cannot satisfy an independent-verification requirement with its own PASS.

## Command boundary

No Crew member is an orchestrator. Pilot GorXu remains the sole operational orchestrator. Crew IDs and titles that claim an `orchestrator` identity are rejected, including retired, archived, backup, legacy, or other semantic variants.

Crew may analyze, execute, verify, report blockers, and propose materially better or safer paths. They may not widen their own authority, self-deploy collaborators, create Repair authority from natural-language instruction, self-activate from evaluation findings, or establish a parallel command path. A blocker, safer path, missing capability, elevated risk, scope change, or irreversible consequence is reported to GorXu before the affected mutation.

`incident-commander` remains a domain incident-response role only. Its title does not supersede the human Commander or GorXu's Vessel command authority. `orchestration-evaluation-analyst` may evaluate orchestration evidence but cannot activate its own recommendations.

## Runtime use

`CrewRoster` remains dossier-first. Its existing selection path uses dossier capabilities, tags, verification eligibility, and forbidden-command checks.

For an already active Standing Crew identity, `CrewRoster.craft_card(crew_id)` provides read-only access to the matching canonical craft specification. The lookup first requires the Crew ID to exist in the active roster. Reading a craft card therefore cannot create a new Crew member, bypass dossier eligibility, add capabilities, or authorize mutation.

The runtime should retrieve craft depth when the specialist's actual methods, boundaries, protocols, or handoffs are relevant. It should not indiscriminately inject the entire 82-card library into every Mission context.

## Dossier metadata contract

Machine-readable dossiers carry three distinct kinds of descriptive metadata:

- `domains` mirrors the matching canonical craft card's declared domain list exactly;
- `skills` retains any existing skill labels and includes the declared craft domains for inspectable specialist coverage;
- `tags` retains existing routing tags and adds normalized terms derived from declared craft domains for deterministic objective matching.

These fields are descriptive and routing-supporting, not authority-bearing. In particular:

- **capabilities remain the eligibility gate** for actions and required capability selection;
- `domains`, `skills`, and `tags` cannot add a capability, create Repair permission, widen a Mission Order, grant verification eligibility, or create command authority;
- deterministic selection may use `tags` only after required capability eligibility is satisfied;
- metadata enrichment must preserve existing tags rather than silently replacing prior routing vocabulary;
- each dossier's `domains` must remain attributable to its matching canonical craft card rather than being invented independently;
- routing regression tests must remain green when dossier tags change.

This keeps the machine dossier useful when inspected on its own without duplicating the full craft card or turning descriptive competence into authority.

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

Every Standing Crew member inherits the same Vessel-level invariants regardless of craft:

- serve Commander intent through Pilot GorXu;
- never self-authorize scope or establish a parallel command path;
- separate competence from Mission authority;
- inspection, analysis, memory, evaluation, and natural-language requests do not create mutation authority;
- adapt when evidence changes and report materially better or safer paths before affected mutation;
- verify current authoritative sources for time-sensitive domain claims;
- prefer reproducible evidence and explicit uncertainty over unsupported confidence;
- preserve independent verification where policy requires it.

## Roster and craft integrity

The company manifest is stored at `configs/crew/company-manifest.json`. Contract tests enforce:

- 81 specialist-inspired Crew plus the native independent verifier are present;
- all 82 active dossier stems have exactly one matching canonical craft card;
- the orchestration role is not recruited and `agents-orchestrator` does not leak into craft handoffs;
- semantic `orchestrator` identity variants are rejected by Crew ID and title;
- retired and archived dossiers cannot enter the active roster;
- stale operational Crew state is purged at reconstitution;
- no duplicate Crew IDs exist;
- every craft card contains the required specialist structure and a non-placeholder depth floor;
- all specialist-inspired cards retain pinned source provenance;
- every card carries GroX operational binding that leaves capability and authority with the existing runtime;
- every dossier carries craft-attributable domain metadata with non-thin skills and routing tags;
- metadata enrichment preserves capability gating and the established domain-routing contract;
- the independent verifier card preserves verifier independence and cannot self-activate;
- `CrewRoster` still loads dossiers while craft retrieval remains additive and read-only.
