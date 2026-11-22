import sys
import pathlib
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).parent / "vendor"))
from swing_v4 import features, round_events, current_team, bootstrap_interval


class SwingTests(unittest.TestCase):
    def test_phase_clock_resets_and_terrorist_death_is_not_terminal(self):
        rd = {"roster": [["A", 1, 2], ["B", 2, 3]], "kills": [[90, "B", 3, "A", 2, 1]],
              "stats": [{"steam_id": 1, "team_side": "T", "economy_level": 2, "win": 1, "clan_name": "Spirit"},
                        {"steam_id": 2, "team_side": "CT", "economy_level": 2, "win": 0, "clan_name": "Falcons"}]}
        # The fixture has one survivor on each side, not an assumed 5v5.
        events = round_events(rd, {"planted": True, "plant_s": 80})
        self.assertEqual(events[0]["after"][0], 0)
        self.assertEqual(events[0]["after"][2], 1)
        self.assertAlmostEqual(events[0]["after"][4], .75)

    def test_phase_switch_changes_context_without_awarding_a_kill(self):
        before = features(3, 3, 79, 80, 2, 2, 0)
        after = features(3, 3, 81, 80, 2, 2, 0)
        self.assertEqual(before[2], 0)
        self.assertEqual(after[2], 1)
        self.assertEqual(before[:2], after[:2])

    def test_current_team_aliases(self):
        self.assertTrue(current_team("Team Spirit", "Spirit"))
        self.assertFalse(current_team("Team Falcons", "Spirit"))

    def test_cluster_interval_uses_map_denominator(self):
        low, high = bootstrap_interval([(2, 2), (2, 2), (2, 2)], 123)
        self.assertEqual((low, high), (1, 1))

    def test_same_frame_mutual_deaths_are_all_kept(self):
        rd = {"roster": [["A", 1, 2], ["B", 2, 3]],
              "kills": [[90,"A",2,"B",3,1],[90,"B",3,"A",2,1]],
              "stats": [{"steam_id":1,"team_side":"T","economy_level":2,"win":1,"clan_name":"Spirit"},
                        {"steam_id":2,"team_side":"CT","economy_level":2,"win":0,"clan_name":"Falcons"}]}
        events = round_events(rd, {"planted":False,"plant_s":None,"winner":"T"})
        self.assertEqual(len(events), 2)
        for event in events:
            self.assertEqual(event["after"][:2], [0, 0])
            self.assertAlmostEqual(sum(a[2] for a in event["alternatives"]), 1)

    def test_defuse_cleanup_does_not_get_credit(self):
        rd = {"roster":[["A",1,2],["B",2,3]], "step":8,"rate":64,
              "kills":[[100.05,"A",2,"B",3,1]],
              "stats":[{"steam_id":1,"team_side":"T","economy_level":2,"win":0,"clan_name":"Spirit"},
                       {"steam_id":2,"team_side":"CT","economy_level":2,"win":1,"clan_name":"Falcons"}]}
        events = round_events(rd,{"planted":True,"plant_s":65,"end_s":100,"end_reason":"BombDefused","winner":"CT"})
        self.assertEqual(events, [])


if __name__ == "__main__":
    unittest.main()
