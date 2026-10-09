from collections.abc import Iterable
from typing import NamedTuple

from BaseClasses import Item, ItemClassification

from .locations import neon_white_level_name_internal
from .regions import neon_white_missions, neon_white_missions_sq, names_of_missions

class NWItem(Item):
    game: str = "Neon White"
    prog_id = 400
    card_id = 500
    level_id = 600
    misc_id = 800
    ability_progressive_id = 20000  # 121 levels + 18 vanilla missions + the 60 custom missions = 199
    ability_group_id       = 20200  # up to 10 copies by number (5 medals + gift + 4 extra for future proofing); 0 is for blank, when there's only one pack per zone
    ability_local_id       = 22400  # each of the 14 items per zone (levels without the item are included for simplicity, and for future proofing) # this is intended if a pack has 1 item, not used for now

    card_classification = ItemClassification.progression | ItemClassification.useful
    usefiller_classification = ItemClassification.useful | ItemClassification.deprioritized | ItemClassification.skip_balancing

class NWItemData(NamedTuple):
    category: str
    id: int
    classification: ItemClassification

def get_items_from_category(category: str) -> Iterable[str]:
    for name, item in nw_items.items():
        if item.category == category:
            yield name

def possible_zones():
    zones = []
    zones.extend(neon_white_level_name_internal.keys())
    zones.extend(names_of_missions(neon_white_missions))
    zones.extend(names_of_missions(neon_white_missions_sq))
    zones.extend([f"Mission {n}" for n in range(1, 61)])
    return zones

abilities = [
    "Katana",
    "Book of Life",
    "Purify - Fire",
    "Purify - Discard",
    "Elevate - Fire",
    "Elevate - Discard",
    "Godspeed - Fire",
    "Godspeed - Discard",
    "Stomp - Fire",
    "Stomp - Discard",
    "Fireball - Fire",
    "Fireball - Discard",
    "Dominion - Fire",
    "Dominion - Discard"
]

def progressive_pack_name(zone: str):
    return f"{zone} - Progressive Abilities"

def normal_pack_name(zone: str):
    return f"{zone} - Ability Pack"

def numbered_pack_name(zone: str, number: int):
    return f"{zone} - Ability Pack {number}"

def single_pack_name(zone: str, contents: str):
    return f"{contents} - {zone}"

def possible_packs_for(zone: str):
    packs = [progressive_pack_name(zone), normal_pack_name(zone)]
    packs.extend(numbered_pack_name(zone, x) for x in range(1, 11))
    return packs

nw_items: dict[str, NWItemData] = {
    item: NWItemData("Card", NWItem.card_id + i + 1, NWItem.card_classification)
        for i, item in enumerate(abilities)
} | {
    "Neon Rank":            NWItemData("Progression", NWItem.prog_id + 0,
        ItemClassification.progression_deprioritized_skip_balancing),
    "Mission Unlock":       NWItemData("Progression", NWItem.prog_id + 1,
        ItemClassification.progression),

    # Generic should not be found in the world; it's just a helper item for FillerWeights
    # because im lazy and i don't want to use schema
    "Generic": NWItemData("Filler", NWItem.misc_id + 99,
        ItemClassification.filler),
    "Heavenly Delight Ticket": NWItemData("Filler", NWItem.misc_id + 0,
        ItemClassification.filler),
    "Insight Crystal Dust": NWItemData("Filler", NWItem.misc_id + 1,
        ItemClassification.filler),
    "Health Card": NWItemData("Filler", NWItem.misc_id + 51,
        NWItem.usefiller_classification),
    "Ammo Card": NWItemData("Filler", NWItem.misc_id + 52,
        NWItem.usefiller_classification)

} | {
    f"{level}": NWItemData("Level", NWItem.level_id + i, ItemClassification.progression)
        for i, level in enumerate(neon_white_level_name_internal.keys())
} | {
    progressive_pack_name(zone): NWItemData("Progressive Abilities", NWItem.ability_progressive_id + i, ItemClassification.progression)
        for i, zone in enumerate(possible_zones())
} | {
    normal_pack_name(zone): NWItemData("Ability Pack", NWItem.ability_group_id + i, ItemClassification.progression)
        for i, zone in enumerate(possible_zones())
} | {
    numbered_pack_name(zone, n): NWItemData("Ability Pack", NWItem.ability_group_id + i + 200*n, ItemClassification.progression)
        for i, zone in enumerate(possible_zones())
        for n in range(1, 11)
} | {
    single_pack_name(zone, ability): NWItemData("Local Ability", NWItem.ability_local_id + i, ItemClassification.progression)
        for i, zone in enumerate(possible_zones())
        for ability in abilities
}

item_categories = [
    "Progression",
    "Card",
    "Filler",
    "Level",
    "Local Ability",
    "Ability Pack",
    "Progressive Abilities"
]

nw_item_groups = { cat: set(get_items_from_category(cat)) for cat in item_categories }
