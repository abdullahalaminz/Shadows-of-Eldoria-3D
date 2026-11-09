"""
combat.py - Interactive turn-based tactical combat engine.
"""

import random
import time
from typing import Optional, Tuple

from entities import Player, Enemy, Skill
from items import Consumable, Weapon, Armor, get_item
from utils import (
    Colors,
    colorize,
    render_bar,
    print_box,
    slow_print,
    pause,
    clear_screen,
    SKULL_ART,
    SWORD_ART,
)


def run_combat(player: Player, enemy: Enemy) -> bool:
    """
    Executes a turn-based battle between player and enemy.
    Returns True if player wins, False if player dies or flees.
    """
    combat_log: list[str] = [
        f"{Colors.BRIGHT_RED}A hostile {enemy.name} emerges from the shadows!{Colors.RESET}",
        f"{Colors.ITALIC}'{enemy.name} {enemy.dialogue}'{Colors.RESET}"
    ]

    round_number = 1
    player.defending = False

    while player.hp > 0 and enemy.hp > 0:
        clear_screen()
        _render_battle_hud(player, enemy, round_number)

        # Print recent battle events
        print(f"\n{Colors.BOLD}─── Battle Log ────────────────────────────────────────{Colors.RESET}")
        for log in combat_log[-5:]:
            print(f"  {log}")
        print(f"{Colors.BOLD}───────────────────────────────────────────────────────{Colors.RESET}\n")

        # --- PLAYER TURN ---
        action_taken = False
        while not action_taken:
            print(f"{Colors.BOLD}Choose Action:{Colors.RESET}")
            print(f"  {Colors.BRIGHT_GREEN}[1]{Colors.RESET} Attack (Melee/Physical)")
            print(f"  {Colors.BRIGHT_CYAN}[2]{Colors.RESET} Cast Skill / Magic")
            print(f"  {Colors.BRIGHT_YELLOW}[3]{Colors.RESET} Use Inventory Item")
            print(f"  {Colors.BRIGHT_BLUE}[4]{Colors.RESET} Defend / Guard (+DEF, +5 MP)")
            if not enemy.is_boss:
                print(f"  {Colors.BRIGHT_MAGENTA}[5]{Colors.RESET} Attempt Escape")
            else:
                print(f"  {Colors.BRIGHT_BLACK}[5] Escape (Cannot flee from a Boss!){Colors.RESET}")

            choice = input(f"\n{Colors.BRIGHT_YELLOW}Action (1-5): {Colors.RESET}").strip()

            if choice == "1":
                # Standard Attack
                player.defending = False
                log_entry = _player_basic_attack(player, enemy)
                combat_log.append(log_entry)
                action_taken = True

            elif choice == "2":
                # Skills
                skill_used, log_entry = _player_skill_menu(player, enemy)
                if skill_used:
                    player.defending = False
                    combat_log.append(log_entry)
                    action_taken = True

            elif choice == "3":
                # Inventory
                item_used, log_entry = _player_inventory_menu(player, enemy)
                if item_used:
                    combat_log.append(log_entry)
                    action_taken = True

            elif choice == "4":
                # Defend
                player.defending = True
                mp_gain = player.restore_mp(6)
                combat_log.append(
                    f"{Colors.BRIGHT_BLUE}🛡 You raise your guard, bracing for impact (+DEF, restored {mp_gain} MP).{Colors.RESET}"
                )
                action_taken = True

            elif choice == "5":
                if enemy.is_boss:
                    print(f"{Colors.RED}The chamber is sealed by malevolent sorcery! You cannot flee!{Colors.RESET}")
                    time.sleep(1.2)
                    continue
                # Flee chance
                flee_chance = 0.45 + (player.speed - enemy.speed) * 0.03
                if random.random() < flee_chance:
                    print(f"\n{Colors.BRIGHT_YELLOW}💨 You threw down a flash of dust and managed to escape!{Colors.RESET}")
                    pause()
                    return False
                else:
                    combat_log.append(f"{Colors.RED}Escape failed! The enemy blocks your retreat!{Colors.RESET}")
                    action_taken = True

            else:
                print(f"{Colors.RED}Invalid option! Choose between 1 and 5.{Colors.RESET}")
                time.sleep(0.8)

        # Check if enemy was defeated by player's turn
        if enemy.hp <= 0:
            break

        # --- STATUS TICKS ON ENEMY ---
        status_msg = _process_status_effects(enemy, is_player=False)
        if status_msg:
            combat_log.append(status_msg)
        if enemy.hp <= 0:
            break

        # Check if enemy is stunned
        if enemy.status_effects.get("stun", 0) > 0:
            enemy.status_effects["stun"] -= 1
            combat_log.append(f"{Colors.BRIGHT_YELLOW}⚡ {enemy.name} is stunned and cannot move!{Colors.RESET}")
        else:
            # --- ENEMY TURN ---
            time.sleep(0.5)
            enemy_action = enemy.choose_action(player)
            
            # Check player dodge
            if random.random() < player.dodge_chance:
                combat_log.append(
                    f"{Colors.BRIGHT_GREEN}💨 You swiftly dodge {enemy.name}'s {enemy_action.name}! (DODGED){Colors.RESET}"
                )
            else:
                dmg_taken = player.take_damage(enemy_action.damage)
                crit_text = ""
                if enemy_action.action_type == "skill":
                    crit_text = f" {Colors.RED}★ SKILL ATTACK! ★{Colors.RESET}"

                combat_log.append(
                    f"{Colors.RED}⚔ {enemy.name} uses {enemy_action.name}! Deals {dmg_taken} damage to you.{crit_text}{Colors.RESET}"
                )

                # Apply enemy status to player
                if enemy_action.status and random.random() < 0.65:
                    player.status_effects[enemy_action.status] = enemy_action.status_turns
                    combat_log.append(
                        f"{Colors.BRIGHT_RED}☣ You have been afflicted with {enemy_action.status.upper()}!{Colors.RESET}"
                    )

        # --- STATUS TICKS ON PLAYER ---
        status_msg_p = _process_status_effects(player, is_player=True)
        if status_msg_p:
            combat_log.append(status_msg_p)

        # Handle temporary buff cooldowns
        if player.buff_turns > 0:
            player.buff_turns -= 1
            if player.buff_turns == 0:
                player.temp_atk_buff = 0
                player.temp_def_buff = 0
                combat_log.append(f"{Colors.DIM}Your temporary stat buffs have worn off.{Colors.RESET}")

        round_number += 1
        time.sleep(0.4)

    # --- BATTLE OUTCOME ---
    clear_screen()
    if player.hp <= 0:
        _render_defeat_screen(player, enemy)
        return False
    else:
        _render_victory_screen(player, enemy)
        return True


def _render_battle_hud(player: Player, enemy: Enemy, round_num: int):
    """Draw tactical HUD with enemy & player stats."""
    # Health bar colors
    e_ratio = enemy.hp / enemy.max_hp
    e_color = Colors.GREEN if e_ratio > 0.5 else (Colors.YELLOW if e_ratio > 0.25 else Colors.RED)

    p_ratio = player.hp / player.max_hp
    p_color = Colors.GREEN if p_ratio > 0.5 else (Colors.YELLOW if p_ratio > 0.25 else Colors.RED)

    # Format status badges
    e_statuses = " ".join([f"[{k.upper()}:{v}]" for k, v in enemy.status_effects.items() if v > 0])
    p_statuses = " ".join([f"[{k.upper()}:{v}]" for k, v in player.status_effects.items() if v > 0])
    if player.buff_turns > 0:
        p_statuses += f" [BUFF:{player.buff_turns}]"

    border = Colors.BRIGHT_RED if enemy.is_boss else Colors.CYAN
    title = f"★ BOSS ENCOUNTER: {enemy.name.upper()} ★" if enemy.is_boss else f"BATTLE: Round {round_num}"

    lines = [
        f"{Colors.BOLD}{enemy.name}{Colors.RESET} ({enemy.enemy_type}) {Colors.BRIGHT_YELLOW}{e_statuses}{Colors.RESET}",
        f"HP:  {render_bar(enemy.hp, enemy.max_hp, 22, e_color)}",
        f"ATK: {enemy.atk}  │  DEF: {enemy.defense}  │  SPD: {enemy.speed}",
        "─" * 60,
        f"{Colors.BOLD}{player.name} the {player.player_class}{Colors.RESET} (Lvl {player.level}) {Colors.BRIGHT_GREEN}{p_statuses}{Colors.RESET}",
        f"HP:  {render_bar(player.hp, player.max_hp, 22, p_color)}",
        f"MP:  {render_bar(player.mp, player.max_mp, 22, Colors.CYAN)}",
        f"ATK: {player.total_atk} (Base {player.base_atk})  │  DEF: {player.total_def}  │  GOLD: {player.gold}",
    ]
    print_box(lines, title=title, border_color=border, width=66)


def _player_basic_attack(player: Player, enemy: Enemy) -> str:
    """Executes a standard attack with critical chance."""
    is_crit = random.random() < player.crit_chance
    dmg_mult = 1.75 if is_crit else 1.0

    raw_dmg = int(player.total_atk * random.uniform(0.9, 1.15) * dmg_mult)
    actual_dmg = enemy.take_damage(raw_dmg)

    crit_tag = f" {Colors.BRIGHT_YELLOW}★ CRITICAL HIT! ★{Colors.RESET}" if is_crit else ""
    return f"{Colors.BRIGHT_GREEN}⚔ You strike {enemy.name} for {actual_dmg} damage!{crit_tag}{Colors.RESET}"


def _player_skill_menu(player: Player, enemy: Enemy) -> Tuple[bool, str]:
    """Displays skill selection and processes cast."""
    print(f"\n{Colors.BOLD}─── Skill Selection (Current MP: {player.mp}/{player.max_mp}) ───{Colors.RESET}")
    for idx, skill in enumerate(player.skills, 1):
        cost_color = Colors.CYAN if player.mp >= skill.mp_cost else Colors.RED
        print(f"  [{idx}] {Colors.BOLD}{skill.name}{Colors.RESET} - Cost: {cost_color}{skill.mp_cost} MP{Colors.RESET}")
        print(f"      {Colors.DIM}{skill.description}{Colors.RESET}")
    print(f"  [0] {Colors.YELLOW}Back to Battle Actions{Colors.RESET}")

    choice = input(f"\nSelect skill (1-{len(player.skills)} or 0): ").strip()
    if choice == "0":
        return False, ""

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(player.skills):
            skill = player.skills[idx]
            if player.mp < skill.mp_cost:
                print(f"{Colors.RED}Not enough MP! (Requires {skill.mp_cost} MP){Colors.RESET}")
                time.sleep(1)
                return False, ""

            player.mp -= skill.mp_cost

            # Execute Skill
            if skill.skill_type == "damage":
                dmg = int(player.total_atk * skill.multiplier * random.uniform(0.95, 1.1))
                actual_dmg = enemy.take_damage(dmg)
                status_str = ""
                if skill.status_effect and random.random() < 0.70:
                    enemy.status_effects[skill.status_effect] = skill.status_turns
                    status_str = f" {Colors.BRIGHT_YELLOW}Afflicted with {skill.status_effect.upper()}!{Colors.RESET}"

                return True, f"{Colors.BRIGHT_CYAN}✨ You cast {skill.name}! Inflicts {actual_dmg} damage!{status_str}{Colors.RESET}"

            elif skill.skill_type == "heal":
                healed = player.heal(int(player.max_hp * 0.45) + 15)
                player.temp_atk_buff += 4
                player.buff_turns = max(player.buff_turns, 3)
                return True, f"{Colors.BRIGHT_GREEN}🌿 You invoke {skill.name}! Restored {healed} HP and gained +4 ATK!{Colors.RESET}"

            elif skill.skill_type == "drain":
                dmg = int(player.total_atk * skill.multiplier)
                actual_dmg = enemy.take_damage(dmg)
                drain_heal = player.heal(int(actual_dmg * 0.75))
                return True, f"{Colors.MAGENTA}🔮 You unleash {skill.name}! Dealt {actual_dmg} damage and absorbed {drain_heal} HP!{Colors.RESET}"

            elif skill.skill_type == "buff":
                player.temp_def_buff += 12
                player.buff_turns = 3
                return True, f"{Colors.BRIGHT_BLUE}🛡 You invoke {skill.name}! Defense heavily bolstered (+12 DEF for 3 turns)!{Colors.RESET}"

    except ValueError:
        pass

    return False, ""


def _player_inventory_menu(player: Player, enemy: Enemy) -> Tuple[bool, str]:
    """Displays usable items in combat."""
    consumables = []
    for item_id, count in player.inventory.items():
        item = get_item(item_id)
        if isinstance(item, Consumable):
            consumables.append((item, count))

    if not consumables:
        print(f"{Colors.RED}You have no usable combat items in your pack!{Colors.RESET}")
        time.sleep(1.0)
        return False, ""

    print(f"\n{Colors.BOLD}─── Battle Inventory ───{Colors.RESET}")
    for idx, (item, count) in enumerate(consumables, 1):
        print(f"  [{idx}] {item.name} x{count} - {Colors.DIM}{item.description}{Colors.RESET}")
    print(f"  [0] {Colors.YELLOW}Back to Actions{Colors.RESET}")

    choice = input(f"\nUse item (1-{len(consumables)} or 0): ").strip()
    if choice == "0":
        return False, ""

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(consumables):
            item, _ = consumables[idx]
            player.remove_item(item.id, 1)

            if item.effect == "heal_hp":
                amt = player.heal(item.power)
                return True, f"{Colors.BRIGHT_GREEN}🧪 You drink {item.name}, regaining {amt} HP!{Colors.RESET}"
            elif item.effect == "heal_mp":
                amt = player.restore_mp(item.power)
                return True, f"{Colors.BRIGHT_CYAN}🧪 You drink {item.name}, recovering {amt} MP!{Colors.RESET}"
            elif item.effect == "buff_atk":
                player.temp_atk_buff += item.power
                player.buff_turns = max(player.buff_turns, item.duration)
                return True, f"{Colors.BRIGHT_YELLOW}⚡ You quaff {item.name}! ATK increased by +{item.power} for {item.duration} turns!{Colors.RESET}"
            elif item.effect == "buff_def":
                player.temp_def_buff += item.power
                player.buff_turns = max(player.buff_turns, item.duration)
                return True, f"{Colors.BRIGHT_BLUE}🛡 You quaff {item.name}! DEF increased by +{item.power} for {item.duration} turns!{Colors.RESET}"
            elif item.effect == "bomb":
                dmg = enemy.take_damage(item.power)
                return True, f"{Colors.BRIGHT_RED}💣 You hurl {item.name}! BOOM! Deals {dmg} explosive damage!{Colors.RESET}"

    except ValueError:
        pass

    return False, ""


def _process_status_effects(entity, is_player: bool) -> str:
    """Tick down status conditions (burn, poison)."""
    messages = []
    name = "You" if is_player else entity.name

    if entity.status_effects.get("burn", 0) > 0:
        burn_dmg = 8
        if is_player:
            entity.hp = max(0, entity.hp - burn_dmg)
        else:
            entity.take_damage(burn_dmg)
        entity.status_effects["burn"] -= 1
        messages.append(f"{Colors.BRIGHT_RED}🔥 {name} suffered {burn_dmg} fire damage from Burn!{Colors.RESET}")

    if entity.status_effects.get("poison", 0) > 0:
        poison_dmg = 10
        if is_player:
            entity.hp = max(0, entity.hp - poison_dmg)
        else:
            entity.take_damage(poison_dmg)
        entity.status_effects["poison"] -= 1
        messages.append(f"{Colors.BRIGHT_GREEN}☣ {name} suffered {poison_dmg} poison damage from Venom!{Colors.RESET}")

    return " ".join(messages)


def _render_victory_screen(player: Player, enemy: Enemy):
    """Celebratory victory summary and rewards."""
    player.battles_won += 1
    if enemy.is_boss:
        player.bosses_defeated += 1

    player.gold += enemy.gold_reward

    print(SWORD_ART)
    print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}═══════════════════ VICTORY ACHIEVED! ═══════════════════{Colors.RESET}")
    print(f"You have vanquished {Colors.BOLD}{enemy.name}{Colors.RESET}!")
    print(f"  • Spoils of War: {Colors.BRIGHT_YELLOW}+{enemy.gold_reward} Gold{Colors.RESET} (Total: {player.gold})")
    print(f"  • Experience:    {Colors.BRIGHT_CYAN}+{enemy.xp_reward} XP{Colors.RESET}")

    # Check Level Up
    leveled, level_logs = player.gain_xp(enemy.xp_reward)
    if leveled:
        print()
        for log in level_logs:
            print(log)

    # Loot drops
    loot_dropped = []
    for item_id, drop_chance in enemy.loot_table:
        if random.random() <= drop_chance:
            loot_item = get_item(item_id)
            if loot_item:
                player.add_item(item_id, 1)
                loot_dropped.append(loot_item.name)

    if loot_dropped:
        print(f"\n{Colors.BRIGHT_YELLOW}Loot Recovered:{Colors.RESET}")
        for item_name in loot_dropped:
            print(f"  🎁 Found: {Colors.BOLD}{item_name}{Colors.RESET}")

    pause()


def _render_defeat_screen(player: Player, enemy: Enemy):
    """Defeat screen when player HP hits 0."""
    print(SKULL_ART)
    print(f"\n{Colors.BRIGHT_RED}{Colors.BOLD}═══════════════════ YOU HAVE FALLEN ═══════════════════{Colors.RESET}")
    print(f"Your light was snuffed out in the dark depths by {enemy.name}.")
    print(f"Your deeds in Eldoria will be remembered only in whispers...")
    print(f"{Colors.DIM}Stats: Level {player.level} {player.player_class} | Battles Won: {player.battles_won}{Colors.RESET}")
    pause("\nPress [ENTER] to return to the mortal realm...")
