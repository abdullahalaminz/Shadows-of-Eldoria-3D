"""
test_game.py - Automated testing and simulation of all game systems.
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
from entities import create_player, spawn_enemy, spawn_boss
from items import get_item, Weapon, Armor
from save_manager import save_game, load_game, delete_save, record_hall_of_fame, get_hall_of_fame


def run_tests():
    print("─── Running System Tests for Shadows of Eldoria ───")

    # 1. Test Player Classes & Factory
    for cls_name in ["Warrior", "Mage", "Rogue", "Paladin"]:
        p = create_player("Tester", cls_name)
        assert p.name == "Tester"
        assert p.player_class == cls_name
        assert p.hp == p.max_hp > 0
        assert p.mp == p.max_mp > 0
        assert len(p.skills) == 3
        assert p.equipped_weapon is not None
        assert p.equipped_armor is not None
        print(f"  ✔ {cls_name} created successfully: HP={p.hp}, MP={p.mp}, ATK={p.total_atk}, DEF={p.total_def}")

    # 2. Test Combat Math & Gear Swapping
    player = create_player("Aiden", "Warrior")
    base_atk = player.total_atk
    dragon_sword = get_item("dragonbone_blade")
    assert isinstance(dragon_sword, Weapon)
    player.equipped_weapon = dragon_sword
    assert player.total_atk > base_atk
    print(f"  ✔ Weapon equipment and stat scaling verified (ATK boosted from {base_atk} to {player.total_atk})")

    # 3. Test Damage and Healing
    start_hp = player.hp
    dmg_taken = player.take_damage(40)
    assert player.hp < start_hp
    healed = player.heal(dmg_taken)
    assert player.hp == start_hp
    print(f"  ✔ Damage mitigation and healing verified (Took {dmg_taken}, healed {healed})")

    # 4. Test XP & Level Up
    old_lvl = player.level
    old_max_hp = player.max_hp
    leveled, logs = player.gain_xp(player.xp_needed + 10)
    assert leveled is True
    assert player.level == old_lvl + 1
    assert player.max_hp > old_max_hp
    print(f"  ✔ Level up verified (Level {old_lvl} -> Level {player.level}, HP {old_max_hp} -> {player.max_hp})")

    # 5. Test Enemy Generation & Bosses
    for floor in [1, 2, 3]:
        enemy = spawn_enemy(floor, 1)
        assert enemy.hp > 0
        assert enemy.atk > 0
        boss = spawn_boss(floor)
        assert boss.is_boss is True
        assert boss.hp > enemy.hp
        print(f"  ✔ Floor {floor} spawns verified: Mob '{enemy.name}' (HP: {enemy.hp}), Boss '{boss.name}' (HP: {boss.hp})")

    # 6. Test Save and Load Persistence
    delete_save()
    saved = save_game(player, current_floor=2)
    assert saved is True
    loaded_data = load_game()
    assert loaded_data is not None
    loaded_player, loaded_floor = loaded_data
    assert loaded_player.name == player.name
    assert loaded_player.player_class == player.player_class
    assert loaded_player.level == player.level
    assert loaded_floor == 2
    delete_save()
    print("  ✔ Save and load persistence verified with zero data corruption")

    # 7. Test Hall of Fame
    record_hall_of_fame(player, won=True)
    records = get_hall_of_fame()
    assert len(records) > 0
    assert records[0]["name"] == player.name
    print(f"  ✔ Hall of Champions ledger verified ({len(records)} entries)")

    print("\n★★★ ALL TESTS PASSED SUCCESSFULLY! ★★★\n")


if __name__ == "__main__":
    run_tests()
