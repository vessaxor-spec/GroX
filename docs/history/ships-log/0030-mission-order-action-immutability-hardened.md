# Ship's Log — Entry 0030

**Date:** 2026-08-15  
**Pilot:** GorXu  
**Milestone:** MissionOrder action immutability hardening

After the bounded authority and risk-floor remediation, a post-remediation audit identified one remaining defense-in-depth weakness in the Mission Order object itself: `allowed_actions` was still held as a mutable list after construction. Although downstream Gateway policy continued to deny unauthorized mutation, a Mission Order's action grant should not be casually widenable after issuance.

`MissionOrder.allowed_actions` is now snapshotted as an immutable tuple when the Order is constructed. Mutating the caller's original list cannot alter the issued Order, and ordinary post-construction reassignment is rejected. Serialization deliberately preserves the existing external list shape so persisted and inspected Mission Order records remain compatible.

The Tool Gateway's independent deny-wins boundary was preserved rather than made dependent on object immutability. Gateway corruption tests now use an explicit low-level `object.__setattr__` bypass to simulate a deliberately corrupted Order and confirm that non-Repair filesystem mutation is still denied even when a mutation grant is forcibly injected.

GitHub-hosted qualification run `31847315479` on Ubuntu 24.04 / Python 3.12.13 passed the complete suite for that Vessel state: **85 unittest tests with 2 environment-dependent skips**, and **83 pytest tests passed with 2 skipped**. The immutable snapshot, reassignment rejection, and corrupted non-Repair `fs_write` denial tests all passed.

The hardening shipped through PR **#7**, `Harden MissionOrder action immutability`, with branch head `43acf675a525ab85e5c038ac738833d999b04cd0` and merge commit `e1e352d90276cee31f0893a43ab6994c33e21e47`.

No routing, command-spine, Standing Crew, A5 governed-capability architecture, GorXu authority, or verifier-independence changes were introduced. A6 remains the active Apex stage.