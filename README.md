# GroX

GroX is an independent, persistent AI command environment built around a clear chain of command:

**Commander → Pilot GorXu → Mission Control → Divisions → Standing Crew**

The Commander provides intent and retains final authority over critical, irreversible, or intent-changing decisions. Pilot GorXu is the primary orchestrator and second-in-command. Mission Control is a GroX-native command system used by GorXu for governance, risk analysis, routing support, verification policy, and operational intelligence. Standing Crew execute bounded Mission Orders under explicit authority and evidence requirements.

This sandbox build provides the first runnable GroX-native Vessel: a Commander Seat CLI, Pilot GorXu orchestration, native Mission Control, persistent Crew roster, bounded tools, durable Mission state, evidence, and independent verification.

## Quick start

```bash
python -m pip install -e .
grox status
grox roster
grox mission "Inspect the Vessel and report readiness" --mode inspect
grox bridge
```
