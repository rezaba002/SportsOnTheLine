import json
import pathlib
import unittest
from bomb_context import extract_context, terminal_probability, plant_from_samples, samples_in


class BombContextTests(unittest.TestCase):
    def test_delta_updates_and_interrupted_attempt(self):
        replay = {"states": [
            {"ingame_tick": 0, "bomb": {"is_planted": False}, "players": [{"id": 1, "name": "A", "is_planting": True}]},
            {"ingame_tick": 64, "players": [{"id": 1, "is_planting": False}]},
            {"ingame_tick": 128, "bomb": {"is_planted": True}},
            {"ingame_tick": 192, "bomb": {"is_defusing": True}},
            {"ingame_tick": 256, "bomb": {"is_defused": True}}]}
        result = extract_context(replay, 0, 64)
        self.assertEqual(result["plant_s"], 2)
        self.assertIsNone(result["planter"])
        self.assertEqual(result["defuse_s"], 4)

    def test_bomb_can_win_with_zero_terrorists(self):
        self.assertIsNone(terminal_probability(0, 2, True))
        self.assertEqual(terminal_probability(0, 2, False), 0)
        self.assertEqual(terminal_probability(1, 0, True), 1)

    def test_timer_recovers_plant_without_transition(self):
        self.assertAlmostEqual(plant_from_samples([(6400, 2, 30)], 0, 64), 90)

    def test_real_round_plant(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        replay = json.loads((root / "research/bomb_probe_round2.json").read_text())
        # Compare reconstructed transition to direct replay tick, independent of model outputs.
        result = extract_context(replay, 0, 64)
        self.assertAlmostEqual(result["plant_s"], 14589 / 64)
        self.assertEqual(result["planter"], "ZywOo")

    def test_timer_inference_matches_real_transition(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        body = (root / "research/bomb_probe_round2.json").read_bytes()
        inferred = plant_from_samples(samples_in(body), 0, 64)
        self.assertLess(abs(inferred - 14589/64), .05)


if __name__ == "__main__":
    unittest.main()
