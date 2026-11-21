"""Verify the episode's forecast and scenario claims from frozen derived tables."""

import csv
from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
TEAMS = ("MOUZ", "FURIA", "Vitality")
SCENARIOS = ("baseline", "roster_only", "moderate_pressure", "strong_pressure")


def csv_by_team(name):
    with (DATA / name).open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    indexed = {row["team"]: row for row in rows}
    assert len(rows) == len(indexed), f"Duplicate teams in {name}"
    return indexed


def pct(value):
    return f"{(value * 100).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)}%"


def main():
    baseline = csv_by_team("major_probabilities.csv")
    sensitivity = csv_by_team("pressure_sensitivity.csv")
    experience = csv_by_team("contender_experience.csv")
    claims = json.loads((DATA / "claim_table.json").read_text(encoding="utf-8"), parse_float=Decimal)
    val = lambda key: claims[key]["value"]

    assert set(baseline) == set(sensitivity) and len(baseline) == 32
    assert set(experience) == set(TEAMS)
    for team, row in baseline.items():
        assert Decimal(row["title"]) == Decimal(sensitivity[team]["baseline_title"])
        assert Decimal(row["advance_s3"]) == Decimal(sensitivity[team]["baseline_playoffs"])
    for scenario in SCENARIOS:
        title = [Decimal(row[f"{scenario}_title"]) for row in sensitivity.values()]
        playoffs = [Decimal(row[f"{scenario}_playoffs"]) for row in sensitivity.values()]
        assert all(0 <= p <= q <= 1 for p, q in zip(title, playoffs)), scenario
        assert sum(title) == 1, scenario
        assert sum(playoffs) == 8, scenario

    for team in TEAMS:
        row, scenario = baseline[team], sensitivity[team]
        title = Decimal(row["title"])
        conditional = title / Decimal(row["advance_s3"])
        moderate = Decimal(scenario["moderate_pressure_title"])
        assert title == val("baseline_trio")[team]
        assert moderate == val("moderate_trio")[team]
        if team != "Vitality":
            assert abs(conditional - val(f"conditional_{team.lower()}")) < Decimal("1e-14")
        print(f"{team}: {pct(title)} baseline, {pct(conditional)} given playoffs, {pct(moderate)} moderate")

    assert [Decimal(sensitivity["Vitality"][f"{s}_title"]) for s in SCENARIOS[:3]] == val("vitality_sensitivity")
    for team in ("MOUZ", "Vitality"):
        assert Decimal(experience[team]["average_career_lan_maps"]) == val("experience_gap")[team]
        assert int(experience[team]["major_title_player_credits"]) == val("major_credits")[team]
    furia = experience["FURIA"]
    assert Decimal(furia["average_career_lan_maps"]) == val("experience_furia")["lan"]
    assert int(furia["major_title_player_credits"]) == val("experience_furia")["credits"]
    assert int(furia["major_winning_players"]) == val("experience_furia")["winningPlayers"]
    print("Verified: 32 teams, four scenarios, and three contender roster summaries.")


if __name__ == "__main__":
    main()
