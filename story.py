"""
story.py - Dungeon exploration, story rooms, puzzles, wandering merchant, and shrines.
"""

import random
import time
from typing import Optional

from entities import Player, spawn_enemy, spawn_boss
from combat import run_combat
from items import Weapon, Armor, Consumable, get_item, ITEM_REGISTRY
from utils import (
    Colors,
    colorize,
    clear_screen,
    pause,
    slow_print,
    print_box,
    render_bar,
    TREASURE_ART,
    SWORD_ART,
)


def run_dungeon_floor(player: Player, floor: int) -> bool:
    """
    Runs a complete floor of the dungeon.
    Returns True if floor is cleared, False if player dies or quits.
    """
    floor_names = {
        1: "Floor 1: The Overgrown Crypt Entrance",
        2: "Floor 2: The Forgotten Catacombs",
        3: "Floor 3: Sanctum of the Void",
    }
    floor_name = floor_names.get(floor, f"Floor {floor}")

    clear_screen()
    print(f"\n{Colors.BRIGHT_MAGENTA}{Colors.BOLD}═════════════════════════════════════════════════════════{Colors.RESET}")
    print(f"             DESCENDING INTO {floor_name.upper()}")
    print(f"{Colors.BRIGHT_MAGENTA}{Colors.BOLD}═════════════════════════════════════════════════════════{Colors.RESET}\n")

    if floor == 1:
        slow_print("The ancient iron gate groans open. Damp air smelling of moss and age washes over you.")
        slow_print("Cobwebs cling to the archways. You grip your weapon, ready for whatever lies in wait...")
    elif floor == 2:
        slow_print("The stone stairs lead deeper into the earth where cold purple flames flicker in iron sconces.")
        slow_print("The walls are lined with thousands of ancient skulls. A dreadful magical hum echoes...")
    elif floor == 3:
        slow_print("Reality warps around you. The floor turns into floating obsidian slabs suspended above a pitch-black abyss.")
        slow_print("Tendrils of void energy crackle in the air. The final confrontation draws near...")

    pause()

    # Room sequences per floor: (type, title)
    # Types: "combat", "chest", "shrine", "merchant", "puzzle", "rest"
    floor_encounters = {
        1: [
            ("combat", "Patrolling Beasts"),
            ("chest", "Ancient Sarcophagus"),
            ("combat", "Crypt Ambush"),
            ("puzzle", "The Moon & Sun Door"),
            ("rest", "Forgotten Well of Solace"),
            ("boss", "Chamber of the Crypt Warden"),
        ],
        2: [
            ("combat", "Wraiths in the Dark"),
            ("merchant", "Grimbold's Shady Goods"),
            ("shrine", "Altar of the Crimson Oath"),
            ("combat", "Tomb Guardians"),
            ("chest", "Obsidian Vault"),
            ("rest", "Sunlit Sanctuary"),
            ("boss", "Phylactery Sanctum of Malakor"),
        ],
        3: [
            ("combat", "Void Aberrations"),
            ("puzzle", "Riddle of the Void Sphinx"),
            ("combat", "Morzan's Elite Guard"),
            ("chest", "Vault of the Fallen Champions"),
            ("rest", "The Final Campfire"),
            ("boss", "Throne of the Void Sovereign"),
        ],
    }

    rooms = floor_encounters.get(floor, [])

    for room_idx, (room_type, room_title) in enumerate(rooms, 1):
        clear_screen()
        print(f"{Colors.BOLD}{Colors.CYAN}[{floor_name} - Chamber {room_idx}/{len(rooms)}: {room_title}]{Colors.RESET}")
        print(f"Player HP: {render_bar(player.hp, player.max_hp, 15, Colors.GREEN)}  |  MP: {render_bar(player.mp, player.max_mp, 15, Colors.CYAN)}  |  Gold: {Colors.BRIGHT_YELLOW}{player.gold}{Colors.RESET}\n")

        # Hub interaction before entering each room
        _prompt_player_action(player)

        # Dispatch room event
        if room_type == "combat":
            enemy = spawn_enemy(floor, room_idx)
            survived = run_combat(player, enemy)
            if not survived:
                if player.hp <= 0:
                    return False  # Dead

        elif room_type == "chest":
            _event_treasure_chest(player, floor)

        elif room_type == "shrine":
            _event_mystic_shrine(player)

        elif room_type == "merchant":
            _event_merchant(player)

        elif room_type == "puzzle":
            _event_puzzle(player, floor)

        elif room_type == "rest":
            _event_rest_site(player)

        elif room_type == "boss":
            boss = spawn_boss(floor)
            slow_print(f"\n{Colors.BRIGHT_RED}A deafening roar shakes the foundation of the dungeon!{Colors.RESET}")
            slow_print(f"{Colors.BOLD}{boss.name}{Colors.RESET} blocks the pathway forward!\n")
            pause("Draw your steel and prepare for the battle of your life...")
            survived = run_combat(player, boss)
            if not survived or player.hp <= 0:
                return False

    # Floor complete!
    clear_screen()
    print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}╔══════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}║             ★ {floor_name.upper()} CLEARED! ★           ║{Colors.RESET}")
    print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}╚══════════════════════════════════════════════════════════╝{Colors.RESET}\n")
    print(f"You have conquered this floor and secured your progress.")
    player.gold += 50
    print(f"{Colors.BRIGHT_YELLOW}+50 Bonus Floor Completion Gold awarded! (Total: {player.gold}){Colors.RESET}")
    pause()
    return True


def _prompt_player_action(player: Player):
    """Allows player to view stats, manage inventory, equip items before proceeding."""
    while True:
        print(f"{Colors.DIM}Options: [1] Proceed to Room   [2] Character Stats   [3] Manage Gear & Pack{Colors.RESET}")
        choice = input(f"{Colors.YELLOW}Enter option (1-3): {Colors.RESET}").strip()
        if choice in ["1", ""]:
            break
        elif choice == "2":
            _show_character_sheet(player)
        elif choice == "3":
            _manage_equipment_and_inventory(player)
        else:
            print(f"{Colors.RED}Invalid choice.{Colors.RESET}")


def _show_character_sheet(player: Player):
    """Display comprehensive character sheet."""
    clear_screen()
    weapon_name = player.equipped_weapon.name if player.equipped_weapon else "Bare Fists"
    armor_name = player.equipped_armor.name if player.equipped_armor else "Unarmored"

    lines = [
        f"{Colors.BOLD}Name:{Colors.RESET}   {player.name} the {player.player_class}",
        f"{Colors.BOLD}Level:{Colors.RESET}  {player.level}   (XP: {player.xp}/{player.xp_needed})",
        f"{Colors.BOLD}HP:{Colors.RESET}     {render_bar(player.hp, player.max_hp, 20, Colors.GREEN)}",
        f"{Colors.BOLD}MP:{Colors.RESET}     {render_bar(player.mp, player.max_mp, 20, Colors.CYAN)}",
        f"{Colors.BOLD}Gold:{Colors.RESET}   {Colors.BRIGHT_YELLOW}{player.gold} coins{Colors.RESET}",
        "─" * 55,
        f"{Colors.BOLD}Total Attack:{Colors.RESET}   {player.total_atk} (Base {player.base_atk} + Weapon)",
        f"{Colors.BOLD}Total Defense:{Colors.RESET}  {player.total_def} (Base {player.base_def} + Armor)",
        f"{Colors.BOLD}Critical Rate:{Colors.RESET}  {int(player.crit_chance * 100)}%",
        f"{Colors.BOLD}Dodge Chance:{Colors.RESET}   {int(player.dodge_chance * 100)}%",
        f"{Colors.BOLD}Speed:{Colors.RESET}          {player.speed}",
        "─" * 55,
        f"{Colors.BOLD}Weapon:{Colors.RESET} {Colors.BRIGHT_CYAN}{weapon_name}{Colors.RESET}",
        f"{Colors.BOLD}Armor:{Colors.RESET}  {Colors.BRIGHT_BLUE}{armor_name}{Colors.RESET}",
        f"{Colors.BOLD}Skills:{Colors.RESET} {', '.join([s.name for s in player.skills])}",
    ]
    print_box(lines, title="CHARACTER RECORD", border_color=Colors.CYAN, width=64)
    pause()


def _manage_equipment_and_inventory(player: Player):
    """View and equip/use items from pack outside combat."""
    while True:
        clear_screen()
        print(f"\n{Colors.BOLD}═══ INVENTORY & EQUIPMENT ═══{Colors.RESET}")
        weapon_name = player.equipped_weapon.name if player.equipped_weapon else "None"
        armor_name = player.equipped_armor.name if player.equipped_armor else "None"
        print(f"Equipped Weapon: {Colors.BRIGHT_CYAN}{weapon_name}{Colors.RESET}")
        print(f"Equipped Armor:  {Colors.BRIGHT_BLUE}{armor_name}{Colors.RESET}\n")

        items_list = []
        for item_id, count in player.inventory.items():
            it = get_item(item_id)
            if it:
                items_list.append((it, count))

        if not items_list:
            print(f"{Colors.DIM}Your backpack is empty.{Colors.RESET}")
            pause()
            break

        for idx, (item, count) in enumerate(items_list, 1):
            extra = ""
            if isinstance(item, Weapon):
                extra = f"{Colors.BRIGHT_GREEN}[Weapon: +{item.attack_bonus} ATK]{Colors.RESET}"
            elif isinstance(item, Armor):
                extra = f"{Colors.BRIGHT_BLUE}[Armor: +{item.defense_bonus} DEF, +{item.hp_bonus} HP]{Colors.RESET}"
            elif isinstance(item, Consumable):
                extra = f"{Colors.YELLOW}[Consumable: {item.effect.upper()}]{Colors.RESET}"

            print(f"  [{idx}] {item.name} x{count} {extra}")
            print(f"      {Colors.DIM}{item.description}{Colors.RESET}")

        print(f"\n  [0] {Colors.YELLOW}Back to Chamber{Colors.RESET}")

        choice = input(f"\nSelect item number to equip/use (or 0): ").strip()
        if choice == "0":
            break

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(items_list):
                item, count = items_list[idx]

                if isinstance(item, Weapon):
                    # Equip weapon
                    old_weapon = player.equipped_weapon
                    player.equipped_weapon = item
                    print(f"\n{Colors.BRIGHT_GREEN}Equipped {item.name}! Attack is now {player.total_atk}!{Colors.RESET}")
                    pause()

                elif isinstance(item, Armor):
                    # Equip armor
                    old_armor = player.equipped_armor
                    # Adjust max hp difference if any
                    diff_hp = item.hp_bonus - (old_armor.hp_bonus if old_armor else 0)
                    player.max_hp += diff_hp
                    player.hp = min(player.max_hp, player.hp + diff_hp)
                    player.equipped_armor = item
                    print(f"\n{Colors.BRIGHT_BLUE}Equipped {item.name}! Defense is now {player.total_def}!{Colors.RESET}")
                    pause()

                elif isinstance(item, Consumable):
                    if item.effect == "heal_hp":
                        if player.hp >= player.max_hp:
                            print(f"{Colors.YELLOW}Your HP is already full!{Colors.RESET}")
                            time.sleep(1)
                            continue
                        player.remove_item(item.id, 1)
                        h = player.heal(item.power)
                        print(f"{Colors.BRIGHT_GREEN}Restored {h} HP! ({player.hp}/{player.max_hp}){Colors.RESET}")
                        pause()

                    elif item.effect == "heal_mp":
                        if player.mp >= player.max_mp:
                            print(f"{Colors.YELLOW}Your MP is already full!{Colors.RESET}")
                            time.sleep(1)
                            continue
                        player.remove_item(item.id, 1)
                        m = player.restore_mp(item.power)
                        print(f"{Colors.BRIGHT_CYAN}Restored {m} MP! ({player.mp}/{player.max_mp}){Colors.RESET}")
                        pause()

                    elif item.effect in ["buff_atk", "buff_def", "bomb"]:
                        print(f"{Colors.YELLOW}This item is best saved for active combat!{Colors.RESET}")
                        time.sleep(1)

        except ValueError:
            pass


# -------------------------------------------------------------
# SPECIFIC EVENT CHAMBERS
# -------------------------------------------------------------

def _event_treasure_chest(player: Player, floor: int):
    """Encounter with a treasure chest, with possible traps or rare loot."""
    player.chests_opened += 1
    print(TREASURE_ART)
    slow_print(f"\n{Colors.BRIGHT_YELLOW}You discover an ornate, iron-bound chest nestled among the rubble!{Colors.RESET}")

    print("\nWhat will you do?")
    print("  [1] Open carefully (inspect for traps)")
    print("  [2] Kick it open aggressively!")
    print("  [3] Leave it alone")

    choice = input(f"{Colors.YELLOW}Action (1-3): {Colors.RESET}").strip()

    if choice == "3":
        print(f"You decide not to tempt fate and move along.")
        pause()
        return

    # Check trap
    is_trapped = random.random() < 0.30

    if choice == "2" and is_trapped:
        trap_dmg = random.randint(15, 25) * floor
        player.hp = max(1, player.hp - trap_dmg)
        print(f"\n{Colors.BRIGHT_RED}💥 CLICK! Poison darts shoot from the lock mechanism!{Colors.RESET}")
        print(f"You take {trap_dmg} damage! (Current HP: {player.hp}/{player.max_hp})")
    elif choice == "1":
        if is_trapped:
            print(f"\n{Colors.BRIGHT_GREEN}✔ You noticed a delicate tripwire! You carefully disarm the trap.{Colors.RESET}")
        else:
            print(f"\n{Colors.GREEN}The chest is clear of traps.{Colors.RESET}")

    # Reward loot
    gold_found = random.randint(30, 60) * floor
    player.gold += gold_found

    item_pool = {
        1: ["steel_longsword", "iron_chainmail", "greater_healing_potion", "fire_bomb"],
        2: ["crystal_staff", "shadow_daggers", "royal_plate", "greater_mana_potion"],
        3: ["dragonbone_blade", "aegis_of_ages", "elixir_of_life"],
    }
    bonus_item_id = random.choice(item_pool.get(floor, ["greater_healing_potion"]))
    bonus_item = get_item(bonus_item_id)
    if bonus_item:
        player.add_item(bonus_item.id, 1)

    print(f"\n{Colors.BRIGHT_YELLOW}Inside the chest you discovered:{Colors.RESET}")
    print(f"  • {Colors.BOLD}{gold_found} Gold Coins{Colors.RESET}")
    if bonus_item:
        print(f"  • {Colors.BOLD}{bonus_item.name}{Colors.RESET} ({bonus_item.description})")

    pause()


def _event_mystic_shrine(player: Player):
    """Encounter with an occult altar offering risky boons."""
    print(
        Colors.BRIGHT_MAGENTA
        + """
                /\\
               /  \\
              / /\\ \\
             / /  \\ \\
            / / /\\ \\ \\
           / / /  \\ \\ \\
          /_/_/____\\_\\_\\
              [====]
              [====]"""
        + Colors.RESET
    )
    slow_print(f"\n{Colors.MAGENTA}You stand before the Altar of the Crimson Oath.{Colors.RESET}")
    slow_print("A bowl of dark liquid glows with supernatural luminescence.")

    print("\nThe altar speaks directly into your mind:")
    print("  [1] Offer Vitality: Sacrifices 25 HP for a permanent +4 to Base Attack.")
    print("  [2] Offer Gold: Donate 40 Gold for a blessing of full HP & MP restoration.")
    print("  [3] Pray silently: A humble prayer for divine fortune (random chance).")
    print("  [4] Step away")

    choice = input(f"{Colors.YELLOW}Choose (1-4): {Colors.RESET}").strip()

    if choice == "1":
        if player.hp <= 30:
            print(f"{Colors.RED}Your vitality is too low to survive the sacrifice!{Colors.RESET}")
        else:
            player.hp -= 25
            player.base_atk += 4
            print(f"\n{Colors.BRIGHT_RED}The blood seeps into the stone. You feel ferocious power surge into your limbs!{Colors.RESET}")
            print(f"{Colors.BRIGHT_GREEN}★ Permanent Base Attack increased to {player.base_atk}!{Colors.RESET}")

    elif choice == "2":
        if player.gold < 40:
            print(f"{Colors.RED}You do not possess enough gold to satisfy the altar.{Colors.RESET}")
        else:
            player.gold -= 40
            player.hp = player.max_hp
            player.mp = player.max_mp
            player.status_effects.clear()
            print(f"\n{Colors.BRIGHT_CYAN}Golden light bathes you! All HP and MP fully restored, ailments purged!{Colors.RESET}")

    elif choice == "3":
        roll = random.random()
        if roll < 0.6:
            player.add_item("greater_healing_potion", 1)
            print(f"\n{Colors.BRIGHT_GREEN}A warm aura surrounds you. A Greater Healing Potion materializes!{Colors.RESET}")
        else:
            print(f"\n{Colors.DIM}The stone remains silent. Nothing happens.{Colors.RESET}")
    else:
        print("You leave the shrine undisturbed.")

    pause()


def _event_merchant(player: Player):
    """Interactive dungeon shopkeeper."""
    clear_screen()
    print(
        Colors.BRIGHT_YELLOW
        + """
        .-.
       /   \\
      | (_) |   Grimbold the Wandering Peddler
       \\   /    "Fine wares for doomed travelers, heh heh!"
       /   \\
      /|   |\\ """
        + Colors.RESET
    )

    catalog = [
        ("greater_healing_potion", 45),
        ("greater_mana_potion", 45),
        ("berserker_brew", 30),
        ("stoneskin_tonic", 30),
        ("fire_bomb", 35),
        ("steel_longsword", 80),
        ("iron_chainmail", 95),
        ("elixir_of_life", 130),
    ]

    while True:
        print(f"\n{Colors.BOLD}Grimbold's Stock (Your Gold: {Colors.BRIGHT_YELLOW}{player.gold}{Colors.RESET}):")
        for idx, (item_id, price) in enumerate(catalog, 1):
            item = get_item(item_id)
            if item:
                afford = Colors.GREEN if player.gold >= price else Colors.RED
                print(f"  [{idx}] {item.name} - {afford}{price} Gold{Colors.RESET}")
                print(f"      {Colors.DIM}{item.description}{Colors.RESET}")

        print(f"\n  [S] {Colors.CYAN}Sell Items from Inventory{Colors.RESET}")
        print(f"  [0] {Colors.YELLOW}Farewell Grimbold (Leave Shop){Colors.RESET}")

        choice = input(f"\nBuy item (1-{len(catalog)}, S, or 0): ").strip().lower()

        if choice == "0":
            print(f"\n'Safe travels, friend. Try not to die out there!'")
            pause()
            break

        elif choice == "s":
            _merchant_sell_menu(player)

        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(catalog):
                    item_id, price = catalog[idx]
                    item = get_item(item_id)
                    if player.gold < price:
                        print(f"{Colors.RED}'Not enough coin, friend! I don't give credit.'{Colors.RESET}")
                        time.sleep(1)
                    else:
                        player.gold -= price
                        player.add_item(item_id, 1)
                        print(f"\n{Colors.BRIGHT_GREEN}Purchased {item.name}! Remaining Gold: {player.gold}{Colors.RESET}")
                        time.sleep(0.8)
            except ValueError:
                pass


def _merchant_sell_menu(player: Player):
    """Allows selling items for 60% of their base value."""
    while True:
        clear_screen()
        print(f"\n{Colors.BOLD}═══ SELL ITEMS TO GRIMBOLD (Your Gold: {player.gold}) ═══{Colors.RESET}")
        sellable = []
        for item_id, count in player.inventory.items():
            it = get_item(item_id)
            if it and it.item_type != "quest" and it.value > 0:
                sell_val = max(1, int(it.value * 0.6))
                sellable.append((it, count, sell_val))

        if not sellable:
            print(f"{Colors.DIM}You have nothing of value to sell.{Colors.RESET}")
            pause()
            break

        for idx, (it, count, val) in enumerate(sellable, 1):
            print(f"  [{idx}] {it.name} x{count} -> Sells for {Colors.BRIGHT_YELLOW}{val} Gold each{Colors.RESET}")

        print(f"\n  [0] Back to Shop")
        choice = input(f"Select item to sell (1-{len(sellable)} or 0): ").strip()
        if choice == "0":
            break

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(sellable):
                it, count, val = sellable[idx]
                player.remove_item(it.id, 1)
                player.gold += val
                print(f"{Colors.BRIGHT_GREEN}Sold 1x {it.name} for +{val} Gold!{Colors.RESET}")
                time.sleep(0.8)
        except ValueError:
            pass


def _event_puzzle(player: Player, floor: int):
    """Interactive puzzles and riddles requiring player logic."""
    if floor == 1:
        slow_print("\nYou approach a massive stone portal adorned with carved celestial dials.")
        slow_print("An inscription is carved in ancient glyphs:")
        print(f"\n{Colors.BRIGHT_CYAN}\"I have no flesh, no feathers, no scales, and no bone.")
        print(f"Yet I have three fingers of my own.")
        print(f"I follow you in sunlight, but vanish in the gloom.")
        print(f"What am I?\"{Colors.RESET}\n")

        print("  [1] A Candle Flame")
        print("  [2] A Shadow")
        print("  [3] A Sundial")
        print("  [4] A Reflection")

        ans = input(f"{Colors.YELLOW}Your answer (1-4): {Colors.RESET}").strip()
        if ans == "2":
            print(f"\n{Colors.BRIGHT_GREEN}The celestial dials align! With a deep rumble, the heavy door slides open!{Colors.RESET}")
            print(f"A hidden alcove reveals a {Colors.BOLD}Twin Shadow Daggers{Colors.RESET} and 40 Gold!")
            player.add_item("shadow_daggers", 1)
            player.gold += 40
        else:
            print(f"\n{Colors.RED}A discordant chime echoes! A burst of flame erupts from the glyphs!{Colors.RESET}")
            player.hp = max(1, player.hp - 20)
            print(f"You took 20 fire damage! (HP: {player.hp}/{player.max_hp})")

    elif floor == 3:
        slow_print("\nA towering Void Sphinx carved from dark star-matter stares down at you.")
        slow_print("Its ruby eyes burn with ancient intellect:")
        print(f"\n{Colors.BRIGHT_MAGENTA}\"Feed me and I will live, give me a drink and I will die.")
        print(f"I swallow kingdoms when untamed, yet warm a weary traveler's eye.")
        print(f"What is my name?\"{Colors.RESET}\n")

        print("  [1] Fire")
        print("  [2] Thirst")
        print("  [3] Greed")
        print("  [4] Time")

        ans = input(f"{Colors.YELLOW}Your answer (1-4): {Colors.RESET}").strip()
        if ans == "1":
            print(f"\n{Colors.BRIGHT_GREEN}The Sphinx bows its head in reverence! 'Wise mortal... take the armament of dawns.'{Colors.RESET}")
            print(f"You receive the {Colors.BRIGHT_YELLOW}Dawnbringer (Legendary){Colors.RESET} blade and an Elixir of Life!")
            player.add_item("dawn_bringer", 1)
            player.add_item("elixir_of_life", 1)
        else:
            print(f"\n{Colors.RED}The Sphinx snarls: 'Foolish insect!' Dark lightning strikes you!{Colors.RESET}")
            player.hp = max(1, player.hp - 35)

    pause()


def _event_rest_site(player: Player):
    """Campfire resting site allowing health recovery or weapon honing."""
    print(
        Colors.BRIGHT_YELLOW
        + """
             (  .      )
           )           (              
          (   (  *  )  )              
          .  / \\ | / \\  .    
           (___________)  Campfire Rest Site"""
        + Colors.RESET
    )
    slow_print("\nYou find a safe hollow shielded by sacred barrier stones.")
    slow_print("A warm campfire crackles pleasantly.")

    print("\nWhat would you like to do?")
    print("  [1] Rest and Sleep (Recover 60% of Max HP and 60% of Max MP)")
    print("  [2] Hone Weapons & Sharpen Blade (+2 Base Attack)")
    print("  [3] Meditate on Battle Techniques (+15 XP)")

    choice = input(f"{Colors.YELLOW}Choice (1-3): {Colors.RESET}").strip()

    if choice == "1":
        h = player.heal(int(player.max_hp * 0.60))
        m = player.restore_mp(int(player.max_mp * 0.60))
        player.status_effects.clear()
        print(f"\n{Colors.BRIGHT_GREEN}You wake feeling refreshed! Healed {h} HP and restored {m} MP!{Colors.RESET}")

    elif choice == "2":
        player.base_atk += 2
        print(f"\n{Colors.BRIGHT_CYAN}You sharpen your weapon to a razor's edge. Base Attack +2! (Now {player.base_atk}){Colors.RESET}")

    elif choice == "3":
        leveled, logs = player.gain_xp(35)
        print(f"\n{Colors.BRIGHT_MAGENTA}Inner peace grants profound clarity. Gained +35 XP!{Colors.RESET}")
        if leveled:
            for log in logs:
                print(log)

    pause()
