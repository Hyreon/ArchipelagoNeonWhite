from collections.abc import Iterable
from typing import NamedTuple

from BaseClasses import Item, ItemClassification

from .locations import neon_white_level_name_internal
from .regions import neon_white_missions, neon_white_missions_sq, names_of_missions
from .abilities import abilities

class NWItem(Item):
    game: str = "Neon White"
    prog_id = 400
    card_id = 500
    level_id = 600
    misc_id = 800
    ability_local_id       = 22400  # space reserved for packs at 20000 (may never come)

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
    zones.extend(remap_zone_list(neon_white_level_name_internal.keys(), map_to_level = True))
    zones.extend(remap_zone_list(names_of_missions(neon_white_missions), map_to_level = False))
    zones.extend(names_of_missions(neon_white_missions_sq))  # no need to remap
    zones.extend([f"Mission {n}" for n in range(1, 61)])  # no need to remap
    return zones

# Ben just HAD to be extra and name a mission and level the same thing >.<
def zone_name(zone, map_to_level=None):
    if zone != "The Third Temple" or map_to_level is None:
        return zone
    if map_to_level:
        return "Third Temple Boss"
    else:
        return "Third Temple Mission"

def zone_to_name(zone):
    if zone == "Third Temple Boss" or zone == "Third Temple Mission":
        return "The Third Temple"
    else:
        return zone

def remap_zone_list(zones, map_to_level=None):
    return [zone_name(zone, map_to_level) for zone in zones]

def local_item_name(zone: str, contents: str, map_to_level):
    zone = zone_name(zone, map_to_level)
    return f"{zone} - {contents}"

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
    local_item_name(zone, ability, None): NWItemData("Local Ability", NWItem.ability_local_id + i, ItemClassification.progression)
        for i, zone in enumerate(possible_zones())
        for ability in abilities
}

item_categories = [
    "Progression",
    "Card",
    "Filler",
    "Level",
    "Local Ability"
]

nw_item_groups = { cat: set(get_items_from_category(cat)) for cat in item_categories }
