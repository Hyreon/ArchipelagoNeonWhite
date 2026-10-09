# pyright: reportUnannotatedClassAttribute=false
# pyright: reportMatchNotExhaustive=false

import base64
import json
import zlib
from typing import Any
import math

from Options import OptionError
from BaseClasses import Item, MultiWorld, Tutorial
from rule_builder.rules import CanReachLocation, Rule

from worlds.AutoWorld import WebWorld, World

from .items import (
    NWItem,
    get_items_from_category,
    nw_item_groups,
    nw_items,
    single_pack_name,
    progressive_pack_name,
    normal_pack_name,
    numbered_pack_name
)
from .locations import (
    checks_in_sets_lvl,
    neon_white_get_locations,
    neon_white_level_name_internal,
    neon_white_levels_giftless,
    neon_white_levels_normal,
    neon_white_levels_sidequests,
    level_id
)

#from .Locations import PTLocation, pt_locations, pt_location_groups
from .options import (
    ExecutionDifficulty,
    Goal,
    KnowledgeDifficulty,
    MissionUnlockMethod,
    NeonWhiteOptions,
    AbilityPackTrim,
    LocalAbilities
)
from .regions import create_regions, default_mission_select_order, default_mission_of
from .rules import (
    LevelRequirements,
    LevelRequirementSet,
    Medal,
    get_mission_rank_required,
    import_json_to_data,
    set_rules,
    vanilla_items
)


class NeonWhiteWeb(WebWorld):
    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up Neon White integration for Archipelago multiworld games.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Badhamknibbs", "stxticOVFL"]
    )]
    theme = "partyTime"
    bug_report_page = "https://github.com/Badhamknibbs/ArchipelagoNeonWhite/issues"


# Keeping World slim so that it's easier to comprehend
class NeonWhiteWorld(World):
    """
    Neon White is a speedrunning FPS puzzle platformer made by freaks for freaks.
    Rush through a series of levels making smart use of your restricted cards to clear heaven of demons.
    """

    game = "Neon White"
    origin_region_name = "Central Heaven"
    options: NeonWhiteOptions  # pyright: ignore[reportIncompatibleVariableOverride]
    options_dataclass = NeonWhiteOptions
    web = NeonWhiteWeb()

    item_name_to_id = {name: data.id for name, data in nw_items.items()}  # noqa: RUF012

    location_name_to_id = neon_white_get_locations()

    item_name_groups = nw_item_groups
    location_name_groups = checks_in_sets_lvl

    requirements: dict[int, LevelRequirementSet] = {}

    ut_can_gen_without_yaml = True

    def __init__(self, multiworld: MultiWorld, player: int):
        super().__init__(multiworld, player)

        self.ordered_levels: list[str] = []   # Post-rando level list, to be split into missions every 11 levels
        self.early_levels: list[str] = []
        self.ranks_required: int = 0
        self.use_levels: bool = False

        self.requirement: LevelRequirementSet

    def generate_early(self) -> None:
        if not self.player_name.isascii():
            raise OptionError("Neon White yaml's slot name has invalid character(s).")
        if not all(x in nw_item_groups["Filler"] for x in self.options.filler_weights):
            raise OptionError("Non-filler in filler_weights")

        self.ordered_levels = []

        ut_regen = getattr(self.multiworld, "re_gen_passthrough", {})
        if (self.game in ut_regen):
            ut_regen: dict[str, Any] = ut_regen[self.game]
            self.ordered_levels = ut_regen.get("levels", [])
            self.early_levels = ut_regen["early_levels"]
            self.ranks_required = ut_regen.get("rank_requirement", 0)
            self.options.mission_count.value = ut_regen.get("mission_count", 0)
            self.options.difficulty_knowledge.value = ut_regen["difficulty_knowledge"]
            self.options.difficulty_execution.value = ut_regen["difficulty_execution"]
            self.options.boof_shenanigans.value = ut_regen["boof_shenanigans"]
            self.options.unlock_method.value = ut_regen["unlock_method"]
            self.options.medal_select.value = ut_regen["medal_select"]
            self.options.gifts.value = ut_regen["gifts"]
            self.options.sidequests.value = ut_regen["sidequests"]
            self.options.total_ranks.value = ut_regen.get("total_ranks", 0)

        self.use_levels = (
                self.options.unlock_method == MissionUnlockMethod.option_levels
        )  # removed reference to progressive levels, the old system; TODO find out if use_levels is being used right in each case

        req_select = int(self.options.difficulty_knowledge)
        req_select += int(self.options.difficulty_execution) * 10

        if (req_select not in NeonWhiteWorld.requirements):
            NeonWhiteWorld.requirements[req_select] = import_json_to_data(
                self.options.difficulty_knowledge, self.options.difficulty_execution)

        self.requirement = NeonWhiteWorld.requirements[req_select]
        medal_capped = max([Medal(x) for x in self.options.medal_select], default=Medal.Bronze)

        if not ut_regen:
            self.early_levels = []

            for level in neon_white_levels_normal:
                if (self.requirement.can_complete_level(level, medal_capped, LevelRequirements.FistOnly)
                    and self.requirement.can_complete_level(level, Medal.Gift, LevelRequirements.FistOnly)):
                    self.early_levels.append(level)

            cutoff = min(self.options.starting_level_count, len(self.early_levels))

            self.multiworld.random.shuffle(self.early_levels)
            self.early_levels = self.early_levels[:cutoff]

        if self.use_levels:
            remain: int = self.options.starting_level_count - len(self.early_levels)
            if remain > 0:
                levels = self.used_levels()

                self.early_levels += self.multiworld.random.choices(
                    [x for x in levels if x not in self.early_levels],
                    k = remain)

            for x in self.early_levels:
                self.multiworld.push_precollected(self.create_item(x))

        if (self.options.ability_pack_sizes.value and
                self.options.ability_pack_contents.value and
                self.options.local_ability_zones != LocalAbilities.option_disabled):
            self.ability_packs = self.generate_ability_packs()

            # self.vanilla_items = vanilla_items()
            # for i in range(0,len(self.ability_packs)):
            #     self.copies_for(i)  # makes adjustments
        else:
            self.ability_packs = None

        if (self.options.difficulty_knowledge <= KnowledgeDifficulty.option_vanilla
            or self.options.difficulty_execution <= ExecutionDifficulty.option_casual):
                self.multiworld.push_precollected(self.create_item("Katana"))

    def create_item(self, name: str) -> NWItem:
        return NWItem(name, nw_items[name].classification, nw_items[name].id, self.player)

    def create_regions(self):
        create_regions(self.player, self.multiworld, self.options)

    def get_filler_rando(self, k: int = 1):
        fillers = self.options.filler_weights;
        choices = self.multiworld.random.choices(list(fillers.keys()), weights=list(fillers.values()), k=k)
        generics = [x for x in nw_item_groups["Filler"] if nw_items[x].id % 100 < 50]
        return [self.multiworld.random.choice(generics) if x == "Generic" else x for x in choices]

    def create_items(self):
        itempool: list[Item] = []

        loc_count = len(self.get_locations())  # pyright: ignore[reportArgumentType]

        # Exclude cards that are assigned to progressive levels
        pack_cards = [ability for ability in self.options.ability_pack_contents.value]
        local_cards = [ability for ability in self.options.local_ability_contents.value]

        # Add soul cards
        itempool += [self.create_item(card) for card in get_items_from_category("Card") if card not in pack_cards and card not in local_cards]

        zones = self.zones()

        if self.options.local_ability_zones != LocalAbilities.option_disabled:
            # Add local cards
            itempool += [self.create_item(single_pack_name(zone, ability)) for zone in zones for ability in local_cards]

            if self.ability_packs:
                if self.options.ability_pack_progressive:
                    itempool += [self.create_item(progressive_pack_name(zone))
                                for zone in zones
                                for _ in range(len(self.options.ability_pack_sizes.value))]
                else:
                    if len(self.options.ability_pack_sizes == 1):
                        itempool += [self.create_item(normal_pack_name(zone))
                                    for zone in zones]
                    else:
                        itempool += [self.create_item(numbered_pack_name(zone, number))
                                    for zone in zones
                                    for number in range(len(self.options.ability_pack_sizes.value))]

        match self.options.unlock_method:
            case MissionUnlockMethod.option_missions:
                # Add a number of mission unlock items equal to the mission count - 1
                itempool.extend(self.create_item("Mission Unlock") for _ in range(self.options.mission_count.value - 1))
            case MissionUnlockMethod.option_ranks:
                # Make sure we add the neon ranks that we need
                total_ranks_clamp: int = min(self.options.total_ranks.value, loc_count - len(itempool))

                if (not getattr(self.multiworld, "re_gen_passthrough", {})):
                    self.ranks_required = int(total_ranks_clamp * (self.options.ranks_required_percent / 100))

                itempool.extend(self.create_item("Neon Rank") for _ in range(total_ranks_clamp))
            case MissionUnlockMethod.option_levels:
                levels = neon_white_levels_normal + neon_white_levels_giftless
                if self.options.sidequests:
                    levels.extend(neon_white_levels_sidequests)
                itempool.extend([self.create_item(level) for level in levels])



        prec = self.multiworld.precollected_items[self.player].copy()

        for item in itempool:
            if item in prec:
                itempool.remove(item)
                prec.remove(item)

        # Fill the rest with filler
        itempool += [self.create_item(x) for x in self.get_filler_rando(k=loc_count - len(itempool))]

        self.multiworld.itempool += itempool

    def copies_for(self, level_index, safe = False):
        max_level_copies = (
            1 if self.options.unlock_method == MissionUnlockMethod.option_levels
              else len(self.options.ability_pack_sizes.value)
        )
        if not self.options.ability_pack_trimming:
            return max_level_copies
        else:
            # this is a mess, isn't it?
            # it's literally not possible to do this if any removable tier can contain more items than a lower, removable tier
            # we'll need to fix that later by making the # of cards unlocked per progressive access item vary per group. later.
            relevant_cards = set(self.vanilla_items[level_index]).intersection(self.options.ability_pack_contents.value)
            group_ability_packs = self.ability_packs[level_index].copy()
            relevant_sections = []
            irrelevant_sections = []
            for start,end,section in self.access_into_sections(group_ability_packs): # looks at sections > 0
                if start == 0 or any(card in relevant_cards for card in section): #start = 0 is no cards, sometimes level access alone is enough to matter
                    relevant_sections.append(section) # end - start is the length
                else:
                    irrelevant_sections.append(section)

            if not safe:
                self.ability_packs[level_index].clear()
                for section in relevant_sections:
                    self.ability_packs[level_index].extend(section)
                for section in irrelevant_sections:
                    self.ability_packs[level_index].extend(section)

                print(level_index, ":", len(relevant_sections), "(", self.ability_packs[level_index], ") : ", relevant_cards)

            return len(relevant_sections)

    def access_into_sections(self, group_ability_packs):
        sizes = self.options.ability_pack_sizes.value
        sections = []
        for i in range(0, len(sizes)):
            start = 0
            if i > 0:
                start = sizes[i - 1]
            end = sizes[i]
            sections.append((start, end, group_ability_packs[start:end].copy()))
        return sections

    def get_filler_item_name(self) -> str:
        return self.get_filler_rando()[0]

    def set_rules(self):
        set_rules(self.multiworld, self, self.options)
        rule: Rule | None = None
        match self.options.goal:
            case Goal.option_3bosses:
                # intentionally fail if no medal select
                if len(self.options.medal_select.value) == 0:
                    raise OptionError("Not enough medals selected")
                medalname = max([Medal(x) for x in self.options.medal_select]).name
                rule = (
                    CanReachLocation(f"The Clocktower {medalname} Completion") &
                    CanReachLocation(f"The Third Temple {medalname} Completion") &
                    CanReachLocation(f"Absolution {medalname} Completion")
                )

        if rule is None:
            raise OptionError("End goal not configured")

        self.set_completion_rule(rule)

    def extend_hint_information(self, hint_data: dict[int, dict[int, str]]):
        hint_data[self.player] = {}

        for location in self.multiworld.get_locations(self.player):
            if location.address is not None and location.parent_region is not None:
                p_region = location.parent_region
                if p_region.name.startswith("Level: ") and p_region.entrances[0].parent_region is not None:
                    hint_data[self.player][location.address] = f"{p_region.entrances[0].parent_region.name}"

    def fill_slot_data(self):

        extra: dict[str, Any] = {}  # pyright: ignore[reportExplicitAny]

        if self.use_levels:
            dumps = json.dumps([neon_white_level_name_internal[x] for x in self.ordered_levels], separators=(",", ":"))

            cpobj = zlib.compressobj(level=9, wbits=-15, memLevel=9)
            encoded_levels = base64.a85encode(cpobj.compress(dumps.encode()) + cpobj.flush()).decode()

            extra["level_order"] = encoded_levels

            if self.options.unlock_method == MissionUnlockMethod.option_missions:
                extra["mission_costs"] = list(range(self.options.mission_count))
            elif self.options.unlock_method == MissionUnlockMethod.option_ranks:
                extra["mission_costs"] = [
                    get_mission_rank_required(self, i + 1)
                        for i in range(self.options.mission_count)
                ]
        
        if self.ability_packs:
            extra["ability_packs"] = self.ability_packs
        
        options_to_show = [
            "difficulty_knowledge", "difficulty_execution", "boof_shenanigans",
            "medal_select", "gifts", "sidequests", "unlock_method", "goal",
            "death_link"]

        if self.options.death_link:
            options_to_show.extend(["death_link_amn", "death_link_res"])

        if self.options.death_link:
            options_to_show.extend(["total_ranks"])

        return {
            "early_levels": self.early_levels,
            "options": self.options.as_dict(*options_to_show)
        } | extra
    
    def generate_ability_packs(self) -> dict[str, Any]:
        ability_packs = []

        ability_count = len(self.options.ability_pack_contents.value)
        expected_count = sum(pack_size for pack_size in self.options.ability_pack_sizes)
        ratio = ability_count / expected_count
        updated_pack_sizes = [ratio * pack_size for pack_size in self.options.ability_pack_sizes]

        # collect the decimals and add 1 to the highest one
        highest = (0, None)
        for i in range(len(updated_pack_sizes)):
            original_pack_size = updated_pack_sizes[i]
            updated_pack_sizes[i] = math.floor(updated_pack_sizes[i])
            remainder = updated_pack_sizes[i] - original_pack_size
            if highest[0] < remainder:
                highest = (remainder, i)
        if highest[1]:
            updated_pack_sizes[highest[1]] += 1

        zones = self.zones()
        num_groups = len(zones)
        for _ in range(0,num_groups):
            order = self.options.ability_pack_contents.value.copy()
            self.random.shuffle(order)

            start = 0
            zone_packs = []
            for size in updated_pack_sizes:
                end = start+size
                zone_packs.append(order[start:end])
                start += size

            ability_packs.append(zone_packs)

        print(ability_packs)
        return ability_packs

    def used_levels(self):
        levels = neon_white_levels_normal + neon_white_levels_giftless
        if self.options.sidequests:
            levels.extend(neon_white_levels_sidequests)
        return levels

    def zones(self):
        if self.options.local_ability_zones == LocalAbilities.option_per_level:
            return self.used_levels()
        elif self.options.local_ability_zones == LocalAbilities.option_per_vanilla_mission or self.options.unlock_method == MissionUnlockMethod.option_levels:
            return default_mission_select_order(self.options.sidequests)
        elif self.options.local_ability_zones == LocalAbilities.option_per_mission:
            return [f"Mission {n + 1}" for n in range(self.options.mission_count)]

    def zone_for(self, level):
        if self.options.local_ability_zones == LocalAbilities.option_per_level:
            return level
        elif self.options.local_ability_zones == LocalAbilities.option_per_mission:
            for connection in self.get_region("Level: " + level).entrances:
                return connection.parent_region.name
            raise RuntimeError(f"No region was assigned to the level {level}")
        elif self.options.local_ability_zones == LocalAbilities.option_per_vanilla_mission:
            return default_mission_of(level)

    def zone_id_for(self, level):
        if self.options.local_ability_zones == LocalAbilities.option_per_level:
            return level_id(level)
        elif self.options.local_ability_zones != LocalAbilities.option_disabled:
            mission = self.zone_for(level)
            vanilla_missions = default_mission_select_order()
            if mission in vanilla_missions:
                return vanilla_missions.index(mission)
            else:
                return int(mission.split(" ")[-1]) - 1


    @staticmethod
    def interpret_slot_data(slot_data: dict[str, Any]) -> dict[str, Any]:
        extra: dict[str, Any] = {}  # pyright: ignore[reportExplicitAny]
        unlock = slot_data["options"]["unlock_method"]

        if (unlock != MissionUnlockMethod.option_levels):
            reverse = {v: k for k, v in neon_white_level_name_internal.items()}

            dcobj = zlib.decompressobj(-15)
            decoded = json.loads(dcobj.decompress(base64.a85decode(slot_data["level_order"])) + dcobj.flush())

            extra["levels"] = [reverse[x] for x in decoded]
            extra["mission_count"] = len(slot_data["mission_costs"])
            extra["rank_requirement"] = slot_data["mission_costs"][-1]

            if (unlock == MissionUnlockMethod.option_ranks):
                extra["total_ranks"] = slot_data["options"]["total_ranks"]

        return {
            "unlock_method": unlock,
            "early_levels": slot_data["early_levels"],
            "difficulty_knowledge": slot_data["options"]["difficulty_knowledge"],
            "difficulty_execution": slot_data["options"]["difficulty_execution"],
            "boof_shenanigans": slot_data["options"]["boof_shenanigans"],
            "gifts": slot_data["options"]["gifts"],
            "sidequests": slot_data["options"]["sidequests"],
            "medal_select": slot_data["options"]["medal_select"]
        } | extra
