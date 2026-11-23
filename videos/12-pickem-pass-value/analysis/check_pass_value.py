"""Recompute coin odds and resale comparisons from frozen aggregates."""

import json
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path


INPUT = Path(__file__).resolve().parents[1] / "data/frozen_inputs.json"


def cents(value):
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def main():
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    n = data["runs_per_strategy"]
    for strategy, counts in data["skill_challenge_counts_0_through_6"].items():
        assert len(counts) == 7 and sum(counts) == n
        silver, gold, diamond = sum(counts[:3]), sum(counts[3:6]), counts[6]
        print(f"{strategy:8} Silver {silver / n:.3%} · Gold {gold / n:.3%} · "
              f"Diamond {diamond}/{n:,} ({diamond / n:.3%})")

    shop = data["shop"]
    cologne = data["cologne"]
    token = Decimal(shop["usd_per_token"])
    fee = Decimal(shop["buyer_paid_per_seller_dollar"])
    price = Decimal(shop["pass_usd"])
    holo_shop_value = shop["holo_tokens"] * token
    holo_break = cents(holo_shop_value * fee)
    assert (holo_shop_value, holo_break) == (Decimal("7.92"), Decimal("9.11"))

    budgets = data["token_budgets"]
    shop_value = token * budgets["diamond"]
    resale = cents(shop_value / fee)
    assert (shop_value, resale) == (Decimal("8.91"), Decimal("7.75"))
    assert resale < price
    print(f"Diamond: ${shop_value} shop value; ${resale} Wallet at shop-price resale.")
    print(f"Holo: ${holo_shop_value} shop value; ${holo_break} gross to recover it after modeled fees.")

    event = cologne["event_holo"]
    print(f"Event Holos cheaper: {event['cheaper_in_recent_window']}/{event['paired_launch_and_recent_n']} "
          f"({event['cheaper_in_recent_window'] / event['paired_launch_and_recent_n']:.0%})")

    quoted_tokens = 0
    quoted_value = Decimal(0)
    for pair in cologne["souvenir_pairs"]:
        increment = Decimal(pair["souvenir_eur"]) / fee - Decimal(pair["base_eur"])
        quote = pair["quote_tokens"]
        print(f"{pair['item']}: EUR {cents(increment)} added before token top-ups and pass cost; "
              f"{pair['souvenir_sales']} souvenir sales; quote: {quote if quote is not None else 'unknown'}")
        if quote is not None:
            quoted_tokens += quote
            # Sum the per-skin estimates as reported to the nearest cent.
            quoted_value += cents(increment)
        else:
            assert cents(increment) == Decimal("16.36")
    assert quoted_tokens == 236 and cents(quoted_value) == Decimal("4.79")
    print(f"Quoted pair: {quoted_tokens} tokens, {budgets['silver'] - quoted_tokens} left, "
          f"EUR {cents(quoted_value)} added before leftovers and pass cost.")


if __name__ == "__main__":
    main()
