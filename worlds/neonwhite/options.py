# pyright: reportUnannotatedClassAttribute=false

from dataclasses import dataclass

from Options import (
    Choice,
    DeathLink,
    DefaultOnToggle,
    ItemDict,
    OptionSet,
    PerGameCommonOptions,
    Range,
    StartInventoryPool,
    Toggle,
    OptionList
)

from .locations import neon_white_levels_medals
from .abilities import abilities

local_ability_groups = [
    "Fires",
    "Discards"
]

class KnowledgeDifficulty(Choice):
    """
    How much understanding of the games mechanics is expected to figure out the solution to a given medal/gift/etc.
    Vanilla: *Only* allow cards and strats the basegame shows you.
    Casual: Expects the bare minimum, only tricks that are taught with in-game tutorials to beat the vanilla game.
    Standard: Incorporates hidden but usually intended or otherwise easy to intuit tech/ideas.
    Expert: Further includes some more advanced tech that is often only relevant to speedrunners.
    Master: Encompasses everything else from level-specific tech to extremely niche game quirks or nuances.
    """
    display_name = "Knowledge Difficulty"
    option_vanilla = 1
    option_casual = 2
    option_standard = 3
    option_expert = 4
    option_master = 5
    default = 3

class ExecutionDifficulty(Choice):
    """
    How hard it is to actually execute a given solution to a given medal/gift/etc, assuming all knowledge.
    Vanilla: *Only* allow cards and strats the basegame shows you.
    Casual: Can be done by a brand-new player with minimal hassle.
    Standard: Consistently doable by a player who has all aces, especially players with dev medals.
    Expert: Doable by a player who has all dev medals and is competent with advanced tech.
    Master: Unreasonably difficult solutions that are inconsistent/overly precise to the vast majority of players.
    """
    display_name = "Execution Difficulty"
    option_vanilla = 1
    option_casual = 2
    option_standard = 3
    option_expert = 4
    option_master = 5
    default = 3

class BoofShenanigans(Toggle):
    """
    Whether to include things like clips and far off Book of Life usages in the logic.
    === DOES NOT DO ANYTHING ATM ===
    """
    display_name = "Book of Life Shenanigans"

class Gifts(DefaultOnToggle):
    """
    Whether or not to make gifts checks.
    """

class Sidequests(DefaultOnToggle):
    """
    Whether or not to make sidequest completions checks.
    """

class MissionUnlockMethod(Choice):
    """
    How missions are unlocked to progress through the game.
    Ranks: Fills the pool with Neon Ranks, each mission requiring a number of ranks to unlock. See Rank Requirement.
    Missions: 1 Mission Unlock item is added to the pool per mission, each obtained unlocking the next locked mission.
    Levels: Each level is an item that must be collected
    Ability Packs: No unlock items specifically are added to the pool. You may play any level that you have an ability pack in. (You MUST have ability packs enabled)
    """
    display_name = "Mission Unlock Method"
    option_ranks = 1
    option_missions = 2
    option_levels = 3
    option_ability_packs = 4
    default = option_ranks

class StartingLevelCount(Range):
    """
    The amount of Levels for you to start with for Levels unlock method.
    This also influences how many fist-only levels are added early into the level pool for other unlock methods.
    """
    display_name = "Starting Level Count"
    range_start = 1
    default = 5
    range_end = 10


class MedalSelect(OptionSet):
    """
    Which medals to have as checks.
    Format as a comma-separated list of medal names: ["Bronze", "Ace"].
    Medals available are: Bronze, Silver, Gold, Ace, and Dev. Case-insensitive.
    """
    display_name = "Medal Selection"
    valid_keys = [x.casefold() for x in neon_white_levels_medals]
    valid_keys_casefold = True
    default = {"Bronze", "Ace"}

class TotalRanks(Range):
    """
    How many total Neon Ranks to add to the pool.
    Only applies when Mission Unlock Method is set to Ranks.
    """
    display_name = "Total Neon Ranks"
    range_start = 1
    default = 100
    range_end = 300

class RanksRequiredPercentage(Range):
    """
    Percentage of existing Neon Ranks required to open the last mission.
    The rest of the mission requirements will scale accordingly.
    Only applies when Mission Unlock Method is set to Ranks.
    """
    display_name = "Ranks Required Percentage"
    range_start = 1
    default = 80
    range_end = 100


class MissionCount(Range):
    """
    The amount of Missions for the game to have when ranks or mission unlock method is chosen.
    Spreads levels as evenly as it can, then spreads across the later half with the remainder.
    """
    display_name = "Mission Count"
    range_start = 3
    default = 11
    range_end = 60

class LevelGradient(Range):
    """
    The amount of "variance" in % to have in the random level selection for the ranks/mission unlock methods.
    A lower value means, as the levels are selected, you will, on average, need more and more cards.
    A higher value means much more randomness in the selection.
    """
    display_name = "Level Selection Variance"
    range_start = 0
    range_end = 100
    default = 50

class Traps(DefaultOnToggle):
    """
    Whether negative effects on the Neon White world are added to the item pool.
    === DOES NOT DO ANYTHING ATM ===
    """
    display_name = "Traps"

class Goal(Choice):
    """
    What the goal to complete should be.
    3bosses - Beat The Clocktower, The Third Temple, and Absolution with the highest medal selected.
    TrueEnding - Gather all memories and write Green into the Book of Life. (WILL FAIL TO GEN)
    """
    display_name = "Goal"
    option_3bosses = 1
    option_trueending = 2
    default = 1

class FillerWeights(ItemDict):
    """
    How often different types of filler should appear.
    "Generic" means to pick from a list of filler that don't do anything.
    Only filler items (+ Generic) can be listed here.
    """
    display_name = "Filler Weights"
    default = {
        "Generic": 10,
        "Health Card": 1,
        "Ammo Card": 1
    }

class DeathLinkAmnesty(Range):
    """
    How many deaths it takes to send a DeathLink.
    """
    display_name = "Death Link Amnesty"
    range_start = 1
    range_end = 30
    default = 1

class DeathLinkResets(Range):
    """
    How many **level resets** it takes to send a DeathLink.
    Setting to 0 disables sending them on resets.
    """
    display_name = "Level Reset Death Link Amnesty"
    range_start = 0
    range_end = 50
    default = 20

class PerMissionContents(OptionList):
    """
    By default, discarding and firing each card is an item, obtained once per world.
    You can assign items of your choice to be distributed multiple times, once per vanilla mission.
    Be careful not to put the same ability in both per mission and per level, or the world won't generate!
    Setting this to something like ["Elevate - Discard"] will mean you will get items like Rebirth - Elevate - Discard,
    unlocking Elevate - Discard in all of those, and only those, levels.
    """
    display_name = "Local Abilities - Per Mission"
    valid_keys = frozenset(local_ability_groups + abilities)
    default = []

class LocalUseRandomMissionContents(Toggle):
    """
    When off (by default), Local Abilities - Per Mission
    are distributed based on vanilla missions, like Rebirth - Elevate - Discard.
    Turning this on will distribute based on your
    randomized missions, like Mission 1 - Elevate - Discard.
    """
    display_name = "Local Abilities - Use Randomized Missions"

class PerLevelContents(OptionList):
    """
    By default, discarding and firing each card is an item, obtained once per world.
    You can assign items of your choice to be distributed multiple times, once per level.
    Be careful not to put the same ability in both per mission and per level, or the world won't generate!
    Setting this to something like ["Elevate - Discard"] will mean you will get items like Cascade - Elevate - Discard,
    unlocking Elevate - Discard in all of those, and only those, levels.
    """
    display_name = "Local Abilities - Per Level"
    valid_keys = frozenset(local_ability_groups + abilities)
    default = []

class AbilityPackScope(Choice):
    """
    If local ability distribution is creating too many items,
    you can always reduce the scope by putting them into packs.
    A pack will grant multiple abilities for its zone when obtained.
    """
    display_name = "Ability Pack Scope"
    option_disabled = 1
    option_per_mission = 2
    option_per_level = 3
    option_both = 4
    default = option_disabled

class AbilityPackSizes(OptionList):
    """
    The size of each ability pack relative to each other,
    and the amount of packs.
    The default of [3, 5, 4] makes pack 2 the biggest,
    with 5/12 items. Pack 1 has 3/12 and pack 3 has 4/12.
    It is designed for progressive packs to give a satisfying arc.
    If there are fewer than 12 relevant items, or more than
    12 relevant items, the game will adjust accordingly.
    """
    display_name = "Ability Packs - Sizes"
    default = [3, 5, 4]

class AbilityPackIsProgressive(DefaultOnToggle):
    """
    If enabled, ability packs unlock abilities in a fixed
    order regardless of which ones you pick up.
    If disabled, ability packs can be obtained out of
    order depending on which ones you pick up.
    """
    display_name = "Ability Packs - Progressive"


@dataclass
class NeonWhiteOptions(PerGameCommonOptions):
    start_inventory_from_pool: StartInventoryPool
    difficulty_knowledge: KnowledgeDifficulty
    difficulty_execution: ExecutionDifficulty
    medal_select: MedalSelect
    gifts: Gifts
    sidequests: Sidequests
    unlock_method: MissionUnlockMethod
    total_ranks: TotalRanks
    ranks_required_percent: RanksRequiredPercentage
    mission_count: MissionCount
    level_gradient: LevelGradient
    starting_level_count: StartingLevelCount
    goal: Goal
    filler_weights: FillerWeights
    death_link: DeathLink
    death_link_amn: DeathLinkAmnesty
    death_link_res: DeathLinkResets
    bad_effects: Traps
    boof_shenanigans: BoofShenanigans
    per_mission_contents: PerMissionContents
    local_use_random_mission_contents: LocalUseRandomMissionContents
    per_level_contents: PerLevelContents
    ability_pack_scope: AbilityPackScope
    ability_pack_sizes: AbilityPackSizes
    ability_pack_progressive: AbilityPackIsProgressive
