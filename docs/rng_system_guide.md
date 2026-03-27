# Understanding Pylatro's RNG System

Welcome! This guide explains how randomness works in Pylatro and how seeds ensure you can replay the same game every time.

---

## What is RNG?

**RNG** stands for **Random Number Generation**. It's what makes games unpredictable—determining which jokers appear in shops, what cards you draw, which blinds you face, and more.

### Key Concept: Seeding

A **seed** is a special code (like `7LB2WVPK`) that completely controls all the randomness in a run. Same seed = same cards, same shop items, same everything. Different seed = completely different game.

**Why this matters:**
- You can share a seed with friends to play the exact same game
- You can practice against the same blind multiple times
- The game records which seed you used, so you can prove your score wasn't fluky

---

## How Seeds Work

### The Seed System

When you start a new run, the game either:
1. **Generates a random seed** for you (like tossing a die multiple times)
2. **Uses a seed you entered** (like typing in a code)

Once the seed is set, **every random decision** that follows is predetermined.

**Think of it like this:**
> Imagine a cookbook where each recipe says "Step 1: Shake the salt shaker exactly 3 times." If you always shake it 3 times, you always get the same amount of salt—even though it looks random.

The seed lets you "shake the salt shaker 3 times" the exact same way twice.

### Seed Format

- **Length:** 1-8 characters
- **Characters:** Uppercase letters and numbers
- **No zeros:** The system uses "O" (letter O) instead of "0" (zero) to avoid confusion
- **Examples:** `7LB2WVPK`, `ABC123`, `HELLO`

---

## What Gets Randomized?

### Major RNG Events

Here are the big moments where randomness matters:

#### 1. **Card Draws**
- Which cards you get from your deck when you draw a hand
- Erratic Deck: card suits and ranks are randomized

#### 2. **Shop Items**
- Which jokers appear in the shop
- How rare they are (common vs. legendary)
- Which consumables (tarot cards, planets, etc.) are available
- What happens when you reroll

#### 3. **Joker Effects**
- 8 Ball: 1-in-4 chance to create a Tarot card
- Business Card: 1-in-2 chance to give you $2 per face card
- Misprint: Randomly adds 0-23 multiplier
- And many more...

#### 4. **Boss Blind Selection**
- Which boss blind appears in each ante
- (Example: Will you face "The Hook" or "The Wheel"?)

#### 5. **Consumable Pulls**
- Random selections from Tarot cards, Planets, and Spectrals
- Triggered by consumable use or joker abilities

#### 6. **Deck Generation**
- For Erratic Deck: randomizes all card suits and ranks

---

## Where Randomness Comes From

### Items That Can Be Randomized

The system pulls random selections from these pools:

#### **Jokers**
- **By Rarity:** Common (most frequent) → Uncommon → Rare → Legendary (rare finds)
- **By Unlock Status:** Some jokers are locked until you meet unlock conditions
- **Example:** Early runs see mostly common jokers; later runs have access to rarer ones

#### **Consumables**
- **Tarot Cards:** Used to modify your game state (upgrade cards, create enhancements, etc.)
- **Planets:** Upgrade your poker hand types
- **Spectral Cards:** Create special effects

#### **Boss Blinds**
- Different challenges appear based on the ante
- Each ante has a pool of available blinds

#### **Card Enhancements & Seals**
- Random modifications to cards (like "Foil" or "Glass")
- Applied through consumables or joker abilities

---

## Profile Unlocks & What You See

### Unlocking Content

Not everything appears in your first game. You need to "unlock" items by:
- Winning runs
- Playing hands
- Meeting other conditions

### How Randomness Works With Unlocks

When the RNG system generates shop items, it:

1. **Checks your unlock status**
2. **Only picks from items you've unlocked**
3. **Generates the random selection**

**In practice:**
- Early game: You see mostly common starting jokers
- Later: You see rare jokers once you've earned them
- Legendary jokers: Only available through the Soul card consumable

---

## Understanding Seeded Runs

### Starting a Seeded Run

**Option 1: Automatic**
- Start a run normally → the game generates a random seed → it's recorded

**Option 2: Manual (Same Game Replay)**
- Enter a seed code you used before → play the exact same game again

### Why Play With the Same Seed?

1. **Practice:** Face the same blinds and shops to improve
2. **Documentation:** Prove a score is legit (with seed verification)
3. **Sharing:** Challenge friends: "Can you beat my seed?"
4. **Science:** Test if you're actually better or just got lucky

### What Stays the Same?

- ✅ Cards you draw
- ✅ Shop items (jokers, consumables, vouchers)
- ✅ Boss blinds
- ✅ Joker ability random triggers
- ✅ Consumable effects

---

## RNG Events Timeline

Here's roughly when randomness applies during a run:

```
RUN START
  └─ Random deck card ordering (if Erratic Deck)

EACH ANTE
  └─ Random boss blind selection

EACH BLIND START
  └─ Random shop generation
      ├─ Random joker selection by rarity
      └─ Random consumable selection

EACH HAND
  ├─ Random card draws from deck
  ├─ Joker ability random triggers (1/4, 1/2 chances, etc.)
  └─ Consumable random selections (tarots, planets, etc.)

BLIND DEFEAT
  └─ Random tag selection to offer you
```

---

## Advanced: How Shops Handle Rerolls

### The Reroll System

When you use a reroll consumable or encounter Chaos the Clown:

1. **First generation:** Items get seeds `item0`, `item1`, `item2`
2. **After one item sells:** New item gets seed `item2` (continues numbering)
3. **Full reroll:** Items reset to `item0`, `item1`, `item2`, and reroll counter increments
4. **Each reroll:** Uses a fresh set of random seeds

**Why this matters:**
- Same seed = same shop behavior every time
- If you know a shop will have "bad" items, you can plan around it
- Rerolling follows a predictable pattern

---

## Creating Reports From Seeds

### Run Verification

When you finish a run with a seed, the system can:
- **Generate a report:** Lists all random decisions that happened
- **Create a hash:** A unique fingerprint verifying the seed and result
- **Enable replay:** Someone can enter the seed and verify your exact path

### What Gets Logged

- Which seed was used
- Cards drawn each hand
- Shop items offered
- Joker ability triggers
- Random selections from consumables

---

## Cheating vs. Legitimate Play

### What You CAN'T Cheat With Seeds

- **Can't pick your own items:** The seed determines everything before you play
- **Can't know the future:** You discover items as you play, same as everyone else
- **Can't control RNG mid-game:** Restarting or reloading doesn't change the seed

### What Seeds PREVENT

- Claiming a lucky run was skill: You can verify the seed/result publicly
- Modifying your score: The seed is the "proof" of what happened
- Claiming impossible results: Others can replay your seed

---

## FAQ

### Q: Can I choose what items appear by picking a certain seed?

**A:** Not practically. Seeds are essentially random. While theoretically you could search for a seed with specific items, it would take impossibly long times. Players just use whatever seed appears.

### Q: If I restart mid-run, does the seed change?

**A:** No. The seed is set at run start. Restarting loads you back to where you were—same seed, same results.

### Q: Why use "O" instead of "0" in seeds?

**A:** Avoids confusion when reading/typing seeds (like confusing "O" with "0" in common fonts).

### Q: Can different people get the same seed?

**A:** Yes, theoretically. But there are so many possible combinations that it's extremely rare randomly.

### Q: What if I want to play a completely random game?

**A:** Just start normally without entering a seed. The game generates a new random seed for you.

---

## Coming Soon in Pylatro

The RNG system is currently being developed to handle:
- ✅ Seed storage and replay
- 🔄 Shop generation with rarity filtering
- 🔄 Booster pack generation
- 🔄 Boss blind cycling
- 🔄 Joker ability random triggers
- 🔄 Run verification and reporting

Check back for updates as these features roll out!

---

## Need Help?

- **Want to understand deck generation?** See [Decks & Card Types](deck_guide.md)
- **Want to learn about jokers?** See [Joker System Guide](joker_guide.md)
- **Want to explore consumables?** See [Tarot & Consumables Guide](consumables_guide.md)
