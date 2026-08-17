from pathlib import Path

ROOT = Path('.')

REPLACEMENTS = {
    'configs/crew/company-manifest.json': [
        ('including retired, archived, backup, legacy, or other semantic variants.', 'including stale, archived, backup, legacy, or other semantic variants.'),
        ('stale, retired, archived, or removed Crew operational state', 'stale, archived, removed, or otherwise non-standing Crew operational state'),
    ],
    'src/grox/crew/roster.py': [
        ('as retired-orchestrator, backup-orchestrator, or a hidden Orchestrator title.', 'as stale-orchestrator, backup-orchestrator, or a hidden Orchestrator title.'),
    ],
    'tests/contracts/test_command_spine.py': [
        ("('retired-orchestrator', 'Analyst'),", "('stale-orchestrator', 'Analyst'),"),
        ("('ordinary-analyst', 'Retired Orchestrator'),", "('ordinary-analyst', 'Stale Orchestrator'),"),
        ("for status in ('retired', 'archived'):", "for status in ('stale', 'archived'):"),
        ("UPDATE crew_state SET status='retired' WHERE crew_id='test-architecture-specialist'", "UPDATE crew_state SET status='stale' WHERE crew_id='test-architecture-specialist'"),
    ],
    'docs/stewardship/CREW_ROSTER.md': [
        ('Retired, archived, removed, or otherwise stale Crew identities', 'Non-standing, archived, removed, or otherwise stale Crew identities'),
        ('including retired, archived, backup, legacy, or other semantic variants.', 'including stale, archived, backup, legacy, or other semantic variants.'),
        ('retired and archived dossiers cannot enter the active roster;', 'non-standing and archived dossiers cannot enter the active roster;'),
    ],
    'docs/stewardship/EXTERNAL_CAPABILITY_INTAKE.md': [
        ('Sleeping retired Crew identities', 'Sleeping non-standing Crew identities'),
    ],
    'docs/stewardship/OPERATIONAL_AUDIT_001.md': [
        ('zero retired operational Crew', 'source-defined operational Crew only'),
    ],
    'docs/history/ships-log/0020-full-company-recruited.md': [
        ('The original bootstrap Systems Architect overlap was retired in favor of the canonical Architect Crew.', 'The original bootstrap Systems Architect overlap was removed in favor of the canonical Architect Crew.'),
    ],
    'docs/history/ships-log/0037-v0.7.1-operational-hardening-release.md': [
        ('retired operational Crew: **0**', 'non-standing operational Crew retained: **0**'),
        ('retired/archive dossier rejection', 'non-standing/archive dossier rejection'),
        ('cannot restore retired Crew authority', 'cannot restore non-standing Crew authority'),
    ],
    'docs/history/ships-log/0038-operational-audit-001-governance-closed.md': [
        ('zero-retired-Crew operational state', 'source-defined-only Crew operational state'),
    ],
    'docs/history/ships-log/0038-post-release-operational-audit.md': [
        ('with no retired Crew', 'with no non-standing Crew retained'),
    ],
    'docs/history/ships-log/0039-post-apex-evolution-program-001-approved.md': [
        ('retain retired Crew as sleeping operational identities;', 'retain non-standing Crew as sleeping operational identities;'),
        ('because ClaudX retired a similarly named role;', 'because ClaudX removed a similarly named role;'),
    ],
    'docs/history/ships-log/0040-external-capability-intake-formalized.md': [
        ('sleeping retired identities', 'sleeping non-standing identities'),
    ],
}

for rel, replacements in REPLACEMENTS.items():
    path = ROOT / rel
    text = path.read_text(encoding='utf-8')
    for old, new in replacements:
        if old not in text:
            raise SystemExit(f'missing expected phrase in {rel}: {old!r}')
        text = text.replace(old, new)
    path.write_text(text, encoding='utf-8')

# Remove the diagnostic workflow from the final candidate.
scan = ROOT / '.github/workflows/tmp-obsolete-crew-scan.yml'
if scan.exists():
    scan.unlink()
