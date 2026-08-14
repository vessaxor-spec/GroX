# Ship's Log — Entry 0028

**Date:** 2026-08-14  
**Pilot:** GorXu  
**Milestone:** A5 Governed Capability Expansion qualified

The Vessel crossed the fifth Apex gate without handing raw host authority to the Crew.

Tool Gateway v2 now governs isolated workspace execution, memory-only secret aliases, exact-origin network access, offline Chromium evidence capture, and pre-registered stdio MCP adapters. Capability remains distinct from permission: every privileged action must intersect the Mission Order, Crew competence, host policy, operation-specific grants, evidence, and independent verification.

Fresh GitHub-hosted qualification passed **65/65** tests. The Ubuntu runner denied the preferred user-namespace `uid_map` operation, and that red canary was preserved as evidence. GorXu used the stronger commissioned Docker fallback instead: no network, all Linux capabilities dropped, `no-new-privileges`, read-only root, bounded resources, digest-pinned/pre-provisioned images, and no runtime image acquisition. Browser networking remained separated from browser rendering; Gateway-approved HTML was rendered offline and screenshot/hash evidence returned.

Live private-Vessel Mission `MSN-5c3b646ce6be` then exercised five governed nodes across `devops-engineer`, `researcher`, `platform-engineer`, and `independent-verifier`. The workspace secret was redacted, absent from durable Mission and SQLite state, and the workspace was destroyed after the tour. Network access remained exact-origin gated, browser-originated networking was disabled, an unapproved origin was blocked, the read-only MCP adapter completed under explicit grants, and independent verification closed PASS.

The Mission completed with **0 replans**, **0 exceptions**, and **0 resumes**. All **82** Standing Crew remained present and private SQLite integrity remained `ok`.

A5 is qualified. GorXu is not yet Apex. The next critical stage is A6: Orchestration Intelligence and Self-Improvement.
