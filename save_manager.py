"""
save_manager.py - Persistent save/load system and Hall of Fame leaderboards.
"""

import json
import os
import time
from typing import Optional, Tuple, Dict, Any, List

from entities import Player
from utils import Colors


SAVE_FILE = "savegame.json"
HALL_OF_FAME_FILE = "hall_of_fame.json"


def save_exists() -> bool:
    """Check if a save file is present."""
    return os.path.exists(SAVE_FILE)


def save_game(player: Player, current_floor: int) -> bool:
    """Save player state and current dungeon floor to disk."""
    data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "floor": current_floor,
        "player": player.to_dict(),
    }
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"{Colors.RED}Failed to save game: {e}{Colors.RESET}")
        return False


def load_game() -> Optional[Tuple[Player, int]]:
    """Load player state and floor from disk."""
    if not save_exists():
        return None
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        player = Player.from_dict(data["player"])
        floor = data.get("floor", 1)
        return player, floor
    except Exception as e:
        print(f"{Colors.RED}Failed to load save file: {e}{Colors.RESET}")
        return None


def delete_save():
    """Remove current save game."""
    if os.path.exists(SAVE_FILE):
        try:
            os.remove(SAVE_FILE)
        except OSError:
            pass


def record_hall_of_fame(player: Player, won: bool):
    """Save run details to the Hall of Fame."""
    entry = {
        "date": time.strftime("%Y-%m-%d %H:%M"),
        "name": player.name,
        "class": player.player_class,
        "level": player.level,
        "battles_won": player.battles_won,
        "gold": player.gold,
        "status": "Vanquisher of Morzan (VICTOR)" if won else "Fallen in the Depths",
    }

    records = []
    if os.path.exists(HALL_OF_FAME_FILE):
        try:
            with open(HALL_OF_FAME_FILE, "r", encoding="utf-8") as f:
                records = json.load(f)
        except Exception:
            records = []

    records.insert(0, entry)
    records = records[:20]  # Keep top 20 entries

    try:
        with open(HALL_OF_FAME_FILE, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=4)
    except Exception:
        pass


def get_hall_of_fame() -> List[Dict[str, Any]]:
    """Retrieve all Hall of Fame entries."""
    if not os.path.exists(HALL_OF_FAME_FILE):
        return []
    try:
        with open(HALL_OF_FAME_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []
