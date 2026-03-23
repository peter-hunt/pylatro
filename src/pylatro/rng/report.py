"""Seed-report CLI for deterministic RNG verification."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from dataclasses import dataclass

from .engine import RNGEngine
from .events import RNGAvailability, RNGEvents


@dataclass(slots=True)
class ReportConfig:
    seed: str
    antes: int = 3
    shop_cards_per_ante: int = 3
    erratic_count: int = 52
    standard_draw_count: int = 10
    standard_deck_name: str = "default"
    profile_path: str | None = None
    full_draw_order: bool = True
    extra_cards: list[str] | None = None
    removed_cards: list[str] | None = None
    first_hand_by_round: bool = True
    hand_size: int = 8
    report_mode: str = "full"


def _display_name(raw: str) -> str:
    return raw.replace("_", " ").title()


def _load_profile(path: str | None) -> dict | None:
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Profile file not found: {path}")
    return json.loads(p.read_text(encoding="utf-8"))


def build_report(config: ReportConfig) -> list[str]:
    engine = RNGEngine(config.seed)
    profile_data = _load_profile(config.profile_path)
    availability = RNGAvailability.from_profile(profile_data)
    events = RNGEvents(engine, availability=availability)

    lines: list[str] = []
    event_idx = 1

    lines.append(f"seed={config.seed}")
    lines.append("factcheck.startup_order=boss->voucher->tag_small->tag_big")
    lines.append(
        "factcheck.pool_pick_order=pseudorandom_element sorts by sort_id else key/index")
    lines.append(
        "factcheck.shop_joker_order=rarity{ante}->Joker{rarity}{append}{ante}->resampleN")
    lines.append(
        "pools="
        f"jokers_r1:{len(events.pools.joker_by_rarity[1])},"
        f"jokers_r2:{len(events.pools.joker_by_rarity[2])},"
        f"jokers_r3:{len(events.pools.joker_by_rarity[3])},"
        f"jokers_r4:{len(events.pools.joker_by_rarity[4])},"
        f"vouchers:{len(events.pools.voucher_pool)},"
        f"tags:{len(events.pools.tag_pool)},"
        f"tarot:{len(events.pools.tarot_pool)},"
        f"planet:{len(events.pools.planet_pool)},"
        f"spectral:{len(events.pools.spectral_pool)},"
        f"boss:{len(events.pools.boss_pool)},"
        f"booster:{len(events.pools.booster_pool)}"
    )
    lines.append(
        "sources=jokers.txt,vouchers.txt,tarots.txt,planets.txt,spectrals.txt,tags.txt,boss_blinds.txt")
    if availability.unlocked_jokers is None:
        lines.append("availability.jokers=all")
    else:
        lines.append(
            f"availability.jokers=profile_unlocked:{len(availability.unlocked_jokers)}")

    lines.append("[timeline]")

    for ante in range(1, config.antes + 1):
        events.set_ante(ante)
        lines.append(f"timeline.ante={ante}")
        lines.append(f"timeline.blind.small=bl_small")
        lines.append(f"timeline.blind.big=bl_big")

        boss = events.startup_boss()
        lines.append(
            f"{event_idx:04d} timeline.blind.boss key={boss.key_used} pick_index={boss.selected_index} before={boss.trace.before} after={boss.trace.after} value={boss.value} token={boss.value} name={_display_name(boss.value)}"
        )
        event_idx += 1

        voucher = events.startup_voucher()
        lines.append(
            f"{event_idx:04d} timeline.shop.voucher key={voucher.key_used} pick_index={voucher.selected_index} before={voucher.trace.before} after={voucher.trace.after} value={voucher.value} token={voucher.value} name={_display_name(voucher.value)} source=vouchers.txt"
        )
        event_idx += 1

        tag_small = events.startup_small_tag()
        lines.append(
            f"{event_idx:04d} timeline.tag.small key={tag_small.key_used} pick_index={tag_small.selected_index} before={tag_small.trace.before} after={tag_small.trace.after} value={tag_small.value} token={tag_small.value} name={_display_name(tag_small.value)}"
        )
        event_idx += 1

        tag_big = events.startup_big_tag()
        lines.append(
            f"{event_idx:04d} timeline.tag.big key={tag_big.key_used} pick_index={tag_big.selected_index} before={tag_big.trace.before} after={tag_big.trace.after} value={tag_big.value} token={tag_big.value} name={_display_name(tag_big.value)}"
        )
        event_idx += 1

        for card_idx in range(config.shop_cards_per_ante):
            rarity_key = f"rarity{events.ante}"
            rarity_trace = engine.trace_float(rarity_key)
            rarity_roll = float(rarity_trace.result)
            if rarity_roll > 0.95:
                rarity_bucket = 3
            elif rarity_roll > 0.7:
                rarity_bucket = 2
            else:
                rarity_bucket = 1

            lines.append(
                f"{event_idx:04d} timeline.shop.joker_rarity[{card_idx}] key={rarity_key} before={rarity_trace.before} after={rarity_trace.after} roll={rarity_roll:.12f} bucket={rarity_bucket}"
            )
            event_idx += 1

            joker = events.next_shop_joker(rarity=rarity_bucket)
            edition = events.poll_edition()
            lines.append(
                f"{event_idx:04d} timeline.shop.joker[{card_idx}] key={joker.key_used} pick_index={joker.selected_index} before={joker.trace.before} after={joker.trace.after} value={joker.value} token={joker.value} name={_display_name(joker.value)} edition={edition} source=jokers.txt"
            )
            event_idx += 1

            tarot = events.next_shop_tarot()
            lines.append(
                f"{event_idx:04d} timeline.shop.tarot[{card_idx}] key={tarot.key_used} pick_index={tarot.selected_index} before={tarot.trace.before} after={tarot.trace.after} value={tarot.value} token={tarot.value} name={_display_name(tarot.value)} source=tarots.txt"
            )
            event_idx += 1

            planet = events.next_shop_planet()
            lines.append(
                f"{event_idx:04d} timeline.shop.planet[{card_idx}] key={planet.key_used} pick_index={planet.selected_index} before={planet.trace.before} after={planet.trace.after} value={planet.value} token={planet.value} name={_display_name(planet.value)} source=planets.txt"
            )
            event_idx += 1

            spectral = events.next_shop_spectral()
            lines.append(
                f"{event_idx:04d} timeline.shop.spectral[{card_idx}] key={spectral.key_used} pick_index={spectral.selected_index} before={spectral.trace.before} after={spectral.trace.after} value={spectral.value} token={spectral.value} name={_display_name(spectral.value)} source=spectrals.txt"
            )
            event_idx += 1

            pack = events.next_pack_key()
            lines.append(
                f"{event_idx:04d} timeline.shop.pack[{card_idx}] value={pack} name={_display_name(pack)}")
            event_idx += 1

            buffoon_joker = events.next_buffoon_joker()
            lines.append(
                f"{event_idx:04d} timeline.pack.buffoon_joker[{card_idx}] key={buffoon_joker.key_used} pick_index={buffoon_joker.selected_index} before={buffoon_joker.trace.before} after={buffoon_joker.trace.after} value={buffoon_joker.value} token={buffoon_joker.value} name={_display_name(buffoon_joker.value)} source=jokers.txt"
            )
            event_idx += 1

            arcana_card = events.next_pack_consumable(
                "arcana", slot_index=1, omen_globe_enabled=False)
            lines.append(
                f"{event_idx:04d} timeline.pack.arcana_consumable[{card_idx}] key={arcana_card.key_used} pick_index={arcana_card.selected_index} before={arcana_card.trace.before} after={arcana_card.trace.after} value={arcana_card.value} token={arcana_card.value} name={_display_name(arcana_card.value)} source=tarots.txt|spectrals.txt"
            )
            event_idx += 1

            celestial_card = events.next_pack_consumable(
                "celestial", slot_index=1)
            lines.append(
                f"{event_idx:04d} timeline.pack.celestial_consumable[{card_idx}] key={celestial_card.key_used} pick_index={celestial_card.selected_index} before={celestial_card.trace.before} after={celestial_card.trace.after} value={celestial_card.value} token={celestial_card.value} name={_display_name(celestial_card.value)} source=planets.txt"
            )
            event_idx += 1

            spectral_card = events.next_pack_consumable(
                "spectral", slot_index=1)
            lines.append(
                f"{event_idx:04d} timeline.pack.spectral_consumable[{card_idx}] key={spectral_card.key_used} pick_index={spectral_card.selected_index} before={spectral_card.trace.before} after={spectral_card.trace.after} value={spectral_card.value} token={spectral_card.value} name={_display_name(spectral_card.value)} source=spectrals.txt"
            )
            event_idx += 1

    lines.append(f"[draw_order:{config.standard_deck_name}]")
    standard_draw = events.generate_standard_deck_draw(
        draw_count=config.standard_draw_count,
        deck_name=config.standard_deck_name,
    )
    lines.append(f"draw={','.join(standard_draw)}")

    if config.full_draw_order:
        full_order = events.generate_deck_draw_order(
            deck_name=config.standard_deck_name,
            extra_cards=config.extra_cards,
            removed_cards=config.removed_cards,
        )
        lines.append(f"deck_size={len(full_order)}")
        lines.append(f"full_draw_order={','.join(full_order)}")

    if config.first_hand_by_round:
        lines.append("[first_hand_by_round]")
        lines.append("factcheck.round_start_shuffle_key=nr{ante}")
        for ante in range(1, config.antes + 1):
            hand = events.generate_first_hand_for_ante(
                ante=ante,
                hand_size=config.hand_size,
                deck_name=config.standard_deck_name,
            )
            hand_line = ",".join(hand)
            lines.append(
                f"ante={ante} blind=small key=nr{ante} hand={hand_line}")
            lines.append(
                f"ante={ante} blind=big key=nr{ante} hand={hand_line}")
            lines.append(
                f"ante={ante} blind=boss key=nr{ante} hand={hand_line}")

    faces = events.generate_erratic_faces(count=config.erratic_count)
    lines.append("[erratic]")
    lines.append(f"faces={','.join(faces)}")

    digest = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()[:16]
    lines.append(f"trace_hash={digest}")

    return lines


def build_initial_hands_report(config: ReportConfig) -> list[str]:
    """Build compact report containing only first hands by ante/blind.

    This mode intentionally omits shop/timeline noise to verify deck draw
    determinism first.
    """
    engine = RNGEngine(config.seed)
    profile_data = _load_profile(config.profile_path)
    availability = RNGAvailability.from_profile(profile_data)
    events = RNGEvents(engine, availability=availability)

    lines: list[str] = []
    lines.append(f"seed={config.seed}")
    lines.append("report_mode=initial-hands")
    lines.append("factcheck.round_start_shuffle_key=nr{ante}")
    lines.append("factcheck.assumption=no_extra_cards_drawn_before_first_hand")
    lines.append("[initial_hands]")

    for ante in range(1, config.antes + 1):
        hand = events.generate_first_hand_for_ante(
            ante=ante,
            hand_size=config.hand_size,
            deck_name=config.standard_deck_name,
        )
        hand_line = ",".join(hand)
        lines.append(f"ante={ante} blind=small key=nr{ante} hand={hand_line}")
        lines.append(f"ante={ante} blind=big key=nr{ante} hand={hand_line}")
        lines.append(f"ante={ante} blind=boss key=nr{ante} hand={hand_line}")

    digest = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()[:16]
    lines.append(f"trace_hash={digest}")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate deterministic RNG verification report")
    parser.add_argument("--seed", required=True, help="Seed string to analyze")
    parser.add_argument("--antes", type=int, default=3,
                        help="How many antes to report")
    parser.add_argument("--shop-cards", type=int,
                        default=3, help="Shop pulls per ante")
    parser.add_argument("--erratic-count", type=int,
                        default=52, help="Erratic deck sample size")
    parser.add_argument("--standard-draw-count", type=int,
                        default=10, help="How many cards to draw from a standard (non-erratic) deck")
    parser.add_argument("--standard-deck", default="default",
                        help="Deck archetype for non-erratic verification (default|abandoned|checkered)")
    parser.add_argument("--profile", default=None,
                        help="Optional profile json path to apply Python-side unlock filtering")
    parser.add_argument("--no-full-draw-order", action="store_true",
                        help="Disable printing full deterministic draw order for selected non-erratic deck")
    parser.add_argument("--extra-card", action="append", default=None,
                        help="Append extra starting card(s), repeatable, format like SA or D10")
    parser.add_argument("--remove-card", action="append", default=None,
                        help="Remove starting card(s) before shuffle, repeatable, format like SA or D10")
    parser.add_argument("--no-first-hand-by-round", action="store_true",
                        help="Disable printing first drawn hand per round")
    parser.add_argument("--hand-size", type=int, default=8,
                        help="Hand size used when printing first drawn hand per round")
    parser.add_argument("--report-mode", choices=["full", "initial-hands"], default="full",
                        help="Report output mode; use initial-hands for low-noise first-hand verification")

    args = parser.parse_args(argv)
    config = ReportConfig(
        seed=args.seed,
        antes=max(1, args.antes),
        shop_cards_per_ante=max(1, args.shop_cards),
        erratic_count=max(1, args.erratic_count),
        standard_draw_count=max(1, args.standard_draw_count),
        standard_deck_name=args.standard_deck,
        profile_path=args.profile,
        full_draw_order=not bool(args.no_full_draw_order),
        extra_cards=args.extra_card,
        removed_cards=args.remove_card,
        first_hand_by_round=not bool(args.no_first_hand_by_round),
        hand_size=max(1, args.hand_size),
        report_mode=args.report_mode,
    )

    builder = build_initial_hands_report if config.report_mode == "initial-hands" else build_report
    for line in builder(config):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
