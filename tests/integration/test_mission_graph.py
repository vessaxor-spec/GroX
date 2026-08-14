import json
import unittest

from grox.contracts import TourResult
from grox.pilot import PilotGorXu
from grox.runtime.executor import CrewExecutor
from tests._support import temp_vessel

EXTRA_CREW=[
    {'crew_id':'researcher','division':'intelligence','title':'Researcher','capabilities':['repo_read','analysis'], 'tags':['research','evidence']},
    {'crew_id':'data-analyst','division':'intelligence','title':'Data Analyst','capabilities':['repo_read','analysis'], 'tags':['data','analysis']},
    {'crew_id':'application-security-engineer','division':'assurance','title':'Application Security Engineer','capabilities':['repo_read','analysis','verify'], 'tags':['security','authority'], 'verification':True},
    {'crew_id':'platform-engineer','division':'platform','title':'Platform Engineer','capabilities':['repo_read','analysis'], 'tags':['platform','runtime']},
]


def graph_vessel():
    td,root,_=temp_vessel()
    for d in EXTRA_CREW:
        (root/'configs/crew/dossiers'/f"{d['crew_id']}.json").write_text(json.dumps(d))
    return td,root,PilotGorXu(root,reasoner=None)


def qualification_plan(directive):
    return {
        'commander_intent': directive,
        'objective': 'Perform a multi-domain Vessel readiness inspection and independently verify the combined evidence.',
        'rationale': 'Run independent branches in parallel, converge after architecture, then verify all branch evidence.',
        'budget': {'max_nodes': 12, 'max_parallel': 3, 'max_replans': 2},
        'nodes': [
            {'node_id':'architecture','objective':'Inspect architecture and command boundaries','mode':'inspect','dependencies':[],
             'candidate_crew_ids':['systems-architect'],'required_capabilities':['repo_read'],'scope':['.']},
            {'node_id':'research','objective':'Research internal evidence and readiness records','mode':'inspect','dependencies':[],
             'candidate_crew_ids':['researcher'],'required_capabilities':['repo_read'],'scope':['docs']},
            {'node_id':'analysis','objective':'Analyze configuration and evidence structure','mode':'inspect','dependencies':[],
             'candidate_crew_ids':['data-analyst'],'required_capabilities':['repo_read'],'scope':['configs']},
            {'node_id':'implementation','objective':'Inspect runtime implementation against architecture','mode':'inspect','dependencies':['architecture'],
             'candidate_crew_ids':['backend-engineer'],'required_capabilities':['repo_read'],'scope':['.']},
            {'node_id':'security','objective':'Inspect authority and security boundaries','mode':'inspect','dependencies':['architecture'],
             'candidate_crew_ids':['application-security-engineer'],'required_capabilities':['repo_read'],'scope':['.']},
            {'node_id':'verify','objective':'Independently verify all completed branch evidence','mode':'verify',
             'dependencies':['implementation','research','analysis','security'],
             'candidate_crew_ids':['code-reviewer'],'required_capabilities':['repo_read','verify'],'scope':['.'],
             'parameters':{'run_tests':True}},
        ],
    }


class FailCrewOnce:
    def __init__(self, base: CrewExecutor, crew_id: str):
        self.base=base; self.crew_id=crew_id; self.failed=False
    def execute(self, order):
        if order.assigned_crew==self.crew_id and not self.failed:
            self.failed=True
            return TourResult(order.order_id,order.assigned_crew,'exception','Injected Crew availability failure',[],
                              {'type':'crew_unavailable','message':'injected A2 qualification failure'})
        return self.base.execute(order)


class MissionGraphIntegrationTests(unittest.TestCase):
    def test_coordinates_multi_stage_parallel_graph(self):
        td,root,p=graph_vessel()
        try:
            directive='Inspect the Vessel across architecture, research, data, implementation, and security, then verify the combined result.'
            r=p.command_graph(directive,plan=qualification_plan(directive),plan_source='test-cognition')
            self.assertEqual(r['status'],'completed')
            self.assertTrue(r['synthesis']['verification_passed'])
            self.assertGreaterEqual(len(r['synthesis']['crew_used']),6)
            self.assertEqual(r['synthesis']['replans'],0)
            mission=p.store.mission(r['mission_id'])
            self.assertEqual(len(mission['graph_nodes']),6)
            self.assertTrue(any(e['event_type']=='batch_started' for e in mission['graph_events']))
            self.assertTrue(any(e['kind']=='pilot_synthesis' for e in mission['evidence']))
        finally: td.cleanup()

    def test_injected_crew_failure_is_replanned_without_commander(self):
        td,root,p=graph_vessel()
        try:
            p.executor=FailCrewOnce(p.executor,'researcher')
            directive='Inspect the Vessel across architecture, research, data, implementation, and security, then verify the combined result.'
            r=p.command_graph(directive,plan=qualification_plan(directive),plan_source='test-cognition')
            self.assertEqual(r['status'],'completed')
            self.assertEqual(r['synthesis']['replans'],1)
            self.assertTrue(r['synthesis']['verification_passed'])
            self.assertGreaterEqual(len(r['synthesis']['crew_used']),6)
            mission=p.store.mission(r['mission_id'])
            replans=[e for e in mission['graph_events'] if e['event_type']=='pilot_replan']
            self.assertEqual(len(replans),1)
            nodes={n['node_id']:n for n in mission['graph_nodes']}
            self.assertEqual(nodes['research']['status'],'replanned')
            recovery=[ˆ›Üˆˆ[ˆ›Ù\ÈYˆ‹œİ\İÚ]
	Ü™\ÙX\˜Ú×Ü™\[‰ÊWBˆÙ[‹˜\ÜÙ\\]X[
[Š™XÛİ™\JKJBˆÙ[‹˜\ÜÙ\\]X[
›Ù\ÖÜ™XÛİ™\VÌWVÉÜİ]\É×K	ØÛÛ\]Y	ÊBˆš[˜[Nˆ˜ÛX[\

B‚ˆYˆ\İÙÜ˜\Ü™\Z\—Ü™\]Z\™\×Ù^XÚ]Û]]][Û—Ø]]Üš]JÙ[ŠN‚ˆ›ÛİYÜ˜\İ™\ÜÙ[

BˆN‚ˆ\™Xİ]™OIÔ™\Z\ˆH›İ[™Y™XÛÜ™›İYÚHZ\ÜÚ[ÛˆÜ˜\‰Âˆ[^Âˆ	ØÛÛ[X[™\—Ú[[	Î™\™Xİ]™K	ÛØš™Xİ]™IÎ‰Ü™\Z\‰Ë	Û›Ù\ÉÎ–ŞÂˆ	Û›ÙWÚY	Î‰Ü™\Z\‰Ë	ÛØš™Xİ]™IÎ‰Ü™\Z\ˆ™XÛÜ™	Ë	Û[ÙIÎ‰Ü™\Z\‰Ë	Ù\[™[˜ÚY\ÉÎ–×Kˆ	ØØ[™Y]WØÜ™]×ÚYÉÎ–ÉØ˜XÚÙ[™Y[™Ú[™Y\‰×K	Ü™\]Z\™YØØ\Xš[]Y\ÉÎ–ÉÜ™\×Ü™XY	Ë	Ü™\×İÜš]I×Kˆ	ÜØÛÜIÎ–ÉÔ‘PQQK›Y	×K	Ü\˜[Y]\œÉÎÉÛÜ\˜][Û‰Î‰İÜš]Wİ^	Ë	Ü]	Î‰Ô‘PQQK›Y	Ë	ØÛÛ[	Î‰Ş	ßBˆWBˆBˆ\˜ÛÛ[X[™ÙÜ˜\
\™Xİ]™K[\[ŠBˆÙ[‹˜\ÜÙ\\]X[
–ÉÜİ]\É×K	Û™YY×Ü[İÙXÚ\Ú[Û‰ÊBˆÙ[‹˜\ÜÙ\[Š	Ù^XÚ][İ]]][Ûˆ]]Üš^˜][Û‰Ë–ÉÜİ[[X\I×JBˆš[˜[Nˆ˜ÛX[\

B