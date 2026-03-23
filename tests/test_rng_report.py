"""Seed report tests used for quick verification workflows."""

from __future__ import annotations
from pylatro.rng.report import ReportConfig, build_initial_hands_report, build_report

import pytest


lupa = pytest.importorskip("lupa")


def test_report_is_stable_for_same_seed():
    config = ReportConfig(seed="7LB2WVPK", antes=2,
                          shop_cards_per_ante=2, erratic_count=10)
    a = build_report(config)
    b = build_report(config)
    assert a == b


def test_report_contains_trace_hash_line():
    lines = build_report(ReportConfig(
        seed="XEQH7CP9", antes=1, shop_cards_per_ante=1, erratic_count=5))
    assert any(line.startswith("trace_hash=") for line in lines)


def test_report_includes_joker_key_and_standard_deck_draw_section():
    lines = build_report(ReportConfig(
        seed="7LB2WVPK",
        antes=2,
        shop_cards_per_ante=1,
        erratic_count=5,
        standard_draw_count=5,
        standard_deck_name="default",
    ))

    assert any(
        "timeline.shop.joker_rarity" in line and "key=rarity2" in line for line in lines)
    assert any(
        "timeline.shop.joker" in line and "key=Joker" in line for line in lines)
    assert any("timeline.shop.joker" in line and "name=" in line for line in lines)
    assert any(
        "timeline.shop.joker" in line and "token=" in line for line in lines)
    assert any(
        "timeline.shop.voucher" in line for line in lines)
    assert any("timeline.shop.tarot" in line and "name=" in line for line in lines)
    assert any(
        "timeline.shop.planet" in line and "name=" in line for line in lines)
    assert any(
        "timeline.shop.spectral" in line and "name=" in line for line in lines)
    assert any("timeline.pack.buffoon_joker" in line for line in lines)
    assert any("timeline.pack.arcana_consumable" in line for line in lines)
    assert any("timeline.pack.celestial_consumable" in line for line in lines)
    assert any("timeline.pack.spectral_consumable" in line for line in lines)
    assert any(line.startswith("[draw_order:default]") for line in lines)
    assert any(line.startswith("draw=") for line in lines)
    assert any(line.startswith("full_draw_order=") for line in lines)


def test_report_includes_factcheck_lines():
    lines = build_report(ReportConfig(seed="7LB2WVPK", antes=1,
                         shop_cards_per_ante=1, erratic_count=3))
    assert any(line.startswith("factcheck.startup_order=") for line in lines)
    assert any(line.startswith("factcheck.pool_pick_order=") for line in lines)
    assert any(line.startswith("availability.jokers=") for line in lines)


def test_report_contains_timeline_blind_lines():
    lines = build_report(ReportConfig(seed="7LB2WVPK", antes=1,
                         shop_cards_per_ante=1, erratic_count=3))
    assert any(line.startswith("timeline.ante=") for line in lines)
    assert any(line.startswith("timeline.blind.small=") for line in lines)
    assert any(line.startswith("timeline.blind.big=") for line in lines)
    assert any("timeline.blind.boss" in line for line in lines)


def test_report_contains_first_hand_by_round_lines():
    lines = build_report(ReportConfig(seed="7LB2WVPK", antes=2,
                         shop_cards_per_ante=1, erratic_count=3))
    assert any(line.startswith("[first_hand_by_round]") for line in lines)
    assert any(line.startswith("factcheck.round_start_shuffle_key=")
               for line in lines)
    assert any(line.startswith("ante=1 blind=small key=nr1 hand=")
               for line in lines)
    assert any(line.startswith("ante=1 blind=big key=nr1 hand=")
               for line in lines)
    assert any(line.startswith("ante=1 blind=boss key=nr1 hand=")
               for line in lines)


def test_initial_hands_mode_is_compact_and_deterministic():
    config = ReportConfig(seed="7LB2WVPK", antes=2,
                          report_mode="initial-hands", hand_size=8)
    a = build_initial_hands_report(config)
    b = build_initial_hands_report(config)
    assert a == b
    assert any(line.startswith("report_mode=initial-hands") for line in a)
    assert any(line.startswith("[initial_hands]") for line in a)
    assert any(line.startswith("ante=1 blind=small key=nr1 hand=")
               for line in a)
    assert not any("timeline.shop" in line for line in a)
