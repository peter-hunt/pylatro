# Shop Generation Special Cases

This document explains all special shop mechanics from Balatro and how Pylatro implements them.

## Overview

Balatro shops have several guaranteed items based on:
1. **Game state**: First shop always includes Buffoon Pack (normal)
2. **Tags**: Received at blind skips and blind wins, modify next shop

---

## First Shop Guarantee (Ante 1)

**Always**: Buffoon Pack (normal size) appears in the first shop of every run.

**Implementation**:
```python
# In shop_phase()
if run.ante == 1:
    booster_packs.append(("buffoon", "normal"))
    # Then add RNG packs for remaining slots
```

This is NOT controlled by tags—it's a design guarantee to onboard players to booster packs.

---

## Tag-Based Shop Modifiers

When a tag is received, it modifies the NEXT shop. Use `run.pending_tag_effects` dict to track activation.

### Booster Pack Tags (Exclusive Pack)

These grant a single, guaranteed pack type:

| Tag | Effect | Implementation |
|-----|--------|-----------------|
| Buffoon Tag | Free Mega Buffoon Pack | `run.pending_tag_effects["buffoon_tag_pending"] = True` |
| Charm Tag | Free Mega Arcana Pack | `run.pending_tag_effects["charm_tag_pending"] = True` |
| Ethereal Tag | Free Spectral Pack | `run.pending_tag_effects["ethereal_tag_pending"] = True` |
| Meteor Tag | Free Mega Celestial Pack | `run.pending_tag_effects["meteor_tag_pending"] = True` |
| Standard Tag | Free Mega Standard Pack | `run.pending_tag_effects["standard_tag_pending"] = True` |

**In shop_phase()**:
```python
if "buffoon_tag_pending" in run.pending_tag_effects:
    booster_packs.append(("buffoon", "mega"))
    del run.pending_tag_effects["buffoon_tag_pending"]
```

### Edition Joker Tags (Base Joker + Edition)

These modify a randomly-selected **base edition** (no current edition) shop joker:

| Tag | Edition | Free? |
|-----|---------|-------|
| Foil Tag | Foil | Yes |
| Holographic Tag | Holographic | Yes |
| Negative Tag | Negative | Yes |
| Polychrome Tag | Polychrome | Yes |

**Implementation**:
```python
# When tag received:
# 1. Select a random base-edition joker from shop
# 2. Apply edition and mark as free
# 3. Store in run.guaranteed_shop_jokers

# In shop_phase():
for joker_id, edition in run.guaranteed_shop_jokers:
    joker_obj = create_joker(joker_id, edition=edition)
    guaranteed_jokers.append(joker_obj)
    joker_prices[joker_obj] = 0  # Make it free
```

### Rarity Joker Tags (Free Count)

These grant free jokers of a specific rarity:

| Tag | Count | Rarity |
|-----|-------|--------|
| Uncommon Tag | 1 | Uncommon |
| Rare Tag | 1 | Rare |

**Implementation**:
```python
# When tag received:
if tag.name == "Rare Tag":
    run.free_joker_count += 1

# In shop_phase():
# Generate 3 shop jokers normally
# Then mark first `free_joker_count` as free (price = 0)
for i in range(run.free_joker_count):
    joker_prices[jokers[i]] = 0
run.free_joker_count = 0
```

### Coupon Tag (All Initial Items Free)

Make initial cards and booster packs free (but NOT rerolls or vouchers).

**Implementation**:
```python
# When Coupon Tag received:
run.coupon_tag_active = True

# In shop_phase():
if run.coupon_tag_active:
    # Make ALL initial items (jokers, consumables, packs) price=0
    # Does NOT affect reroll costs or voucher prices
    for item in initial_items:
        prices[item] = 0
    run.coupon_tag_active = False
```

### Voucher Tag (Extra Voucher)

Add one additional voucher to the shop:

**Implementation**:
```python
# When Voucher Tag received:
run.pending_tag_effects["voucher_tag_pending"] = True

# In shop_phase():
if "voucher_tag_pending" in run.pending_tag_effects:
    vouchers.append(generate_random_voucher())
    del run.pending_tag_effects["voucher_tag_pending"]
```

### D6 Tag (Free Rerolls)

Make reroll costs $0 in next shop:

**Implementation**:
```python
# When D6 Tag received:
run.pending_tag_effects["d6_tag_pending"] = True

# In shop_phase():
if "d6_tag_pending" in run.pending_tag_effects:
    reroll_cost = 0  # Apply when calculating shop costs
    del run.pending_tag_effects["d6_tag_pending"]
```

---

## Implementation Priority

### Phase 1: Core Booster Packs
1. ✅ Ante 1 Buffoon Pack guarantee
2. ✅ Booster Tag pack guarantees (Buffoon, Charm, etc.)
3. ⏳ Price logic (make guaranteed packs free/discounted)

### Phase 2: Joker Guarantees
1. ⏳ Edition tag application (Foil, Holographic, etc.)
2. ⏳ Rarity tag free jokers (Uncommon, Rare)
3. ⏳ Price logic for free jokers

### Phase 3: Other Modifiers
1. ⏳ Coupon Tag (all initial items free)
2. ⏳ Voucher Tag (extra voucher)
3. ⏳ D6 Tag (free rerolls)

---

## Data Flow Diagram

```
Tag Received (blind skip/win)
  ↓
Tag Handler sets run.pending_tag_effects[...] = True
  ↓
Player continues to next blind
  ↓
Blind Defeat → Tag effect applies
  ↓
shop_phase() reads pending_tag_effects
  ↓
Generate initial items + guaranteed items
  ↓
Apply Edition tags, Free joker counts, Coupon free items
  ↓
Return shop dict to player
```

---

## Testing Checklist

- [ ] Ante 1: Buffoon Pack always in first shop
- [ ] Buffoon Tag: Mega Buffoon appears, priced at 0
- [ ] Charm Tag: Mega Arcana appears, priced at 0
- [ ] Foil Tag: Random base-edition joker becomes Foil + free
- [ ] Rare Tag: 1 rare joker appears with price 0
- [ ] Coupon Tag: All 3 initial jokers + 2 initial consumables + 1 initial pack are free
- [ ] D6 Tag: Reroll costs $0 in next shop
- [ ] Voucher Tag: Extra voucher appears in shop

---

## Notes

- Tags only affect NEXT shop, then are consumed
- Multiple tags can stack (if Buffoon Tag + Coupon Tag: Mega Buffoon is free)
- Edition jokers (Foil/Holo/etc) should pick from base-edition jokers only
- Coupon Tag makes initial items free but NOT rerolls or vouchers
