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
    option_ability_pack = 4
    default = 1

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

class AbilityPackDomain(OptionList):
    """
    By default, items are obtained once per world.
    However, you can split items of your choice
    to be distributed in packs across levels or missions.
    """
    display_name = "Ability Packs"
    option_disabled = 1
    option_per_vanilla_mission = 2
    option_per_custom_mission = 3
    option_per_level = 4
    default = option_per_level

class AbilityPackSizes(OptionList):
    """
    The size of each ability pack, and the amount of packs, rounded to the nearest percent.
    This must add up to 100%.
    The default settings [16.7, 50.0, 33.3] add 3 packs per zone,
    where the first one grants 2/12 items, the second one grants 6/12,
    and the last one grants 4/12. it's a good curve for progressive.
    Some other examples:
    [100.0] means one pack to grant every ability pack ability
    [10.0, 20.0, 30.0, 40.0] means 4 packs, each bigger than the last
    """
    display_name = "Ability Packs - Sizes"
    default = [16.7, 50.0, 33.3]

class AbilityPackAbilities(OptionList):
    """
    What abilities are unlocked by ability packs.
    When an item is listed here, it will not be added to the main pool.
    Careful when messing with this - if it doesn't match an ability name, the world won't generate.
    """
    display_name = "Ability Packs - Affected Abilities"
    default = ["Godspeed - Fire", "Stomp - Discard", "Elevate - Discard", "Godspeed - Discard", "Elevate - Fire", "Stomp - Fire", "Purify - Fire", "Fireball - Fire", "Purify - Discard", "Dominion - Fire", "Fireball - Discard", "Dominion - Discard"]

class AbilityPackSmoothing(OptionList):
    """
    With purely random abilities, you aren't guaranteed anything useful. Pack smoothing fixes that.
    This overrides the pack size. You need a lot of abilities to do anything in some levels, even at expert or master level.
    This logic has little effect on missions but is still applied.
    No Smoothing: Your only assurance is that by your last pack, you have everything, including what you need.
    Traversal: Your first ability pack contains whatever you need to traverse some level in the zone at your skill level.
    First Grants Check: Your first ability pack guarantees a check at your skill level, supposing you have all global items.
    All Grant Check: If you have ability packs 1 to X, you will be able to clear at least X checks.
    === DOES NOT DO ANYTHING ATM ===
    """
    display_name = "Ability Packs - Smoothing"
    option_no_smoothing = 1
    option_traversal = 2  # if every check wants an ability, you start with it
    option_first_grants_check = 3  # picks a route to either gift or get >= the lowest medal, that isn't a superset of a solve for something smaller but still >= lower medal, and grants everything for at least it
    option_all_grant_check = 4  # repeats this process for each pack, picking higher medals
    default = option_traversal

class AbilityPackTrim(Toggle):
    """
    When enabled, useless packs are removed.
    A pack is useless if grants no new cards, and is not required to ability the level.
    With this setting enabled, you are not guaranteed the same amount of items
    across all seeds. Additionally, some levels will have less ability cards.
    === DOES NOT DO ANYTHING ATM ===
    """
    display_name = "Ability Packs - Trimming"

class AbilityPackIsProgressive(DefaultOnToggle):
    """
    If enabled, ability packs unlock abilities in a fixed
    order regardless of which ones you pick up.
    If disabled, ability packs can be obtained out of
    order depending on which ones you pick up.
    """
    display_name = "Ability Packs - Progressive"

class AbilityPackVariation(DefaultOnToggle):
    """
    If enabled, the ability pack sizes are treated as a suggestion rather than a rule.
    This has a stronger effect on levels with fewer cards.
    === DOES NOT DO ANYTHING ATM ===
    """
    display_name = "Ability Packs - Vary Pack Size"


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
    ability_pack: AbilityPackDomain
    ability_pack_sizes: AbilityPackSizes
    ability_pack_abilities: AbilityPackAbilities
    ability_pack_smoothing: AbilityPackSmoothing
    ability_pack_trimming: AbilityPackTrim
    ability_pack_progressive: AbilityPackIsProgressive
    ability_pack_variation: AbilityPackVariation
