"""
main.py - Shadows of Eldoria: The Sunken Crypt
A full-featured Terminal RPG Adventure with tactical combat, story choices, and character progression.
"""

import sys
import time

from utils import (
    Colors,
    colorize,
    clear_screen,
    pause,
    slow_print,
    print_box,
    TITLE_BANNER,
    SWORD_ART,
    SKULL_ART,
)
from entities import Player, create_player
from story import run_dungeon_floor
from save_manager import (
    save_exists,
    save_game,
    load_game,
    delete_save,
    record_hall_of_fame,
    get_hall_of_fame,
)


def main():
    """Main game entry point."""
    while True:
        clear_screen()
        print(TITLE_BANNER)

        has_save = save_exists()
        save_tag = f" {Colors.BRIGHT_GREEN}(Saved Game Available){Colors.RESET}" if has_save else ""

        print(f"  {Colors.BOLD}─── MAIN MENU ──────────────────────────────────{Colors.RESET}")
        print(f"  {Colors.BRIGHT_GREEN}[1]{Colors.RESET} Begin New Adventure")
        if has_save:
            print(f"  {Colors.BRIGHT_CYAN}[2]{Colors.RESET} Continue Adventure{save_tag}")
        else:
            print(f"  {Colors.BRIGHT_BLACK}[2] Continue Adventure (No Save Found){Colors.RESET}")
        print(f"  {Colors.BRIGHT_YELLOW}[3]{Colors.RESET} Game Guide & Combat Mechanics")
        print(f"  {Colors.BRIGHT_MAGENTA}[4]{Colors.RESET} Hall of Champions (Records)")
        print(f"  {Colors.BRIGHT_RED}[5]{Colors.RESET} Exit Game")
        print(f"  {Colors.BOLD}────────────────────────────────────────────────{Colors.RESET}\n")

        choice = input(f"{Colors.YELLOW}Enter choice (1-5): {Colors.RESET}").strip()

        if choice == "1":
            start_new_game()
        elif choice == "2":
            if has_save:
                continue_game()
            else:
                print(f"{Colors.RED}No saved game found! Please start a new adventure.{Colors.RESET}")
                time.sleep(1.2)
        elif choice == "3":
            show_guide()
        elif choice == "4":
            show_hall_of_fame()
        elif choice == "5":
            clear_screen()
            print(f"\n{Colors.BRIGHT_CYAN}Thank you for braving Eldoria! Farewell, adventurer.{Colors.RESET}\n")
            sys.exit(0)
        else:
            print(f"{Colors.RED}Invalid selection. Please choose from 1 to 5.{Colors.RESET}")
            time.sleep(0.8)


def start_new_game():
    """Character creation and campaign launch."""
    clear_screen()
    print(f"\n{Colors.BOLD}═══ CREATE YOUR HERO ═══{Colors.RESET}\n")

    # Name input
    while True:
        name = input(f"Enter your character's name: {Colors.BRIGHT_GREEN}").strip()
        print(Colors.RESET, end="")
        if name:
            break
        print(f"{Colors.RED}Name cannot be empty!{Colors.RESET}")

    # Class selection
    clear_screen()
    print(f"\nWelcome, {Colors.BOLD}{name}{Colors.RESET}. Select your archetype:\n")

    classes = [
        (
            "Warrior",
            "Heavy armor, robust health, and high physical resilience.",
            "HP: 130  │  MP: 40  │  ATK: 14  │  DEF: 8",
            "Skills: Shield Slam, Iron Tempest, War Cry",
        ),
        (
            "Mage",
            "Master of the elements with massive spell bursts and life siphon.",
            "HP: 90   │  MP: 90  │  ATK: 16  │  DEF: 4",
            "Skills: Arcane Missiles, Hellfire Orb, Vampiric Drain",
        ),
        (
            "Rogue",
            "Agile assassin with high evasion, devastating critical strikes, and poisons.",
            "HP: 105  │  MP: 55  │  ATK: 15  │  DEF: 5",
            "Skills: Shadow Strike, Venomous Shiv, Vanish in Smoke",
        ),
        (
            "Paladin",
            "Holy champion blending offensive smiting, self-healing, and protective wards.",
            "HP: 120  │  MP: 60  │  ATK: 13  │  DEF: 7",
            "Skills: Radiant Smite, Holy Light, Divine Bastion",
        ),
    ]

    for idx, (c_name, desc, stats, skills) in enumerate(classes, 1):
        print(f"  {Colors.BOLD}[{idx}] {c_name}{Colors.RESET}")
        print(f"      {desc}")
        print(f"      {Colors.CYAN}{stats}{Colors.RESET}")
        print(f"      {Colors.DIM}{skills}{Colors.RESET}\n")

    while True:
        choice = input(f"{Colors.YELLOW}Choose your class (1-4): {Colors.RESET}").strip()
        class_map = {"1": "Warrior", "2": "Mage", "3": "Rogue", "4": "Paladin"}
        if choice in class_map:
            chosen_class = class_map[choice]
            break
        print(f"{Colors.RED}Invalid class choice. Please choose 1, 2, 3, or 4.{Colors.RESET}")

    player = create_player(name, chosen_class)

    clear_screen()
    slow_print(f"The legend of {Colors.BOLD}{player.name} the {player.player_class}{Colors.RESET} begins...\n")
    slow_print("Centuries ago, the Sunken Crypt of Eldoria was sealed to contain the Void Sovereign Morzan.")
    slow_print("Now, dark tremors convulse the land, and the ancient seals have broken.")
    slow_print("Armed with your weapon and resolve, you step into the yawning black maw of the catacombs...\n")
    pause("Press [ENTER] to enter the Crypt...")

    run_campaign(player, start_floor=1)


def continue_game():
    """Load existing save game and resume."""
    result = load_game()
    if not result:
        print(f"{Colors.RED}Failed to load save game.{Colors.RESET}")
        pause()
        return

    player, floor = result
    clear_screen()
    print(f"\n{Colors.BRIGHT_GREEN}Save game loaded successfully!{Colors.RESET}")
    print(f"Hero: {Colors.BOLD}{player.name} the {player.player_class}{Colors.RESET} (Level {player.level})")
    print(f"Location: Floor {floor} | Gold: {player.gold} | Battles Won: {player.battles_won}\n")
    pause("Press [ENTER] to resume your quest...")

    run_campaign(player, start_floor=floor)


def run_campaign(player: Player, start_floor: int = 1):
    """Main campaign loop through all dungeon floors."""
    total_floors = 3

    for floor in range(start_floor, total_floors + 1):
        # Save before entering new floor
        save_game(player, floor)

        survived = run_dungeon_floor(player, floor)

        if not survived or player.hp <= 0:
            # Defeat
            record_hall_of_fame(player, won=False)
            delete_save()
            return

        # Prompt between floors
        if floor < total_floors:
            clear_screen()
            print(f"\n{Colors.BRIGHT_CYAN}══════════════════════════════════════════════════════════{Colors.RESET}")
            print(f"             RESTING BEFORE THE NEXT DEPTHS")
            print(f"{Colors.BRIGHT_CYAN}══════════════════════════════════════════════════════════{Colors.RESET}\n")
            print("Your progress has been auto-saved.")
            print("  [1] Continue deeper into the abyss")
            print("  [2] Save & Return to Main Menu")

            choice = input(f"\n{Colors.YELLOW}Enter option (1-2): {Colors.RESET}").strip()
            if choice == "2":
                save_game(player, floor + 1)
                print(f"\n{Colors.BRIGHT_GREEN}Game saved! Returning to Main Menu...{Colors.RESET}")
                time.sleep(1.2)
                return

    # Epic Campaign Victory!
    _render_campaign_victory(player)
    record_hall_of_fame(player, won=True)
    delete_save()


def _render_campaign_victory(player: Player):
    """Grand ending sequence upon defeating the final boss."""
    clear_screen()
    print(SWORD_ART)
    print(f"""{Colors.BRIGHT_YELLOW}
  ╔═══════════════════════════════════════════════════════════════════════════╗
  ║                                                                           ║
  ║                   ★ THE SUNKEN CRYPT HAS FALLEN! ★                        ║
  ║                                                                           ║
  ║               MORZAN IS VANQUISHED - ELDORIA IS SAVED!                    ║
  ║                                                                           ║
  ╚═══════════════════════════════════════════════════════════════════════════╝{Colors.RESET}\n""")

    slow_print(f"With a final earth-shattering blow, Lord Morzan dissolves into harmless stardust.")
    slow_print("The malevolent obsidian spire crumbles into pure golden light.")
    slow_print("Sunbeams pierce the subterranean depths for the first time in a thousand years.")
    slow_print(f"\nYou, {Colors.BOLD}{player.name} the {player.player_class}{Colors.RESET}, emerge into the dawn as the Savior of the Realm!\n")

    print(f"{Colors.BOLD}─── FINAL ADVENTURE RECORD ─────────────────────────────{Colors.RESET}")
    print(f"  • Hero:            {player.name} the {player.player_class}")
    print(f"  • Final Level:     {player.level}")
    print(f"  • Battles Won:     {player.battles_won}")
    print(f"  • Bosses Slain:    {player.bosses_defeated}")
    print(f"  • Chests Opened:   {player.chests_opened}")
    print(f"  • Gold Amassed:    {player.gold}")
    print(f"{Colors.BOLD}────────────────────────────────────────────────────────{Colors.RESET}\n")

    pause("Press [ENTER] to engrave your name into the Hall of Champions...")


def show_guide():
    """Display rules, tips, and mechanics."""
    clear_screen()
    lines = [
        f"{Colors.BOLD}1. Combat System:{Colors.RESET}",
        f"   • Attack: Standard physical hit with critical strike chance.",
        f"   • Skills: Spend MP to deal burst damage, heal, or inflict status.",
        f"   • Defend: Greatly increases DEF for the turn and recovers 6 MP.",
        f"   • Items: Usable mid-fight (healing, mana, buffs, fire bombs).",
        "",
        f"{Colors.BOLD}2. Status Effects:{Colors.RESET}",
        f"   • Burn (🔥): Deals persistent fire damage each turn.",
        f"   • Poison (☣): Deals escalating nature decay damage.",
        f"   • Stun (⚡): Target skips their entire action for that round.",
        "",
        f"{Colors.BOLD}3. Exploration & Events:{Colors.RESET}",
        f"   • Sarcophagi & Vaults: Search for weapons, armors, and gold.",
        f"   • Peddler Grimbold: Buy consumables, sell excess gear for coin.",
        f"   • Mystic Shrines: Gamble vitality or gold for blessings.",
        f"   • Campfires: Rest to replenish 60% of Max HP and MP.",
        "",
        f"{Colors.BOLD}4. Progression & Saves:{Colors.RESET}",
        f"   • Earn XP to level up, which grants permanent stat growth.",
        f"   • Progress auto-saves between chambers and floors.",
    ]
    print_box(lines, title="HOW TO PLAY & TACTICAL GUIDE", border_color=Colors.BRIGHT_YELLOW, width=68)
    pause()


def show_hall_of_fame():
    """Display past runs and hero records."""
    clear_screen()
    records = get_hall_of_fame()

    print(f"\n{Colors.BOLD}═════════════════════ HALL OF CHAMPIONS ═════════════════════{Colors.RESET}\n")

    if not records:
        print(f"{Colors.DIM}No heroes have ventured into the crypt yet. Will you be the first?{Colors.RESET}\n")
    else:
        print(f"  {'HERO NAME':<16} {'CLASS':<10} {'LVL':<5} {'WINS':<6} {'GOLD':<8} {'OUTCOME'}")
        print(f"  {'-'*16} {'-'*10} {'-'*5} {'-'*6} {'-'*8} {'-'*24}")
        for r in records:
            outcome_col = Colors.GREEN if "VICTOR" in r.get("status", "") else Colors.RED
            status_text = f"{outcome_col}{r.get('status', 'Unknown')}{Colors.RESET}"
            print(
                f"  {r['name']:<16} {r['class']:<10} {r['level']:<5} {r['battles_won']:<6} {r['gold']:<8} {status_text}"
            )
        print()

    pause()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Adventure paused. Farewell!{Colors.RESET}\n")
