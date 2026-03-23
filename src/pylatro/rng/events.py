"""High-level RNG event helpers mirroring Balatro call patterns."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .engine import RNGEngine, RNGTrace
from .pools import RNGPools, DEFAULT_POOLS


@dataclass(slots=True)
class PullResult:
    """Result of a keyed pull with trace metadata."""

    value: str
    key_used: str
    attempts: int
    selected_index: int
    trace: RNGTrace


@dataclass(slots=True)
class RNGAvailability:
    """Python-side availability state used before Lua RNG picks."""

    unlocked_jokers: set[str] | None = None
    unavailable_jokers: set[str] | None = None
    unavailable_tarots: set[str] | None = None
    unavailable_planets: set[str] | None = None
    unavailable_spectrals: set[str] | None = None

    @classmethod
    def from_profile(cls, profile_data: dict[str, Any] | None) -> "RNGAvailability":
        if not profile_data:
            return cls()

        unlocks = profile_data.get("unlocks", {}) if isinstance(
            profile_data, dict) else {}
        unlocked_jokers_raw = unlocks.get(
            "jokers") if isinstance(unlocks, dict) else None
        unlocked_jokers = set(
            unlocked_jokers_raw) if unlocked_jokers_raw else None
        return cls(unlocked_jokers=unlocked_jokers)


class RNGEvents:
    """Event-order helper built on top of RNGEngine."""

    def __init__(self, engine: RNGEngine, pools: RNGPools | None = None, ante: int = 1, availability: RNGAvailability | None = None):
        self.engine = engine
        self.pools = pools or DEFAULT_POOLS
        self.ante = ante
        self.availability = availability or RNGAvailability()

    def set_availability(self, availability: RNGAvailability) -> None:
        self.availability = availability

    def set_ante(self, ante: int) -> None:
        self.ante = ante

    def _pick_with_resample(self, pool: list[str], base_key: str, unavailable: set[str] | None = None, fallback_value: str | None = None) -> PullResult:
        if unavailable is None:
            unavailable = set()

        candidate = [
            v if v not in unavailable else "UNAVAILABLE" for v in pool]
        attempts = 1
        key_used = base_key
        trace, selected_index = self.engine.trace_pick(key_used, candidate)
        value = str(trace.result)

        max_attempts = max(32, len(candidate) * 2)
        while value == "UNAVAILABLE" and attempts < max_attempts:
            attempts += 1
            key_used = f"{base_key}_resample{attempts}"
            trace, selected_index = self.engine.trace_pick(key_used, candidate)
            value = str(trace.result)

        if value == "UNAVAILABLE":
            if fallback_value:
                value = fallback_value
            else:
                raise RuntimeError(
                    f"No available outcome for key '{base_key}' after {attempts} attempts"
                )

        return PullResult(value=value, key_used=key_used, attempts=attempts, selected_index=selected_index, trace=trace)

    def _joker_unavailable(self, rarity: int, explicit_unavailable: set[str] | None) -> set[str]:
        out = set(explicit_unavailable or set())

        if self.availability.unavailable_jokers:
            out.update(self.availability.unavailable_jokers)

        if self.availability.unlocked_jokers is not None and rarity < 4:
            for joker in self.pools.joker_by_rarity[rarity]:
                if joker not in self.availability.unlocked_jokers:
                    out.add(joker)

        return out

    def startup_boss(self) -> PullResult:
        return self._pick_with_resample(self.pools.boss_pool, "boss")

    def startup_voucher(self) -> PullResult:
        return self._pick_with_resample(self.pools.voucher_pool, f"Voucher{self.ante}")

    def startup_small_tag(self) -> PullResult:
        eligible = [t for t in self.pools.tag_pool if self.pools.tag_min_ante.get(
            t, 0) <= self.ante]
        return self._pick_with_resample(eligible, f"Tag{self.ante}")

    def startup_big_tag(self) -> PullResult:
        eligible = [t for t in self.pools.tag_pool if self.pools.tag_min_ante.get(
            t, 0) <= self.ante]
        return self._pick_with_resample(eligible, f"Tag{self.ante}")

    def _roll_joker_rarity(self, append: str = "") -> int:
        rarity_roll = self.engine.next_float(f"rarity{self.ante}{append}")
        if rarity_roll > 0.95:
            return 3
        if rarity_roll > 0.7:
            return 2
        return 1

    def next_shop_joker(self, append: str = "", unavailable: set[str] | None = None, rarity: int | None = None) -> PullResult:
        rarity = rarity or self._roll_joker_rarity(append)
        pool = self.pools.joker_by_rarity[rarity]
        pool_key = f"Joker{rarity}{append}{self.ante}"
        blocked = self._joker_unavailable(rarity, unavailable)
        fallback = "joker" if rarity == 1 and "joker" in pool else None
        return self._pick_with_resample(pool, pool_key, unavailable=blocked, fallback_value=fallback)

    def next_shop_tarot(self, append: str = "", unavailable: set[str] | None = None) -> PullResult:
        blocked = set(unavailable or set())
        if self.availability.unavailable_tarots:
            blocked.update(self.availability.unavailable_tarots)
        fallback = "the_fool" if "the_fool" in self.pools.tarot_pool else None
        return self._pick_with_resample(self.pools.tarot_pool, f"Tarot{append}{self.ante}", unavailable=blocked, fallback_value=fallback)

    def next_shop_planet(self, append: str = "", unavailable: set[str] | None = None) -> PullResult:
        blocked = set(unavailable or set())
        if self.availability.unavailable_planets:
            blocked.update(self.availability.unavailable_planets)
        fallback = "plute" if "plute" in self.pools.planet_pool else None
        return self._pick_with_resample(self.pools.planet_pool, f"Planet{append}{self.ante}", unavailable=blocked, fallback_value=fallback)

    def next_shop_spectral(self, append: str = "", unavailable: set[str] | None = None) -> PullResult:
        blocked = set(unavailable or set())
        if self.availability.unavailable_spectrals:
            blocked.update(self.availability.unavailable_spectrals)
        fallback = "incantation" if "incantation" in self.pools.spectral_pool else None
        return self._pick_with_resample(self.pools.spectral_pool, f"Spectral{append}{self.ante}", unavailable=blocked, fallback_value=fallback)

    def next_buffoon_joker(self, unavailable: set[str] | None = None) -> PullResult:
        """Balatro Buffoon pack joker pull (key append `buf`)."""
        return self.next_shop_joker(append="buf", unavailable=unavailable)

    def next_pack_consumable(self, pack_kind: str, slot_index: int = 1, omen_globe_enabled: bool = False, unavailable: set[str] | None = None) -> PullResult:
        """Balatro-like pack consumable pull with pack-specific key appends.

        Arcana: `ar1` (Tarot) with Omen Globe chance switching to Spectral via `ar2`.
        Celestial: `pl1` (Planet).
        Spectral: `spe` (Spectral).
        Buffoon: Joker via `buf`.
        """
        kind = pack_kind.strip().lower()
        if kind == "arcana":
            if omen_globe_enabled and self.engine.next_float("omen_globe") > 0.8:
                return self.next_shop_spectral(append="ar2", unavailable=unavailable)
            return self.next_shop_tarot(append="ar1", unavailable=unavailable)
        if kind == "celestial":
            return self.next_shop_planet(append="pl1", unavailable=unavailable)
        if kind == "spectral":
            return self.next_shop_spectral(append="spe", unavailable=unavailable)
        if kind == "buffoon":
            return self.next_buffoon_joker(unavailable=unavailable)
        raise ValueError(f"Unsupported pack_kind '{pack_kind}'")

    def next_pack_key(self, append: str = "") -> str:
        key = f"pack_generic{self.ante}{append}"
        total_weight = sum(weight for _, weight in self.pools.booster_pool)
        poll = self.engine.next_float(key) * total_weight
        running = 0.0
        selected = self.pools.booster_pool[-1][0]
        for pack_key, weight in self.pools.booster_pool:
            running += weight
            if running >= poll:
                selected = pack_key
                break
        return selected

    def poll_edition(self, append: str = "", mod: float = 1.0, edition_rate: float = 1.0, no_neg: bool = False) -> str:
        # Matches Balatro threshold ordering in poll_edition.
        key = f"edi{append}{self.ante}"
        edition_poll = self.engine.next_float(key)
        if edition_poll > 1 - 0.003 * mod and not no_neg:
            return "negative"
        if edition_poll > 1 - 0.006 * edition_rate * mod:
            return "polychrome"
        if edition_poll > 1 - 0.02 * edition_rate * mod:
            return "holo"
        if edition_poll > 1 - 0.04 * edition_rate * mod:
            return "foil"
        return "base"

    def generate_erratic_faces(self, count: int = 52) -> list[str]:
        out: list[str] = []
        for _ in range(count):
            value, _ = self.engine.pick_element(
                "erratic", self.pools.playing_cards)
            out.append(str(value))
        return out

    def generate_standard_deck_draw(self, draw_count: int = 10, deck_name: str = "default", shuffle_key: str = "shuffle") -> list[str]:
        """Shuffle a non-erratic deck and return the top N cards for verification."""
        cards = self.pools.get_deck_cards(deck_name)
        shuffled = self.engine.shuffle(shuffle_key, cards)
        return [str(card) for card in shuffled[:draw_count]]

    def generate_deck_draw_order(
        self,
        deck_name: str = "default",
        shuffle_key: str = "shuffle",
        extra_cards: list[str] | None = None,
        removed_cards: list[str] | None = None,
    ) -> list[str]:
        """Return full deterministic draw order for a deck after modifiers.

        This mirrors the idea that deck composition is finalized first,
        then shuffled once by key, and cards are drawn from the resulting order.
        """
        cards = self.pools.get_deck_cards(deck_name)

        if removed_cards:
            for card in removed_cards:
                if card in cards:
                    cards.remove(card)

        if extra_cards:
            cards.extend(extra_cards)

        shuffled = self.engine.shuffle(shuffle_key, cards)
        return [str(card) for card in shuffled]

    def generate_first_hand_for_ante(
        self,
        ante: int,
        hand_size: int = 8,
        deck_name: str = "default",
    ) -> list[str]:
        """Return first drawn hand for a blind start in an ante.

        Balatro shuffles with key `nr{ante}` when entering DRAW_TO_HAND.
        This helper assumes no extra cards are drawn before first hand.
        """
        order = self.generate_deck_draw_order(
            deck_name=deck_name,
            shuffle_key=f"nr{ante}",
            extra_cards=None,
            removed_cards=None,
        )
        return order[:hand_size]

    # In-hand / random event helpers
    def lucky_mult_trigger(self, normal_probability: float = 1.0) -> bool:
        return self.engine.next_float("lucky_mult") < normal_probability / 5

    def lucky_money_trigger(self, normal_probability: float = 1.0) -> bool:
        return self.engine.next_float("lucky_money") < normal_probability / 15

    def glass_breaks(self, normal_probability: float = 1.0, glass_odds: float = 4.0) -> bool:
        return self.engine.next_float("glass") < normal_probability / glass_odds

    def wheel_of_fortune_hits(self, normal_probability: float = 1.0, odds: float = 4.0) -> bool:
        return self.engine.next_float("wheel_of_fortune") < normal_probability / odds
