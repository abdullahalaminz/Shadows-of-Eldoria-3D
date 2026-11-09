# ⚔️ Shadows of Eldoria: The Sunken Crypt 🏰

[![Python Version](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![WebGL / Three.js](https://img.shields.io/badge/WebGL-Three.js_r128-049EF4?style=for-the-badge&logo=three.js&logoColor=white)](https://threejs.org/)
[![Performance](https://img.shields.io/badge/Performance-60_FPS_GPU_Instanced-22c55e?style=for-the-badge&logo=speedtest&logoColor=white)](#performance-optimizations)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero_Install-f59e0b?style=for-the-badge)](#quick-start)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

> A dual-mode dark-fantasy RPG featuring a **real-time 3D First-Person Action Dungeon Crawler** (WebGL / Three.js) and a **classic tactical Turn-Based Terminal RPG** (pure Python standard library).

---

## 📑 Table of Contents

- [🎮 Game Modes Overview](#-game-modes-overview)
- [⚡ Quick Start (Play in 5 Seconds)](#-quick-start-play-in-5-seconds)
- [🕹️ Mode 1: 3D First-Person Action (Browser)](#️-mode-1-3d-first-person-action-browser)
  - [Controls Reference](#controls-reference)
  - [Step-by-Step Gameplay Walkthrough](#step-by-step-gameplay-walkthrough)
  - [Combat & Spells Guide](#combat--spells-guide)
  - [Dungeon Secrets & Boss Encounter](#dungeon-secrets--boss-encounter)
- [📜 Mode 2: Tactical Terminal RPG (Python)](#-mode-2-tactical-terminal-rpg-python)
  - [4 Hero Archetypes](#4-hero-archetypes)
  - [Turn-Based Battle Mechanics](#turn-based-battle-mechanics)
- [🚀 Hosting on GitHub Pages (Play Online for Free)](#-hosting-on-github-pages-play-online-for-free)
- [📂 Project Architecture](#-project-architecture)
- [⚙️ Performance & Engine Features](#️-performance--engine-features)

---

## 🎮 Game Modes Overview

| Feature | 🌟 Mode 1: 3D Action Dungeon | 📜 Mode 2: Terminal RPG |
| :--- | :--- | :--- |
| **Perspective** | First-Person 3D (WASD + Mouse Look) | Text-based Tactical Interface |
| **Combat Style** | Real-time Hack & Slash + Fireball Spells | Turn-based Strategy & MP Abilities |
| **Engine** | WebGL / Three.js (PBR Shaders) | Pure Python Standard Library |
| **Audio** | Real-time Web Audio API Synthesizer | ASCII UI & Visual Indicators |
| **Platform** | Any Browser (Chrome, Edge, Firefox, Safari) | Windows Terminal, macOS, Linux Shell |
| **Installation** | **Zero install** (Open in browser) | **Zero install** (`python main.py`) |

---

## ⚡ Quick Start (Play in 5 Seconds)

### Play Mode 1 (3D Action Game):
Double-click `index.html` in your browser, or start the local server:
```bash
python launch_3d.py
```
*Direct URL: [http://localhost:8000/index.html](http://localhost:8000/index.html)*

### Play Mode 2 (Terminal RPG):
Run with Python (no `pip install` required):
```bash
python main.py
```

To run the automated test & balance suite:
```bash
python test_game.py
```

---

## 🕹️ Mode 1: 3D First-Person Action (Browser)

Step inside the 3D stone corridors of the Sunken Crypt with real-time lighting, sword slashes, explosive fireball spells, 3D animated enemies, and dynamic minimap.

### Controls Reference

| Action | Control Key | Description |
| :--- | :--- | :--- |
| **Move / Strafe** | <kbd>W</kbd> <kbd>A</kbd> <kbd>S</kbd> <kbd>D</kbd> or <kbd>↑</kbd> <kbd>←</kbd> <kbd>↓</kbd> <kbd>→</kbd> | Walk forward, backward, and strafe left/right |
| **Look Around** | **Mouse Movement** | Smooth first-person camera rotation |
| **Lock / Unlock Mouse** | **Left Click** / <kbd>ESC</kbd> | Click canvas to lock cursor; press ESC to pause |
| **Sword Slash** | **Left Mouse Button (LMB)** | Swing your Damascus steel blade in close melee |
| **Cast Fireball** | **Right Mouse Button (RMB)** or <kbd>E</kbd> | Launch an explosive fireball (15 MP, AoE splash) |
| **Jump** | <kbd>Spacebar</kbd> | Leap over obstacles or evade attacks |
| **Heal** | <kbd>Q</kbd> | Consume a Health Potion (+50 HP restored) |
| **Interact / Open** | <kbd>F</kbd> | Open treasure chests and enter floor portals |

---

### Step-by-Step Gameplay Walkthrough

#### Step 1: Entering the Crypt
1. Open `index.html` in your browser.
2. Click the glowing **"ENTER THE CRYPT"** button. This will lock your mouse cursor into first-person view.
3. Your HUD displays your **HP (Health)**, **MP (Mana)**, **XP Level**, **Floor Number**, **Gold**, and a **Real-Time Minimap**.

#### Step 2: Exploring Corridors & Reading the Minimap
- The circular radar in the top-right corner is your **Minimap**:
  - 🔵 **Cyan Arrow**: Your current location and view angle.
  - 🔴 **Red Dots**: Nearby wandering monsters.
  - 🟡 **Yellow Dots**: Unopened treasure chests.
- Follow the stone corridors illuminated by your personal brass lantern and warm wall torches.

#### Step 3: Combat with Monsters
- When an enemy spots you, they will rush to attack:
  - **Goblins (Green)**: Fast-moving scavengers with spiked clubs. Keep your distance or strike first.
  - **Skeletons (Bone White)**: Tougher undead knights wielding rusted broadswords with cyan eye embers.
  - **Lord Morzan (Boss on Floor 3)**: A giant dark-plate sovereign wielding a flaming demonic claymore!
- **Overhead 3D Health Bars**: Each monster displays a real-time floating health bar above their head so you always know their remaining vitality.
- **Melee Combat**: Time your sword swings (**Left Click**). When hit, enemies flash white and suffer knockback.
- **Ranged Magic**: Cast Fireballs (**Right Click** or <kbd>E</kbd>) to blast groups from a distance.

#### Step 4: Looting & Recovering Vitality
- Approach ornate wooden chests and press <kbd>F</kbd> to unlock them for gold coins and extra potions.
- When low on health, tap <kbd>Q</kbd> to drink a Health Potion.
- Your Mana (MP) naturally regenerates over time.

#### Step 5: Descending to the Next Floor
- Clear the monsters in the room and locate the glowing **Purple Rune Portal**.
- Stand near the portal and press <kbd>F</kbd> to descend deeper into the crypt:
  - **Floor 1**: The Crypt Entrance
  - **Floor 2**: The Catacombs (Deadlier Skeletons & tougher layouts)
  - **Floor 3**: Sanctum of the Void (Final confrontation with Lord Morzan!)

---

## 📜 Mode 2: Tactical Terminal RPG (Python)

A pure Python turn-based text adventure with branching story events, puzzles, and persistent auto-saves.

### 4 Hero Archetypes

1. 🛡️ **Warrior**: Massive HP and physical defense. Abilities: *Shield Slam* (Stun), *Iron Tempest* (Heavy AOE slash), *War Cry* (Heal & ATK buff).
2. 🔮 **Mage**: High mana pool and devastating magic burst. Abilities: *Arcane Missiles*, *Hellfire Orb* (Burns target), *Vampiric Drain* (Life steal).
3. 🗡️ **Rogue**: Fast speed, high critical strike chance, and evasion. Abilities: *Shadow Strike*, *Venomous Shiv* (Poison DOT), *Vanish in Smoke*.
4. ☀️ **Paladin**: Holy frontline fighter with strong defense and healing. Abilities: *Radiant Smite*, *Holy Light* (Heal & cure status), *Divine Bastion*.

### Turn-Based Battle Mechanics
- **Combat Menu**: Select `[1] Attack`, `[2] Skills`, `[3] Inventory`, `[4] Guard`, or `[5] Flee`.
- **Active Guarding**: Raising your shield cuts incoming damage by up to 50% and restores MP.
- **Status Effects**: Enemies and players can suffer from **Burn (🔥)**, **Poison (☣)**, and **Stun (⚡)**.
- **Wandering Peddler (Grimbold)**: Encounter merchant chambers to buy potions, better armors, and sell unwanted loot.
- **Persistent Saves**: Auto-saves after every chamber to `savegame.json`, with a persistent `hall_of_fame.json` leaderboard.

---

## 🚀 Hosting on GitHub Pages (Play Online for Free)

Because the 3D game uses client-side WebGL and bundles `three.min.js` locally, you can host it **for free on GitHub Pages** so anyone can play from their phone or browser without installing anything!

### How to Enable GitHub Pages:
1. Push this repository to your GitHub account:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Shadows of Eldoria 3D"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
   git push -u origin main
   ```
2. On GitHub, navigate to **Settings** ➔ **Pages** (under "Code and automation").
3. Under **Build and deployment** ➔ **Branch**:
   - Select **`main`** branch.
   - Folder: **`/ (root)`**.
   - Click **Save**.
4. Within 1-2 minutes, GitHub will give you a live URL:
   `https://YOUR_USERNAME.github.io/YOUR_REPOSITORY/`

Anyone who clicks the link can play the full 3D game instantly in their web browser!

---

## 📂 Project Architecture

```text
.
├── index.html          # WebGL 3D game shell & HTML5 HUD overlay
├── style.css           # Glassmorphism UI styling, health/mana bars, minimap
├── game3d.js           # Three.js 3D engine: procedural dungeon, physics, AI
├── audio.js            # Synthesized retro audio engine (Web Audio API)
├── three.min.js        # Local standalone Three.js engine (100% offline capable)
├── launch_3d.py        # Python 1-click launcher for local HTTP server
│
├── main.py             # Terminal RPG main loop & hero creation
├── entities.py         # Player classes, stats, leveling, enemy AI, bosses
├── combat.py           # Turn-based combat engine with tactical HUD
├── story.py            # Dungeon floors, riddles, shrines, merchant shop
├── items.py            # Weapons, armors, potions catalog & loot tables
├── save_manager.py     # JSON save/load persistence & Hall of Champions
├── utils.py            # ANSI colors, health bars, and ASCII banners
└── test_game.py        # Automated test suite (classes, math, persistence)
```

---

## ⚙️ Performance & Engine Features

- **GPU Instanced Meshes (`THREE.InstancedMesh`)**: All 300+ dungeon stone wall blocks are rendered in **1 single GPU draw call**, guaranteeing silky-smooth 60 FPS even on entry-level laptops and integrated GPUs.
- **Physically-Based Rendering (PBR)**: Realistic stone masonry and flagstone paving with custom bump maps and roughness maps.
- **Wet Floor Specular Reflections**: Real-time glossy water puddles on the dungeon floor that reflect flickering torchlight.
- **Dynamic Minimap Radar**: Real-time canvas radar tracking player orientation and nearby entities.
- **Synthesized Web Audio**: Realistic procedural sound effects (sword whooshes, impacts, fireball whistles, explosions, potion sips) generated on-the-fly via mathematical oscillators without needing large `.mp3` downloads.
- **Zero External Dependencies**: Works out-of-the-box on Windows, macOS, and Linux without needing `pip install` or `npm install`.

---

## 📜 License

This project is open-source under the [MIT License](LICENSE). Feel free to modify, expand, or build your own custom levels and dungeons!
