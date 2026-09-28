import unittest
from mcdraft.column_personality import snapshot, tendency_lines, integrate_writer, brand_column


class ColumnPersonalityTests(unittest.TestCase):
    def setUp(self):
        self.profiles={'Alpha': {'tags':[{'name':'Bench Museum Curator'}], 'bench_per_gw':9.5},
                       'Beta': {'tags':[{'name':'Waiver Hawk'}], 'activity_per_gw':1.2}}
        self.matches=[dict(event=3,entry_1_name='Alpha',entry_2_name='Beta',entry_1_points=44,entry_2_points=40)]

    def test_implicit_tendencies_with_evidence(self):
        text=' '.join(tendency_lines(3,'completed',self.profiles,self.matches))
        self.assertIn('9.5',text)
        self.assertIn('1.2',text)
        self.assertIn('44–40',text)
        self.assertNotIn('Bench Museum Curator',text)
        self.assertNotIn('Waiver Hawk',text)
        self.assertEqual(text,' '.join(tendency_lines(3,'completed',self.profiles,self.matches)))

    def test_no_retroactive_profiles(self):
        store={}
        snapshot(store,10,3,self.profiles)
        self.profiles['Alpha']['bench_per_gw']=99
        snapshot(store,10,3,self.profiles)
        self.assertEqual(store['weeks']['3']['Alpha']['bench_per_gw'],9.5)
        wrapped=integrate_writer(lambda gw,phase:[],store['weeks'],self.profiles,self.matches)
        self.assertEqual(wrapped(2,'completed'),[])
        self.assertIn('9.5',' '.join(wrapped(3,'completed')))
        self.assertIn('99.0',' '.join(wrapped(3,'upcoming')))

    def test_preview_never_claims_result(self):
        text=' '.join(tendency_lines(3,'upcoming',self.profiles,self.matches))
        self.assertNotIn('44–40',text)
        self.assertNotIn('This week brought',text)

    def test_unknown_tags_missing_metrics_and_other_fixtures(self):
        self.assertEqual(tendency_lines(4,'completed',self.profiles,self.matches),[])
        self.assertEqual(tendency_lines(3,'completed',{'Alpha':{'tags':[{'name':'Unknown'}]}},self.matches),[])
        del self.profiles['Alpha']['bench_per_gw']
        self.assertNotIn('Alpha',' '.join(tendency_lines(3,'completed',self.profiles,self.matches)))

    def test_new_league_or_season_resets_snapshots(self):
        store={}
        snapshot(store,10,5,self.profiles)
        snapshot(store,10,1,self.profiles)
        self.assertEqual(list(store['weeks']),['1'])
        snapshot(store,11,2,self.profiles)
        self.assertEqual(list(store['weeks']),['2'])

    def test_branding_only_column_and_idempotent(self):
        page='<head></head><header>Dashboard</header><div class="storyline-latest"><h2>Column</h2></div>'
        result=brand_column(page)
        self.assertIn('<header>Dashboard</header>',result)
        self.assertLess(result.index('alt="Jasp Sports News"'),result.index('<h2>Column'))
        self.assertEqual(result,brand_column(result))
