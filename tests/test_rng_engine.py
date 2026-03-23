"""Determinism tests for the new RNG subsystem."""

from __future__ import annotations
import json

from pylatro.rng.events import RNGEvents
from pylatro.rng.engine import RNGEngine
from pylatro.rng.pools import DEFAULT_POOLS
from pylatro.rng.events import RNGAvailability

import pytest


lupa = pytest.importorskip("lupa")


def test_same_seed_same_sequence():
    a = RNGEngine("7LB2WVPK")
    b = RNGEngine("7LB2WVPK")

    keys = ["boss", "Voucher1", "Tag1", "rarity1", "edi1", "lucky_mult"]
    seq_a = [a.next_float(k) for k in keys]
    seq_b = [b.next_float(k) for k in keys]

    assert seq_a == seq_b


def test_snapshot_restore_replays_identically():
    engine = RNGEngine("XEQH7CP9")
    pre = [engine.next_float("boss"), engine.next_float("Voucher1")]
    state = engine.snapshot_state()

    continuation_a = [engine.next_float("Tag1"), engine.next_float("Tag1")]
    engine.restore_state(state)
    continuation_b = [engine.next_float("Tag1"), engine.next_float("Tag1")]

    assert pre
    assert continuation_a == continuation_b


def test_erratic_generation_is_deterministic():
    a = RNGEvents(RNGEngine("7LB2WVPK"))
    b = RNGEvents(RNGEngine("7LB2WVPK"))

    faces_a = a.generate_erratic_faces(52)
    faces_b = b.generate_erratic_faces(52)

    assert faces_a == faces_b
    assert len(faces_a) == 52


def test_standard_deck_draw_is_deterministic_non_erratic():
    a = RNGEvents(RNGEngine("7LB2WVPK"))
    b = RNGEvents(RNGEngine("7LB2WVPK"))

    draw_a = a.generate_standard_deck_draw(draw_count=10, deck_name="default")
    draw_b = b.generate_standard_deck_draw(draw_count=10, deck_name="default")

    assert draw_a == draw_b
    assert len(draw_a) == 10


def test_real_content_pools_loaded():
    assert "joker" in DEFAULT_POOLS.joker_by_rarity[1]
    assert "seed_money" in DEFAULT_POOLS.voucher_pool
    assert "the_fool" in DEFAULT_POOLS.tarot_pool


def test_pack_helpers_use_balatro_key_appends():
    events = RNGEvents(RNGEngine("7LB2WVPK"))
    events.set_ante(2)

    buffoon = events.next_buffoon_joker()
    assert buffoon.key_used.startswith("Joker")
    assert "buf2" in buffoon.key_used

    arcana = events.next_pack_consumable("arcana", omen_globe_enabled=False)
    assert arcana.key_used == "Tarotar12"

    celestial = events.next_pack_consumable("celestial")
    assert celestial.key_used == "Planetpl12"

    spectral = events.next_pack_consumable("spectral")
    assert spectral.key_used == "Spectralspe2"


def test_profile_based_unlock_filter_blocks_locked_jokers(tmp_path):
    profile = {
        "unlocks": {
            "jokers": ["joker"]
        }
    }
    profile_path = tmp_path / "profile.json"
    profile_path.write_text(json.dumps(profile), encoding="utf-8")

    availability = RNGAvailability.from_profile(profile)
    events = RNGEvents(RNGEngine("7LB2WVPK"), availability=availability)

    for _ in range(5):
        pull = events.next_shop_joker(rarity=1)
        assert pull.value == "joker"
