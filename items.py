"""
items.py - Items, weapons, armors, potions, and equipment catalog.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Item:
    id: str
    name: str
    description: str
    item_type: str  # "weapon", "armor", "consumable", "quest"
    value: int      # Gold buy/sell value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "item_type": self.item_type,
            "value": self.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Item":
        item_id = data.get("id", "")
        if item_id in ITEM_REGISTRY:
            return ITEM_REGISTRY[item_id]
        return cls(**data)


@dataclass
class Weapon(Item):
    attack_bonus: int = 0
    crit_bonus: float = 0.05  # Bonus crit chance (e.g. 0.05 = +5%)
    weapon_type: str = "Sword"

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "attack_bonus": self.attack_bonus,
            "crit_bonus": self.crit_bonus,
            "weapon_type": self.weapon_type,
        })
        return d


@dataclass
class Armor(Item):
    defense_bonus: int = 0
    hp_bonus: int = 0
    armor_type: str = "Medium"

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "defense_bonus": self.defense_bonus,
            "hp_bonus": self.hp_bonus,
            "armor_type": self.armor_type,
        })
        return d


@dataclass
class Consumable(Item):
    effect: str = "heal_hp"  # "heal_hp", "heal_mp", "buff_atk", "buff_def", "bomb"
    power: int = 30
    duration: int = 0        # For buffs (number of turns)

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "effect": self.effect,
            "power": self.power,
            "duration": self.duration,
        })
        return d


# -------------------------------------------------------------
# GLOBAL ITEM CATALOG
# -------------------------------------------------------------

ITEM_REGISTRY: Dict[str, Item] = {
    # --- WEAPONS ---
    "rusty_sword": Weapon(
        id="rusty_sword",
        name="Rusty Iron Sword",
        description="A nicked blade with dried rust. Better than bare hands.",
        item_type="weapon",
        value=15,
        attack_bonus=5,
        crit_bonus=0.05,
        weapon_type="Sword",
    ),
    "steel_longsword": Weapon(
        id="steel_longsword",
        name="Steel Longsword",
        description="Well-balanced Eldorian steel with a sharp edge.",
        item_type="weapon",
        value=60,
        attack_bonus=14,
        crit_bonus=0.08,
        weapon_type="Sword",
    ),
    "shadow_daggers": Weapon(
        id="shadow_daggers",
        name="Twin Shadow Daggers",
        description="Obsidian daggers that glint with silent malice. High critical strikes.",
        item_type="weapon",
        value=85,
        attack_bonus=12,
        crit_bonus=0.22,
        weapon_type="Dagger",
    ),
    "apprentice_staff": Weapon(
        id="apprentice_staff",
        name="Apprentice Birch Staff",
        description="Carved from elder birch, channels basic arcane energy.",
        item_type="weapon",
        value=20,
        attack_bonus=6,
        crit_bonus=0.05,
        weapon_type="Staff",
    ),
    "crystal_staff": Weapon(
        id="crystal_staff",
        name="Arcane Crystal Staff",
        description="A pulsating sapphire gem rests upon a silver spire.",
        item_type="weapon",
        value=90,
        attack_bonus=18,
        crit_bonus=0.10,
        weapon_type="Staff",
    ),
    "dragonbone_blade": Weapon(
        id="dragonbone_blade",
        name="Dragonbone Greatsword",
        description="Forged from ancient drake fangs. Tremendous crushing force.",
        item_type="weapon",
        value=200,
        attack_bonus=30,
        crit_bonus=0.15,
        weapon_type="Greatsword",
    ),
    "dawn_bringer": Weapon(
        id="dawn_bringer",
        name="Dawnbringer (Legendary)",
        description="Gleams with sunfire. Banishes shadows and smites fiends.",
        item_type="weapon",
        value=400,
        attack_bonus=45,
        crit_bonus=0.25,
        weapon_type="Holy Blade",
    ),

    # --- ARMOR ---
    "tattered_clothes": Armor(
        id="tattered_clothes",
        name="Tattered Adventurer Clothes",
        description="Frayed cloth offering minimal protection against cuts.",
        item_type="armor",
        value=5,
        defense_bonus=1,
        hp_bonus=0,
        armor_type="Cloth",
    ),
    "leather_armor": Armor(
        id="leather_armor",
        name="Reinforced Leather Tunic",
        description="Tough boiled hide fitted with bronze studs.",
        item_type="armor",
        value=40,
        defense_bonus=6,
        hp_bonus=15,
        armor_type="Leather",
    ),
    "iron_chainmail": Armor(
        id="iron_chainmail",
        name="Iron Chainmail Hauberk",
        description="Interlocking iron rings providing solid protection.",
        item_type="armor",
        value=85,
        defense_bonus=12,
        hp_bonus=35,
        armor_type="Mail",
    ),
    "mage_robes": Armor(
        id="mage_robes",
        name="Runewoven Silk Robes",
        description="Imbued with protective barriers against physical and occult harm.",
        item_type="armor",
        value=75,
        defense_bonus=8,
        hp_bonus=25,
        armor_type="Robe",
    ),
    "royal_plate": Armor(
        id="royal_plate",
        name="Knight's Sunforged Plate",
        description="Heavy polished plate armour decorated in gold filigree.",
        item_type="armor",
        value=180,
        defense_bonus=20,
        hp_bonus=60,
        armor_type="Plate",
    ),
    "aegis_of_ages": Armor(
        id="aegis_of_ages",
        name="Aegis of Ages (Legendary)",
        description="Mythical enchanted armour said to turn away dragon fire.",
        item_type="armor",
        value=450,
        defense_bonus=32,
        hp_bonus=110,
        armor_type="Plate",
    ),

    # --- CONSUMABLES ---
    "minor_healing_potion": Consumable(
        id="minor_healing_potion",
        name="Minor Health Potion",
        description="A crimson vial that restores 45 HP.",
        item_type="consumable",
        value=20,
        effect="heal_hp",
        power=45,
    ),
    "greater_healing_potion": Consumable(
        id="greater_healing_potion",
        name="Greater Health Potion",
        description="A shimmering draught restoring 110 HP.",
        item_type="consumable",
        value=50,
        effect="heal_hp",
        power=110,
    ),
    "elixir_of_life": Consumable(
        id="elixir_of_life",
        name="Elixir of Life",
        description="Divine nectar that fully restores all HP and cures ailments.",
        item_type="consumable",
        value=120,
        effect="heal_hp",
        power=999,
    ),
    "mana_draught": Consumable(
        id="mana_draught",
        name="Mana Draught",
        description="Glowing azure potion restoring 30 MP.",
        item_type="consumable",
        value=25,
        effect="heal_mp",
        power=30,
    ),
    "greater_mana_potion": Consumable(
        id="greater_mana_potion",
        name="Greater Mana Potion",
        description="Deep starlight essence restoring 75 MP.",
        item_type="consumable",
        value=60,
        effect="heal_mp",
        power=75,
    ),
    "berserker_brew": Consumable(
        id="berserker_brew",
        name="Berserker's Draught",
        description="Boils your blood, boosting Attack by +10 for 3 turns.",
        item_type="consumable",
        value=35,
        effect="buff_atk",
        power=10,
        duration=3,
    ),
    "stoneskin_tonic": Consumable(
        id="stoneskin_tonic",
        name="Stoneskin Tonic",
        description="Hardens your flesh, boosting Defense by +8 for 3 turns.",
        item_type="consumable",
        value=35,
        effect="buff_def",
        power=8,
        duration=3,
    ),
    "fire_bomb": Consumable(
        id="fire_bomb",
        name="Alchemist's Fire Bomb",
        description="Throw at enemy to deal 55 explosive fire damage instantly.",
        item_type="consumable",
        value=40,
        effect="bomb",
        power=55,
    ),

    # --- QUEST & PUZZLE ITEMS ---
    "rusty_crypt_key": Item(
        id="rusty_crypt_key",
        name="Rusty Crypt Key",
        description="An old iron skeleton key found in the crypt depths.",
        item_type="quest",
        value=0,
    ),
    "ancient_sun_sigil": Item(
        id="ancient_sun_sigil",
        name="Ancient Sun Sigil",
        description="A golden medallion shaped like the dawn. Slits into the sanctuary door.",
        item_type="quest",
        value=0,
    ),
    "void_core": Item(
        id="void_core",
        name="Dark Void Crystal",
        description="A whispering shard of pitch-black crystal extracted from an elite fiend.",
        item_type="quest",
        value=100,
    ),
}


def get_item(item_id: str) -> Optional[Item]:
    """Retrieve an item from registry by ID."""
    return ITEM_REGISTRY.get(item_id)
