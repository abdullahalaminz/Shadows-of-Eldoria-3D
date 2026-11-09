"""
entities.py - Player classes, enemies, bosses, combat skills, and leveling logic.
"""

import math
import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple

from items import Item, Weapon, Armor, Consumable, get_item, ITEM_REGISTRY
from utils import Colors, colorize


@dataclass
class Skill:
    id: str
    name: str
    mp_cost: int
    description: str
    skill_type: str  # "damage", "heal", "buff", "debuff"
    multiplier: float = 1.0  # multiplier on player's total ATK
    status_effect: Optional[str] = None  # "burn", "poison", "stun"
    status_turns: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "mp_cost": self.mp_cost,
            "description": self.description,
            "skill_type": self.skill_type,
            "multiplier": self.multiplier,
            "status_effect": self.status_effect,
            "status_turns": self.status_turns,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Skill":
        return cls(**data)


SKILL_REGISTRY: Dict[str, Skill] = {
    # Warrior Skills
    "shield_slam": Skill(
        id="shield_slam",
        name="Shield Slam",
        mp_cost=12,
        description="Bash the enemy with your shield. Moderate damage and 50% chance to stun.",
        skill_type="damage",
        multiplier=1.3,
        status_effect="stun",
        status_turns=1,
    ),
    "iron_tempest": Skill(
        id="iron_tempest",
        name="Iron Tempest",
        mp_cost=25,
        description="A devastating sweeping slash dealing 220% physical damage.",
        skill_type="damage",
        multiplier=2.2,
    ),
    "war_cry": Skill(
        id="war_cry",
        name="War Cry",
        mp_cost=15,
        description="Rally your battle spirit, restoring 30 HP and boosting ATK.",
        skill_type="heal",
        multiplier=0.0,
    ),

    # Mage Skills
    "arcane_missiles": Skill(
        id="arcane_missiles",
        name="Arcane Missiles",
        mp_cost=12,
        description="Launches concentrated magical bolts dealing 140% spell damage.",
        skill_type="damage",
        multiplier=1.4,
    ),
    "hellfire": Skill(
        id="hellfire",
        name="Hellfire Orb",
        mp_cost=28,
        description="Summons an inferno ball dealing 200% damage and burning the target.",
        skill_type="damage",
        multiplier=2.0,
        status_effect="burn",
        status_turns=3,
    ),
    "life_drain": Skill(
        id="life_drain",
        name="Vampiric Drain",
        mp_cost=22,
        description="Siphon vital force: deals 130% damage and heals you for 75% of damage dealt.",
        skill_type="drain",
        multiplier=1.3,
    ),

    # Rogue Skills
    "shadow_strike": Skill(
        id="shadow_strike",
        name="Shadow Strike",
        mp_cost=14,
        description="Strike from the shadows. High damage with a +35% critical strike chance.",
        skill_type="damage",
        multiplier=1.7,
    ),
    "toxic_shiv": Skill(
        id="toxic_shiv",
        name="Venomous Shiv",
        mp_cost=18,
        description="Infect the target with deadly nightshade venom for 3 turns.",
        skill_type="damage",
        multiplier=1.2,
        status_effect="poison",
        status_turns=3,
    ),
    "smoke_bomb": Skill(
        id="smoke_bomb",
        name="Vanish in Smoke",
        mp_cost=20,
        description="Distract the enemy, stunning them for 1 turn and guaranteeing evasion.",
        skill_type="damage",
        multiplier=0.5,
        status_effect="stun",
        status_turns=1,
    ),

    # Paladin Skills
    "radiant_smite": Skill(
        id="radiant_smite",
        name="Radiant Smite",
        mp_cost=16,
        description="Infuse weapon with holy light. Deals 180% damage (bonus vs undead).",
        skill_type="damage",
        multiplier=1.8,
    ),
    "holy_light": Skill(
        id="holy_light",
        name="Holy Light",
        mp_cost=20,
        description="Pray to the Dawn, restoring 65 HP and curing status effects.",
        skill_type="heal",
        multiplier=0.0,
    ),
    "divine_bastion": Skill(
        id="divine_bastion",
        name="Divine Bastion",
        mp_cost=22,
        description="Create a sacred ward reducing incoming damage by 50% for 2 turns.",
        skill_type="buff",
        multiplier=0.0,
    ),
}


class Player:
    def __init__(
        self,
        name: str,
        player_class: str,
        hp: int = 100,
        max_hp: int = 100,
        mp: int = 50,
        max_mp: int = 50,
        base_atk: int = 12,
        base_def: int = 5,
        speed: int = 10,
        gold: int = 40,
        level: int = 1,
        xp: int = 0,
        equipped_weapon: Optional[Weapon] = None,
        equipped_armor: Optional[Armor] = None,
    ):
        self.name = name
        self.player_class = player_class
        self.hp = hp
        self.max_hp = max_hp
        self.mp = mp
        self.max_mp = max_mp
        self.base_atk = base_atk
        self.base_def = base_def
        self.speed = speed
        self.gold = gold
        self.level = level
        self.xp = xp
        self.equipped_weapon = equipped_weapon
        self.equipped_armor = equipped_armor

        self.inventory: Dict[str, int] = {}  # item_id -> quantity
        self.skills: List[Skill] = []
        self.status_effects: Dict[str, int] = {}  # effect -> remaining turns
        self.temp_atk_buff = 0
        self.temp_def_buff = 0
        self.buff_turns = 0
        self.defending = False

        # Gameplay statistics
        self.battles_won = 0
        self.chests_opened = 0
        self.bosses_defeated = 0

    @property
    def xp_needed(self) -> int:
        return int(40 * (self.level ** 1.6))

    @property
    def total_atk(self) -> int:
        weapon_bonus = self.equipped_weapon.attack_bonus if self.equipped_weapon else 0
        return max(1, self.base_atk + weapon_bonus + self.temp_atk_buff)

    @property
    def total_def(self) -> int:
        armor_bonus = self.equipped_armor.defense_bonus if self.equipped_armor else 0
        defense = self.base_def + armor_bonus + self.temp_def_buff
        if self.defending:
            defense = int(defense * 1.8) + 4
        return max(0, defense)

    @property
    def crit_chance(self) -> float:
        base_crit = 0.08
        if self.player_class == "Rogue":
            base_crit = 0.18
        weapon_crit = self.equipped_weapon.crit_bonus if self.equipped_weapon else 0.0
        return min(0.75, base_crit + weapon_crit)

    @property
    def dodge_chance(self) -> float:
        base_dodge = min(0.40, self.speed * 0.015)
        if self.player_class == "Rogue":
            base_dodge += 0.10
        return base_dodge

    def take_damage(self, raw_damage: int) -> int:
        """Apply defense formula and reduce HP."""
        mitigation = self.total_def * 0.65
        actual_damage = max(1, int(raw_damage - mitigation))
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage

    def heal(self, amount: int) -> int:
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp

    def restore_mp(self, amount: int) -> int:
        old_mp = self.mp
        self.mp = min(self.max_mp, self.mp + amount)
        return self.mp - old_mp

    def add_item(self, item_id: str, count: int = 1):
        if item_id in self.inventory:
            self.inventory[item_id] += count
        else:
            self.inventory[item_id] = count

    def remove_item(self, item_id: str, count: int = 1) -> bool:
        if item_id in self.inventory and self.inventory[item_id] >= count:
            self.inventory[item_id] -= count
            if self.inventory[item_id] <= 0:
                del self.inventory[item_id]
            return True
        return False

    def has_item(self, item_id: str, count: int = 1) -> bool:
        return self.inventory.get(item_id, 0) >= count

    def gain_xp(self, amount: int) -> Tuple[bool, List[str]]:
        """Add XP and handle potential level-ups."""
        self.xp += amount
        leveled_up = False
        logs = []

        while self.xp >= self.xp_needed:
            self.xp -= self.xp_needed
            self.level += 1
            leveled_up = True

            # Stat scaling by class
            hp_gain = 20
            mp_gain = 10
            atk_gain = 3
            def_gain = 2

            if self.player_class == "Warrior":
                hp_gain += 12
                def_gain += 2
                atk_gain += 2
            elif self.player_class == "Mage":
                mp_gain += 18
                atk_gain += 4
                hp_gain += 6
            elif self.player_class == "Rogue":
                atk_gain += 4
                self.speed += 2
                hp_gain += 10
            elif self.player_class == "Paladin":
                hp_gain += 15
                mp_gain += 10
                def_gain += 3

            self.max_hp += hp_gain
            self.hp = self.max_hp
            self.max_mp += mp_gain
            self.mp = self.max_mp
            self.base_atk += atk_gain
            self.base_def += def_gain

            logs.append(
                f"{Colors.BRIGHT_GREEN}★ LEVEL UP! You reached Level {self.level}! ★{Colors.RESET}\n"
                f"  HP +{hp_gain} (Max: {self.max_hp}), MP +{mp_gain} (Max: {self.max_mp})\n"
                f"  ATK +{atk_gain} (Base: {self.base_atk}), DEF +{def_gain} (Base: {self.base_def})"
            )

        return leveled_up, logs

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "player_class": self.player_class,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "mp": self.mp,
            "max_mp": self.max_mp,
            "base_atk": self.base_atk,
            "base_def": self.base_def,
            "speed": self.speed,
            "gold": self.gold,
            "level": self.level,
            "xp": self.xp,
            "equipped_weapon": self.equipped_weapon.id if self.equipped_weapon else None,
            "equipped_armor": self.equipped_armor.id if self.equipped_armor else None,
            "inventory": self.inventory,
            "skills": [s.id for s in self.skills],
            "battles_won": self.battles_won,
            "chests_opened": self.chests_opened,
            "bosses_defeated": self.bosses_defeated,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Player":
        weapon_id = data.get("equipped_weapon")
        armor_id = data.get("equipped_armor")
        weapon = get_item(weapon_id) if weapon_id else None
        armor = get_item(armor_id) if armor_id else None

        player = cls(
            name=data["name"],
            player_class=data["player_class"],
            hp=data["hp"],
            max_hp=data["max_hp"],
            mp=data["mp"],
            max_mp=data["max_mp"],
            base_atk=data["base_atk"],
            base_def=data["base_def"],
            speed=data["speed"],
            gold=data["gold"],
            level=data["level"],
            xp=data["xp"],
            equipped_weapon=weapon,  # type: ignore
            equipped_armor=armor,    # type: ignore
        )
        player.inventory = data.get("inventory", {})
        skill_ids = data.get("skills", [])
        player.skills = [SKILL_REGISTRY[sid] for sid in skill_ids if sid in SKILL_REGISTRY]
        player.battles_won = data.get("battles_won", 0)
        player.chests_opened = data.get("chests_opened", 0)
        player.bosses_defeated = data.get("bosses_defeated", 0)
        return player


def create_player(name: str, class_choice: str) -> Player:
    """Factory to initialize a new player with starter kit."""
    if class_choice == "Warrior":
        p = Player(
            name=name,
            player_class="Warrior",
            hp=130,
            max_hp=130,
            mp=40,
            max_mp=40,
            base_atk=14,
            base_def=8,
            speed=8,
            gold=30,
            equipped_weapon=get_item("rusty_sword"),  # type: ignore
            equipped_armor=get_item("leather_armor"),  # type: ignore
        )
        p.skills = [SKILL_REGISTRY["shield_slam"], SKILL_REGISTRY["iron_tempest"], SKILL_REGISTRY["war_cry"]]
        p.add_item("minor_healing_potion", 2)
        p.add_item("stoneskin_tonic", 1)

    elif class_choice == "Mage":
        p = Player(
            name=name,
            player_class="Mage",
            hp=90,
            max_hp=90,
            mp=90,
            max_mp=90,
            base_atk=16,
            base_def=4,
            speed=11,
            gold=40,
            equipped_weapon=get_item("apprentice_staff"),  # type: ignore
            equipped_armor=get_item("mage_robes"),        # type: ignore
        )
        p.skills = [SKILL_REGISTRY["arcane_missiles"], SKILL_REGISTRY["hellfire"], SKILL_REGISTRY["life_drain"]]
        p.add_item("minor_healing_potion", 2)
        p.add_item("mana_draught", 2)
        p.add_item("fire_bomb", 1)

    elif class_choice == "Rogue":
        p = Player(
            name=name,
            player_class="Rogue",
            hp=105,
            max_hp=105,
            mp=55,
            max_mp=55,
            base_atk=15,
            base_def=5,
            speed=15,
            gold=50,
            equipped_weapon=get_item("shadow_daggers"),  # type: ignore
            equipped_armor=get_item("leather_armor"),     # type: ignore
        )
        p.skills = [SKILL_REGISTRY["shadow_strike"], SKILL_REGISTRY["toxic_shiv"], SKILL_REGISTRY["smoke_bomb"]]
        p.add_item("minor_healing_potion", 3)
        p.add_item("berserker_brew", 1)

    else:  # Paladin
        p = Player(
            name=name,
            player_class="Paladin",
            hp=120,
            max_hp=120,
            mp=60,
            max_mp=60,
            base_atk=13,
            base_def=7,
            speed=9,
            gold=35,
            equipped_weapon=get_item("steel_longsword"),  # type: ignore
            equipped_armor=get_item("iron_chainmail"),   # type: ignore
        )
        p.skills = [SKILL_REGISTRY["radiant_smite"], SKILL_REGISTRY["holy_light"], SKILL_REGISTRY["divine_bastion"]]
        p.add_item("minor_healing_potion", 2)
        p.add_item("mana_draught", 1)

    return p


# -------------------------------------------------------------
# ENEMY DEFINITION & AI
# -------------------------------------------------------------

@dataclass
class EnemyAction:
    action_type: str  # "attack", "skill", "buff", "debuff"
    name: str
    description: str
    damage: int = 0
    status: Optional[str] = None
    status_turns: int = 0


class Enemy:
    def __init__(
        self,
        name: str,
        hp: int,
        atk: int,
        defense: int,
        speed: int,
        xp_reward: int,
        gold_reward: int,
        is_boss: bool = False,
        enemy_type: str = "Beast",
        dialogue: str = "grunts menacingly!",
        loot_table: Optional[List[Tuple[str, float]]] = None,  # (item_id, chance)
    ):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.atk = atk
        self.defense = defense
        self.speed = speed
        self.xp_reward = xp_reward
        self.gold_reward = gold_reward
        self.is_boss = is_boss
        self.enemy_type = enemy_type
        self.dialogue = dialogue
        self.loot_table = loot_table or []
        self.status_effects: Dict[str, int] = {}

    def take_damage(self, raw_damage: int) -> int:
        mitigation = self.defense * 0.5
        actual_damage = max(1, int(raw_damage - mitigation))
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage

    def choose_action(self, player: Player) -> EnemyAction:
        """Determine enemy tactical move."""
        roll = random.random()

        if self.is_boss:
            if self.hp < self.max_hp * 0.35 and roll < 0.40:
                # Boss desperation / ultimate move
                dmg = int(self.atk * 1.7)
                return EnemyAction(
                    action_type="skill",
                    name="Apocalyptic Cataclysm",
                    description=f"{self.name} channels devastating dark energy across the chamber!",
                    damage=dmg,
                    status="burn",
                    status_turns=2,
                )
            elif roll < 0.35:
                dmg = int(self.atk * 1.3)
                return EnemyAction(
                    action_type="skill",
                    name="Soul Shatter",
                    description=f"{self.name} crushes the air with an occult shockwave!",
                    damage=dmg,
                    status="stun" if random.random() < 0.3 else None,
                    status_turns=1,
                )

        # Standard enemy behavior
        if roll < 0.25 and self.enemy_type == "Undead":
            dmg = int(self.atk * 1.2)
            return EnemyAction(
                action_type="skill",
                name="Necrotic Grasp",
                description=f"{self.name} claws with frigid skeletal hands, decaying your flesh!",
                damage=dmg,
                status="poison" if random.random() < 0.4 else None,
                status_turns=2,
            )
        elif roll < 0.25 and self.enemy_type == "Beast":
            dmg = int(self.atk * 1.3)
            return EnemyAction(
                action_type="skill",
                name="Vicious Rend",
                description=f"{self.name} lunges forward with razor sharp fangs!",
                damage=dmg,
            )

        # Basic Attack
        variation = random.randint(-2, 3)
        dmg = max(1, self.atk + variation)
        return EnemyAction(
            action_type="attack",
            name="Strike",
            description=f"{self.name} attacks with ferocious intent!",
            damage=dmg,
        )


def spawn_enemy(floor: int, encounter_num: int) -> Enemy:
    """Generate thematic enemies scaling with dungeon depth."""
    if floor == 1:
        pool = [
            ("Crypt Goblin Scavenger", 35, 10, 2, 9, 25, 15, "Humanoid", "cackles and twitches its ears!"),
            ("Decaying Skeleton", 45, 12, 4, 7, 30, 20, "Undead", "rattles its dry bones ominously!"),
            ("Giant Brood Spider", 40, 11, 3, 11, 28, 18, "Beast", "hisses and drips corrosive venom!"),
            ("Rogue Crypt Cultist", 50, 14, 3, 8, 35, 25, "Humanoid", "chants forbidden abyssal verses!"),
        ]
        chosen = random.choice(pool)
        return Enemy(
            name=chosen[0],
            hp=chosen[1],
            atk=chosen[2],
            defense=chosen[3],
            speed=chosen[4],
            xp_reward=chosen[5],
            gold_reward=chosen[6],
            enemy_type=chosen[7],
            dialogue=chosen[8],
            loot_table=[("minor_healing_potion", 0.40), ("stoneskin_tonic", 0.20), ("rusty_sword", 0.15)],
        )

    elif floor == 2:
        pool = [
            ("Shadow Wraith", 75, 20, 6, 12, 55, 35, "Undead", "drifts through the cold stone, weeping."),
            ("Armored Tomb Guardian", 95, 18, 12, 6, 65, 45, "Construct", "its granite joints grind with immense weight!"),
            ("Abyssal Bloodhound", 80, 22, 7, 14, 60, 40, "Beast", "howls with burning crimson eyes!"),
            ("Heretic Sorcerer", 85, 24, 6, 10, 70, 50, "Humanoid", "weaves dark incantations between glowing fingers."),
        ]
        chosen = random.choice(pool)
        return Enemy(
            name=chosen[0],
            hp=chosen[1],
            atk=chosen[2],
            defense=chosen[3],
            speed=chosen[4],
            xp_reward=chosen[5],
            gold_reward=chosen[6],
            enemy_type=chosen[7],
            dialogue=chosen[8],
            loot_table=[("greater_healing_potion", 0.35), ("greater_mana_potion", 0.30), ("steel_longsword", 0.15), ("fire_bomb", 0.25)],
        )

    else:  # Floor 3 (Deep Sanctum)
        pool = [
            ("Voidstalker Fiend", 120, 28, 10, 15, 95, 60, "Demon", "flickers in and out of planar reality!"),
            ("Corrupted Dragonkin", 140, 32, 14, 11, 110, 75, "Dragon", "exhales suffocating sulfur fumes!"),
            ("Eldritch Fleshweaver", 130, 30, 12, 12, 100, 70, "Abomination", "twists flesh and bone into grotesque shapes."),
        ]
        chosen = random.choice(pool)
        return Enemy(
            name=chosen[0],
            hp=chosen[1],
            atk=chosen[2],
            defense=chosen[3],
            speed=chosen[4],
            xp_reward=chosen[5],
            gold_reward=chosen[6],
            enemy_type=chosen[7],
            dialogue=chosen[8],
            loot_table=[("greater_healing_potion", 0.45), ("greater_mana_potion", 0.40), ("berserker_brew", 0.30), ("dragonbone_blade", 0.10)],
        )


def spawn_boss(floor: int) -> Enemy:
    """Create unique floor bosses."""
    if floor == 1:
        return Enemy(
            name="Gorgoroth the Crypt Warden",
            hp=160,
            atk=18,
            defense=8,
            speed=9,
            xp_reward=120,
            gold_reward=100,
            is_boss=True,
            enemy_type="Undead",
            dialogue="raises his jagged tomb-axe: 'NO MORTAL TREADS UPON MORZAN'S DOMAIN!'",
            loot_table=[("iron_chainmail", 1.0), ("greater_healing_potion", 1.0), ("rusty_crypt_key", 1.0)],
        )
    elif floor == 2:
        return Enemy(
            name="Malakor the Dread Lich",
            hp=260,
            atk=28,
            defense=12,
            speed=12,
            xp_reward=220,
            gold_reward=180,
            is_boss=True,
            enemy_type="Undead",
            dialogue="levitates surrounded by whirling soul skulls: 'YOUR FLESH WILL FUEL MY PHYLACTERY!'",
            loot_table=[("crystal_staff", 1.0), ("royal_plate", 0.7), ("elixir_of_life", 1.0), ("ancient_sun_sigil", 1.0)],
        )
    else:
        return Enemy(
            name="Lord Morzan, Void Sovereign",
            hp=450,
            atk=38,
            defense=16,
            speed=14,
            xp_reward=500,
            gold_reward=400,
            is_boss=True,
            enemy_type="Demon",
            dialogue="steps from the weeping obsidian rift: 'I AM THE BEGINNING AND THE EXTINCTION. WITNESS TRUE DARKNESS!'",
            loot_table=[("dawn_bringer", 1.0), ("aegis_of_ages", 1.0)],
        )
