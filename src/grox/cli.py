from __future__ import annotations
import argparse, json
from pathlib import Path
from .pilot import PilotGorXu
from .contracts import MissionMode, RiskClass
from .health import VesselHealth
from .installation import (
    InstallationError,
    commission_workspace,
    default_workspace,
    workspace_status,
)
from .persistence import PersistenceManager
from .reconstitution import ReconstitutionPlanner
from .vessel import resolve_vessel_root


# Compatibility/test override only. Normal installed operation leaves this null
# so operational root discovery remains lazy and fail-closed.
ROOT: Path | None = None


def vessel_root():
    if ROOT is not None:
        return Path(ROOT).expanduser().resolve()
    return resolve_vessel_root(module_file=__file__)


def pilot(): return PilotGorXu(vessel_root())

def dump(x): print(json.dumps(x,indent=2,default=str))

def status(p):
    ms=p.store.recent_missions(5); states=p.store.crew_states()
    print("GroX Vessel: ONLINE")
    print("Command spine: Commander -> Pilot GorXu -> Divisions -> Standing Crew")
    print(f"Vessel root: {p.root}")
    print(f"Standing Crew: {len(p.roster.all())} | Missions recorded: {len(p.store.recent_missions(1000))}")
    print(f"Cognitive Pilot: {p.cognitive_status}")
    active=[x for x in states if x['status']=='on_duty']; print(f"Crew on duty: {len(active)}")
    if ms: print(f"Last mission: {ms[0]['mission_id']} [{ms[0]['status']}] {ms[0]['directive']}")

def health(json_output=False):
    root=vessel_root()
    report=VesselHealth(root).collect()
    if json_output:
        dump(report.to_dict()); return
    print(f"GroX Vessel health: {report.disposition}")
    print(f"Vessel root: {report.vessel_root}")
    for check in report.checks:
        marker='!' if check.status=='FAIL' else '-' if check.status in {'WARN','UNKNOWN'} else '+'
        print(f"{marker} {check.check_id:24} {check.status:7} {check.detail}")
        if check.recommendation: print(f"  recommendation: {check.recommendation}")

def reconstitution_plan(json_output=False,fresh_host=False,source_changed=False):
    root=vessel_root()
    report=VesselHealth(root).collect()
    plan=ReconstitutionPlanner().plan(report,fresh_host=fresh_host,source_changed=source_changed)
    if json_output:
        dump(plan.to_dict()); return
    print(f"GroX reconstitution plan: {plan.mode.upper()}")
    print(f"Evidence surfaces: {plan.planned_surface_count}/{plan.full_surface_count} | avoided={plan.avoided_surface_count} | structural reduction={plan.structural_reduction_ratio:.1%}")
    print("Reasons:")
    for reason in plan.reasons: print(f"- {reason}")
    print("Load surfaces:")
    for surface in plan.load_surfaces: print(f"- {surface}")

def init_workspace(workspace=None,config_dir=None,non_interactive=False,json_output=False):
    selected=Path(workspace).expanduser() if workspace else None
    if selected is None and not non_interactive:
        suggested=default_workspace()
        response=input(f"Where should GroX establish its dedicated workspace?\n[{suggested}]: ").strip()
        selected=Path(response).expanduser() if response else suggested
    result=commission_workspace(selected,config_dir=Path(config_dir).expanduser() if config_dir else None)
    if json_output:
        dump(result.to_dict()); return
    print(f"GroX workspace foundation: {result.status.upper()}")
    print(f"Workspace: {result.workspace}")
    print(f"Host binding: {result.config_file}")
    print(f"Marker: {result.marker_file}")
    if result.created_directories:
        print(f"Created directories: {', '.join(result.created_directories)}")
    else:
        print("Created directories: none (existing commissioned foundation)")
    print("Operational Pilot startup still requires a valid GroX Vessel source binding in NCI-1A.")

def show_workspace(config_dir=None,json_output=False):
    report=workspace_status(config_dir=Path(config_dir).expanduser() if config_dir else None)
    if json_output:
        dump(report); return
    state="COMMISSIONED" if report['commissioned'] else "NOT COMMISSIONED"
    print(f"GroX workspace: {state}")
    print(f"Workspace: {report['workspace']}")
    print(f"Default workspace: {report['default_workspace']}")
    print(f"Host binding: {report['config_file']}")
    print(f"Marker: {report['marker_file']}")

def bridge(p):
    print("GroX Bridge online. Pilot GorXu standing by. /help for commands; /exit to leave.")
    while True:
        try: line=input("Commander> ").strip()
        except (EOFError,KeyboardInterrupt): print(); break
        if not line: continue
        if line in {'/exit','/quit'}: break
        if line=='/help': print("/status /roster /missions /show <id> /exit | plain text = Mission directive"); continue
        if line=='/status': status(p); continue
        if line=='/roster':
            for d,s in zip(p.roster.all(),[]): pass
            states={x['crew_id']:x for x in p.store.crew_states()}
            for d in p.roster.all(): print(f"{d.crew_id:30} {d.division:14} {states[d.crew_id]['status']:8} tours={states[d.crew_id]['tours']}")
            continue
        if line=='/missions':
            for m in p.store.recent_missions(): print(f"{m['mission_id']} {m['status']:20} {m['directive']}")
            continue
        if line.startswith('/show '): dump(p.store.mission(line.split(maxsplit=1)[1])); continue
        dump(p.command(line))

def main(argv=None):
    ap=argparse.ArgumentParser(prog='grox'); sp=ap.add_subparsers(dest='cmd')
    sp.add_parser('status'); sp.add_parser('roster'); sp.add_parser('missions'); sp.add_parser('bridge')
    init=sp.add_parser('init'); init.add_argument('--workspace'); init.add_argument('--config-dir'); init.add_argument('--non-interactive',action='store_true'); init.add_argument('--json',action='store_true',dest='json_output')
    ws=sp.add_parser('workspace'); ws.add_argument('--config-dir'); ws.add_argument('--json',action='store_true',dest='json_output')
    he=sp.add_parser('health'); he.add_argument('--json',action='store_true',dest='json_output')
    rp=sp.add_parser('reconstitution-plan'); rp.add_argument('--json',action='store_true',dest='json_output'); rp.add_argument('--fresh-host',action='store_true'); rp.add_argument('--source-changed',action='store_true')
    sh=sp.add_parser('show'); sh.add_argument('mission_id')
    m=sp.add_parser('mission'); m.add_argument('directive'); m.add_argument('--mode',choices=[x.value for x in MissionMode]); m.add_argument('--risk',choices=[x.value for x in RiskClass]); m.add_argument('--crew'); m.add_argument('--scope',default='.')
    r=sp.add_parser('repair-write'); r.add_argument('path'); r.add_argument('content'); r.add_argument('--risk',choices=[x.value for x in RiskClass]); r.add_argument('--crew')
    gm=sp.add_parser('graph-mission'); gm.add_argument('directive'); gm.add_argument('--plan',required=True); gm.add_argument('--risk',choices=[x.value for x in RiskClass]); gm.add_argument('--allow-repair',action='store_true'); gm.add_argument('--plan-source',default='commander-seat-plan')
    sn=sp.add_parser('snapshot'); sn.add_argument('--label'); sn.add_argument('--out')
    sv=sp.add_parser('verify-snapshot'); sv.add_argument('path')
    sr=sp.add_parser('restore-snapshot'); sr.add_argument('path'); sr.add_argument('--confirm',action='store_true')
    ns=ap.parse_args(argv)
    try:
        if ns.cmd=='init': init_workspace(ns.workspace,ns.config_dir,ns.non_interactive,ns.json_output); return
        if ns.cmd=='workspace': show_workspace(ns.config_dir,ns.json_output); return
        if ns.cmd=='health': health(ns.json_output); return
        if ns.cmd=='reconstitution-plan': reconstitution_plan(ns.json_output,ns.fresh_host,ns.source_changed); return
        if ns.cmd=='snapshot':
            pm=PersistenceManager(vessel_root()); dump(pm.create_snapshot(label=ns.label,output=Path(ns.out) if ns.out else None).to_dict()); return
        if ns.cmd=='verify-snapshot':
            pm=PersistenceManager(vessel_root()); dump(pm.verify_snapshot(Path(ns.path)).to_dict()); return
        if ns.cmd=='restore-snapshot':
            pm=PersistenceManager(vessel_root()); dump(pm.restore_snapshot(Path(ns.path),confirm=ns.confirm)); return
        p=pilot()
        if ns.cmd in (None,'bridge'): bridge(p); return
        if ns.cmd=='status': status(p); return
        if ns.cmd=='roster':
            states={x['crew_id']:x for x in p.store.crew_states()}
            for d in p.roster.all(): print(f"{d.crew_id:30} {d.division:14} {states[d.crew_id]['status']:8} tours={states[d.crew_id]['tours']} caps={','.join(sorted(d.capabilities))}")
        elif ns.cmd=='missions': dump(p.store.recent_missions())
        elif ns.cmd=='show': dump(p.store.mission(ns.mission_id))
        elif ns.cmd=='mission': dump(p.command(ns.directive,mode=MissionMode(ns.mode) if ns.mode else None,risk=RiskClass(ns.risk) if ns.risk else None,crew_id=ns.crew,scope=ns.scope))
        elif ns.cmd=='repair-write': dump(p.repair_write(ns.path,ns.content,risk=RiskClass(ns.risk) if ns.risk else None,crew_id=ns.crew))
        elif ns.cmd=='graph-mission':
            plan=json.loads(Path(ns.plan).read_text())
            dump(p.command_graph(ns.directive,plan=plan,risk=RiskClass(ns.risk) if ns.risk else None,allow_repair=ns.allow_repair,plan_source=ns.plan_source))
    except InstallationError as exc:
        ap.error(str(exc))

if __name__=='__main__': main()
