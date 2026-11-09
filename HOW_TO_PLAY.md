# 📖 Shadows of Eldoria: Complete Player's Manual & Strategy Guide

Welcome, adventurer! This guide covers in-depth mechanics, strategies, class builds, and survival tips for both **Shadows of Eldoria 3D** and the **Terminal RPG Adventure**.

---

## 🗺️ Part 1: Shadows of Eldoria 3D (First-Person Action)

### 🕹️ Complete Controls Cheat Sheet

| Key / Input | Action | Tactical Usage |
| :--- | :--- | :--- |
| **W, A, S, D** | Move & Strafe | Keep moving during combat to dodge incoming enemy strikes. |
| **Mouse Move** | First-Person Look | Aim your camera at enemy heads or down corridors. |
| **Left Click (LMB)** | Sword Strike | Fast melee hit with knockback. Effective against single targets. |
| **Right Click / E** | Cast Fireball | Spends 15 MP. Deals heavy area-of-effect damage to clustered foes. |
| **Space** | Jump | Leap forward or bunny-hop backward away from heavy monster swings. |
| **Q** | Drink Potion | Restores 50 HP immediately. Best used when HP drops below 40%. |
| **F** | Interact | Opens golden treasure chests and activates dimensional portals. |
| **ESC** | Pause Menu | Unlocks the mouse cursor and pauses action. |

---

### ⚔️ Combat Tactics & Survival Tips

1. **Circle-Strafing & Kiting**:
   - Monsters charge in straight lines when they spot you.
   - Hold `W` + `A` or `W` + `D` while rotating your mouse to circle around enemies. Their melee swings will miss you while you slash their flanks.

2. **Fireball Group Management**:
   - Don't waste Fireballs on single isolated goblins.
   - When entering a new room with 2 or 3 monsters, let them bunch together near the doorway, then fire a Fireball directly at their feet. The explosive splash radius will damage all of them at once!

3. **Mana Regeneration**:
   - Mana automatically replenishes over time.
   - If you run out of mana, fall back and slash with your sword for a few seconds until your MP bar refills to 15.

4. **Reading the Overhead Health Bars**:
   - Every monster has a 3D red health bar floating above their head.
   - Target the monster with the lowest remaining HP first to reduce the number of incoming attacks quickly.

5. **Floor Portals**:
   - The purple rune portal only activates once you find the final chamber of the floor.
   - Always search side rooms for treasure chests **before** stepping through the portal, as you cannot travel backward once you descend.

---

### 💀 Enemy Bestiary & Boss Patterns

#### 1. Crypt Goblin (Floor 1 & 2)
- **Health**: 45 HP
- **Speed**: Fast
- **Attack**: 10 Damage
- **Behavior**: Fast and erratic. Vulnerable to sword knockback.

#### 2. Skeleton Guardian (Floor 2 & 3)
- **Health**: 70 HP
- **Speed**: Moderate
- **Attack**: 16 Damage
- **Behavior**: Armored undead with higher damage. Vulnerable to Fireball explosions.

#### 3. Lord Morzan, Void Sovereign (Floor 3 Boss)
- **Health**: 260 HP
- **Speed**: Steady
- **Attack**: 28 Damage
- **Strategy**: Keep your distance! Backpedal while casting Fireballs. When he closes in, jump sideways and slash twice, then immediately retreat. Drink potions as soon as you take a direct hit.

---

## 📜 Part 2: Terminal RPG Adventure (Turn-Based Strategy)

### 🛡️ Class Guides & Build Recommendations

#### 🛡️ The Warrior (Beginner Friendly)
- **Base Stats**: 130 HP, 40 MP, 14 ATK, 8 DEF
- **Strengths**: High survivability, mistakes are forgiven easily.
- **Key Skill**: *Shield Slam* (Stuns the enemy for 1 turn, giving you a free round of attacks).
- **Recommended Strategy**: Use *Shield Slam* early in the fight to disable enemy heavy attacks, then finish them off with *Iron Tempest*.

#### 🔮 The Mage (Glass Cannon)
- **Base Stats**: 90 HP, 90 MP, 16 ATK, 4 DEF
- **Strengths**: Tremendous spell damage and sustain.
- **Key Skill**: *Vampiric Drain* (Deals 130% damage and restores your HP by 75% of the damage dealt).
- **Recommended Strategy**: Alternate between *Hellfire Orb* (for burn damage) and *Vampiric Drain* to keep your HP topped off without spending health potions.

#### 🗡️ The Rogue (High Agility & Crits)
- **Base Stats**: 105 HP, 55 MP, 15 ATK, 5 DEF (High Speed & Dodge)
- **Strengths**: Frequent double damage critical strikes and high dodge rate.
- **Key Skill**: *Venomous Shiv* (Applies 3-turn stackable poison).
- **Recommended Strategy**: Poison the enemy on Turn 1, then use *Shadow Strike* for high crit finishes.

#### ☀️ The Paladin (Balanced Holy Crusader)
- **Base Stats**: 120 HP, 60 MP, 13 ATK, 7 DEF
- **Strengths**: Self-healing, status immunity, and high smite damage.
- **Key Skill**: *Holy Light* (Restores 65 HP and purges Burn/Poison).
- **Recommended Strategy**: Use *Radiant Smite* for burst damage and save *Holy Light* to counter enemy poison and burn effects.

---

### 🧩 Puzzle & Riddle Solutions

During your descent into the crypt in Terminal mode, you will encounter ancient monolith doors:

- **The Moon & Sun Door (Floor 1)**:
  - *Riddle*: "I have no flesh, no feathers... I follow you in sunlight, but vanish in the gloom. What am I?"
  - *Answer*: **A Shadow** (Option 2).
  - *Reward*: Twin Shadow Daggers + 40 Gold.

- **The Void Sphinx (Floor 3)**:
  - *Riddle*: "Feed me and I will live, give me a drink and I will die... What is my name?"
  - *Answer*: **Fire** (Option 1).
  - *Reward*: Legendary Dawnbringer blade + Elixir of Life.

---

## 🛠️ Frequently Asked Questions (FAQ)

### Q: Does the 3D game require an internet connection?
**No.** All Three.js libraries (`three.min.js`), shaders, 3D models, textures, and audio synthesizers (`audio.js`) are bundled locally within the project. It works 100% offline.

### Q: Why does the mouse cursor lock?
The 3D game uses the browser's standard **Pointer Lock API** to deliver smooth first-person camera control (just like desktop games). You can press <kbd>ESC</kbd> at any time to release the cursor.

### Q: Can I run this on Mac or Linux?
**Yes.** Both game modes are cross-platform:
- Mode 1 runs in any modern browser (Chrome, Safari, Firefox, Edge).
- Mode 2 runs on Python 3.8+ across Windows, macOS, and Linux terminals.

---

*May the light guide your blade through the dark depths of Eldoria!* ⚔️
