"""Offline regression tests for radar explanations and column additions."""
import unittest
from mcdraft.editorial_expansion import RADAR_JS, RADAR_CSS, column_desks, add_column_desks, humanise_column_story, _ordinal

class EditorialExpansionTests(unittest.TestCase):
    def setUp(self):
        self.matches = [
          dict(event=2,entry_1_name='Alpha',entry_2_name='Beta',entry_1_points=58,entry_2_points=55),
          dict(event=2,entry_1_name='Gamma',entry_2_name='Delta',entry_1_points=45,entry_2_points=60),
          dict(event=1,entry_1_name='Alpha',entry_2_name='Gamma',entry_1_points=30,entry_2_points=25),
          dict(event=1,entry_1_name='Beta',entry_2_name='Delta',entry_1_points=32,entry_2_points=35),
        ]
        self.honours = {'weeks':[
          {'gw':1,'awards':[],'positions':{'Alpha':2,'Beta':3,'Gamma':4,'Delta':1}},
          {'gw':2,'awards':[{'label':'🚀 Improver of the Week','managers':['Alpha'], 'detail':'Up one place'}],
           'positions':{'Alpha':1,'Beta':3,'Gamma':4,'Delta':2}},
        ]}
        self.history={'gameweeks':{'1':{'finished':True},'2':{'finished':True},'3':{'finished':False}}}

    def test_completed_week_has_awards_and_standings_story(self):
        lines=column_desks(2,self.honours,self.matches,self.history)
        self.assertTrue(any('award' in x.lower() for x in lines))
        self.assertTrue(any('Alpha' in x and '1st' in x for x in lines))
        self.assertTrue(any('edged' in x or 'escape' in x for x in lines))

    def test_no_live_week_claims_or_future_leakage(self):
        self.assertEqual(column_desks(3,self.honours,self.matches,self.history),[])
        f=add_column_desks(lambda gw,phase:['Existing '+phase],self.honours,self.matches,self.history)
        self.assertEqual(f(2,'live'),['Existing live'])
        self.assertEqual(f(3,'upcoming'),['Existing upcoming'])
        self.assertGreater(len(f(2,'completed')),1)

    def test_ordinal_suffixes(self):
        self.assertEqual([_ordinal(n) for n in (1,2,3,4,11,12,13,21,23)],
                         ['1st','2nd','3rd','4th','11th','12th','13th','21st','23rd'])

    def test_story_is_paragraphs_and_avoids_duplicate_table_and_streak(self):
        body=("GW5 belonged to Semenyo after 17 points. PAUer Rangers were climbing the table. "
              "Kamararama FC have made it 5 wins in a row. "
              "Jacquet Potato squeezed past danny’s doggy dudes 37-36. "
              "There are free agents waiting to be claimed.")
        extras=["🪑 BENCH WATCH: Brobbey got 17 points on the bench.",
                "THE TABLE SHUFFLE — PAUer Rangers climb from 5th to 3th.",
                "THE FORM WATCH — Kamararama FC have 5 wins on the bounce.",
                "THE NERVE CENTRE — Jacquet Potato edged danny’s doggy dudes 37–36.",
                "Spare a thought for Ollie Gonna Squashya, whose 44 points weren't enough."]
        next_week="GW6 offers Jaap? Best Stam against PAUer Rangers."
        wrapped=humanise_column_story(lambda gw:'\n\n'.join([body]+extras+[next_week]),self.honours)
        story=wrapped(5)
        self.assertEqual(story,wrapped(5))
        self.assertGreaterEqual(story.count('\n\n'),2)
        self.assertTrue(story.endswith(next_week))
        self.assertNotIn('3th',story)
        self.assertNotIn('THE FORM WATCH',story)
        self.assertIn('Brobbey',story)
        self.assertIn('Ollie Gonna Squashya',story)

    def test_radar_explanation_uses_original_scores(self):
        self.assertIn('mcdOriginalRenderMyTeamRadar()',RADAR_JS)
        self.assertIn('matrix=eligible.map(radarScores)',RADAR_JS)
        self.assertIn('90 PL minutes',RADAR_JS)
        self.assertIn('radar-explainer',RADAR_CSS)

if __name__=='__main__': unittest.main()
