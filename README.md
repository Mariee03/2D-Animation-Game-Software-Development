# Castles and War – 2D Strategy Game ⚔️🏰

**Castles and War** is a 2D multiplayer resource-management and tower-defense strategy game built in **Python with Pygame**. Two players compete to mine resources, build units (workers, swordsmen, archers), and destroy the opponent’s wall. The game features animated characters, strategic mechanics, and real-time battle logic.

> Created by Marie Elyse Bassil & Kiana Naidu

---

## 🎯 Objective

The game simulates a medieval conflict scenario where each player must:
- Collect resources by sending workers to mines
- Train military units
- Defend their wall while attempting to destroy the opponent’s wall
- Win by depleting the opponent’s wall health to zero

---

## 🧩 Structure

The game is made up of three files:

| File | Purpose |
|------|---------|
| `object.py` | Contains all class definitions (Animation, Object, Entity, Worker, Swordsman, Archer, Tower) |
| `game.py` | Controls game loop, event handling, drawing, combat logic, and animations |
| `commands.txt` | A reference for in-game keyboard controls |

---

## 🕹️ Gameplay Features

- 🛡️ Two-player strategy with alternating turns
- ⛏️ Resource mining and worker deployment
- ⚔️ Unit training (archers, swordsmen)
- 🏹 Real-time combat animation with arrows and melee logic
- 📜 Keyboard-based command input (see `commands.txt`)
- 🎮 Game-over conditions based on wall destruction or resource depletion

---

## 🧱 Object-Oriented Design

### Classes Defined:
- `Animation`: Loads and manages sprite frames and animation rate
- `Object`: Base class for all visual game objects
- `Entity`: Base class for all moving or interactive game units
- `Worker`, `Swordsman`, `Archer`, `Tower`: Extend `Entity` with custom behavior and animations

---

## 🔁 Game Loop & Logic

- Each turn, players can:
  - Train units
  - Deploy them to the mine or wall
  - Skip a turn
- Unit animations, resource management, and attacks are handled via sprite updates and collision detection
- Combat includes:
  - Melee (swordsman) and ranged (archer) attacks
  - Animations for moving, attacking, resting
- Victory is determined when one wall's health drops to 0

---

## 🎨 Controls

See `commands.txt` for full list. Examples:

- `Q` / `P`: Train worker
- `A` + `L`: Deploy worker
- `Left Shift` / `Right Shift`: End turn
- `Arrows` / `WASD`: Control unit movement

---

## 🚀 How to Run

1. Clone the repo:
```bash
git clone https://github.com/Mariee03/2D-Animation-Game-Software-Development.git
cd 2D-Animation-Game-Software-Development
```

2. Install Pygame:
```bash
pip install pygame
```

3.Run the game:
```bash
python game.py
```
Make sure object.py and commands.txt are in the same directory.

## 📬 Authors

Created by:

Marie Elyse Bassil
Kiana Naidu
