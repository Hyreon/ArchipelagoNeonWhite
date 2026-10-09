from BaseClasses import MultiWorld, Region

from .locations import (
    NWLocation,
    neon_white_get_locations,
    neon_white_levels_giftless,
    neon_white_levels_medals,
    neon_white_levels_normal,
    neon_white_levels_sidequests,
    level_id
)
from .options import MissionUnlockMethod, NeonWhiteOptions

# Mission names and their counts
neon_white_missions = [
    ("Rebirth", 10),
    ("Killer Inside", 10),
    ("Only Shallow", 10),
    ("The Old City", 3),
    ("The Burn That Cures", 10),
    ("Covenant", 10),
    ("Reckoning", 10),
    ("Benediction", 10),
    ("Apocrypha", 10),
    ("The Third Temple", 2),
    ("Thousand Pound Butterfly", 10),
    ("Hand of God", 2)
]
neon_white_missions_sq = [
    ("Red Sidequests", 8),
    ("Violet Sidequests", 8),
    ("Yellow Sidequests", 8),
]

def default_mission_of(level):
    level_number = level_id(level)
    levels_scanned = 0
    for mission in (neon_white_missions + neon_white_missions_sq):
        levels_here = mission[1]
        if levels_scanned + levels_here > level_number:
            return mission[0]
        else:
            levels_scanned += levels_here

def default_mission_select_order():
    return [mission_context[0] for mission_context in (neon_white_missions + neon_white_missions_sq)]

def names_of_missions(mission_list): # abstraction, in case we change the internal format of missions and their counts later
    return (m[0] for m in mission_list)

def create_regions(player: int, multiworld: MultiWorld, options: NeonWhiteOptions):
    if (options.unlock_method == MissionUnlockMethod.option_levels):
        # Basegame missions
        mission_list = names_of_missions(neon_white_missions)
        print(mission_list)
        if options.sidequests:
            mission_list.extend(names_of_missions(neon_white_missions_sq))
    else:
        # 121 levels split amongst X missions, differing from the base game
        mission_list = [f"Mission {x + 1}" for x in range(options.mission_count)]

    heaven_regions: list[Region] = [Region("Central Heaven", player, multiworld, None)]

    neon_white_locations = neon_white_get_locations()

    # Create regions and add locations
    heaven_regions.extend([Region(mission, player, multiworld) for mission in mission_list])

    for level in neon_white_levels_normal + neon_white_levels_giftless:
        check_region = Region("Level: " + level, player, multiworld)
        for medal in options.medal_select:
            check_name: str = level + " " + medal.title() + " Completion"
            new_location = NWLocation(player, check_name, neon_white_locations[check_name], check_region)
            # Make the highest medal a priority location
            #if medal == options.medal_cap - 1: new_location.progress_type = LocationProgressType.PRIORITY
            check_region.locations.append(new_location)
        if options.gifts and level not in neon_white_levels_giftless:
            check_name = level + " Gift"
            new_location = NWLocation(player, check_name, neon_white_locations[check_name], check_region)
            #new_location.progress_type = LocationProgressType.PRIORITY
            check_region.locations.append(new_location)

        heaven_regions.append(check_region)

    if options.sidequests:
        for level in neon_white_levels_sidequests:
            check_region = Region("Level: " + level, player, multiworld)
            check_name = level + " Completion"
            new_location = NWLocation(player, check_name, neon_white_locations[check_name], check_region)
            #new_location.progress_type = LocationProgressType.PRIORITY
            check_region.locations.append(new_location)
            heaven_regions.append(check_region)

    multiworld.regions += heaven_regions
