from __future__ import annotations
import argparse, json
from pathlib import Path
from .pilot import PilotGorXu
from .contracts import MissionMode, RiskClass
from .persistence import PersistenceManager
from .vessel import resolve_vessel_root

ROOT=resolve_vessel_root(module_file=__file__)

def pilot(): return PilotGorXu(ROOT)

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
    sh=sp.add_parser('show'); sh.add_argument('mission_id')
    m=sp.add_parser('mission'); m.add_argument('directive'); m.add_argument('--mode',choices=[x.value for x in MissionMode]); m.add_argument('--risk',choices=[x.value for x in RiskClass]); m.add_argument('--crew'); m.add_argument('--scope',default='.')
    r=sp.add_parser('repair-write'); r.add_argument('path'); r.add_argument('content'); r.add_argument('--risk',choices=[x.value for x in RiskClass]); r.add_argument('--crew')
    gm=sp.add_parser('graph-mission'); gm.add_argument('directive'); gm.add_argument('--plan',required=True); gm.add_argument('--risk',choices=[x.value for x in RiskClass]); gm.add_argument('--allow-repair',action='store_true'); gm.add_argument('--plan-source',default='commander-seat-plan')
    sn=sp.add_parser('snapshot'); sn.add_argument('--label'); sn.add_argument('--out')
    sv=sp.add_parser('verify-snapshot'); sv.add_argument('path')
    sr=sp.add_parser('restore-snapshot'); sr.add_argument('path'); sr.add_argument('--confirm',action='store_true')
    ns=ap.parse_args(argv)
    if ns.cmd=='snapshot':
        pm=PersistenceManager(ROOT); dump(pm.create_snapshot(label=ns.label,output=Path(ns.out) if ns.out else None).to_dict()); return
    if ns.cmd=='verify-snapshot':
        pm=PersistenceManager(ROOT); dump(pm.verify_snapshot(Path(ns.path)).to_dict()); return
    if ns.cmd=='restore-snapshot':
        pm=PersistenceManager(ROOT); dump(pm.restore_snapshot(Path(ns.path),confirm=ns.confirm)); return
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

if __name__=='__main__': main()