"""Reproduce Stage 1 finish probabilities and ticket evaluations from frozen draws."""

import argparse
import csv
import json
import math
from pathlib import Path
import random

import numpy as np

DATA = Path(__file__).resolve().parents[1] / "data"
SLOTS = ("3-0", "0-3", "advance")
COUNTS = (2, 2, 6)
FINISHES = ("0-3", "1-3", "2-3", "3-2", "3-1", "3-0")


def score_matrix(draws):
    return [v.astype(np.int8) for v in (draws == 5, draws == 0, (draws == 3) | (draws == 4))]


def indices(ticket, field):
    groups = [[field.index(team) for team in ticket[slot]] for slot in SLOTS]
    if tuple(map(len, groups)) != COUNTS or len({i for group in groups for i in group}) != 10:
        raise ValueError("A ticket needs ten distinct teams allocated 2/2/6.")
    return groups


def evaluate(ticket, mat):
    correct = sum(m[:, group].sum(axis=1) for m, group in zip(mat, ticket))
    n = len(correct)
    p = float(np.mean(correct >= 5))
    margin = 1.96 * math.sqrt(p * (1 - p) / n)
    return {
        "p_5_or_more": p,
        "expected_correct": float(correct.mean()),
        "mc_ci95": [max(0.0, p - margin), min(1.0, p + margin)],
        "n": n,
    }


def optimize(mat):
    """The episode's seeded six-start greedy search, with category swaps."""
    used, naive = set(), []
    for m, count in zip(mat, COUNTS):
        picks = [int(i) for i in np.argsort(-m.mean(axis=0)) if i not in used][:count]
        naive.append(picks)
        used.update(picks)
    rng = random.Random(116)
    starts = [naive]
    for _ in range(5):
        pool = list(range(mat[0].shape[1]))
        rng.shuffle(pool)
        starts.append([pool[:2], pool[2:4], pool[4:10]])
    best, best_p = None, -1
    for start in starts:
        ticket = [group.copy() for group in start]
        totals = sum(m[:, group].sum(axis=1) for m, group in zip(mat, ticket))
        p = float(np.mean(totals >= 5))
        while True:
            high, choice = p, None
            occupied = {i: k for k, group in enumerate(ticket) for i in group}
            for k, group in enumerate(ticket):
                for pos, old in enumerate(group):
                    for candidate in range(mat[0].shape[1]):
                        other = occupied.get(candidate)
                        if candidate == old or other == k:
                            continue
                        trial = totals - mat[k][:, old] + mat[k][:, candidate]
                        if other is not None:
                            trial = trial - mat[other][:, candidate] + mat[other][:, old]
                        probability = float(np.mean(trial >= 5))
                        if probability > high + 1e-12:
                            high = probability
                            choice = k, pos, old, candidate, other, trial
            if choice is None:
                break
            k, pos, old, candidate, other, totals = choice
            ticket[k][pos] = candidate
            if other is not None:
                ticket[other][ticket[other].index(candidate)] = old
            p = high
        if p > best_p:
            best, best_p = ticket, p
    return best, naive


def check_stats(actual, expected):
    for key in ("p_5_or_more", "expected_correct", "mc_ci95", "n"):
        np.testing.assert_allclose(actual[key], expected[key], rtol=0, atol=1e-12, err_msg=key)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--search", action="store_true", help="Repeat the seeded search.")
    args = parser.parse_args()
    summary = json.loads((DATA / "forecast_summary.json").read_text(encoding="utf-8"))
    field = summary["field_order"]
    cutoff = summary["search_draws"]
    with np.load(DATA / "stage1_draws.npz", allow_pickle=False) as draws:
        baseline = draws[f"half{summary['baseline_half_life_days']}"]
        np.testing.assert_equal(baseline.shape, (100_000, len(field)))
        with (DATA / "stage1_probabilities.csv").open(encoding="utf-8-sig", newline="") as handle:
            rows = {row["team"]: row for row in csv.DictReader(handle)}
        np.testing.assert_equal(set(rows), set(field))
        for k, finish in enumerate(FINISHES):
            np.testing.assert_allclose(
                np.mean(baseline == k, axis=0),
                [float(rows[t][finish]) for t in field],
                rtol=0, atol=1e-12,
                err_msg=finish,
            )
        print(f"Finish probabilities: {len(field)} teams × {len(FINISHES)} records verified")

        held_out = score_matrix(baseline[cutoff:])
        for label, row in summary["tickets"].items():
            actual = evaluate(indices(row["picks"], field), held_out)
            check_stats(actual, row["evaluation"])
            print(f"{label}: {actual['p_5_or_more']:.1%} on {actual['n']:,} held-out draws")

        model = indices(summary["tickets"]["model"]["picks"], field)
        for half_life, expected in summary["sensitivity"].items():
            actual = evaluate(model, score_matrix(draws[f"half{half_life}"][cutoff:]))
            check_stats(actual, expected)
            print(f"{half_life}-day half-life: {actual['p_5_or_more']:.1%} on {actual['n']:,} held-out draws")

        if args.search:
            search = score_matrix(baseline[:cutoff])
            best, naive = optimize(search)
            for label, observed in (("model", best), ("naive", naive)):
                expected = indices(summary["tickets"][label]["picks"], field)
                if [set(group) for group in expected] != [set(group) for group in observed]:
                    raise AssertionError(f"Search did not reproduce the {label} ticket")
            print("30,000-draw search reproduced both tickets")


if __name__ == "__main__":
    main()
