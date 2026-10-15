from .bases import NeonWhiteTestBase

from ..locations import (
    neon_white_level_name_internal,
    level_id
)
from ..regions import (
    default_mission_of
)
from ..items import (
    possible_zones
)

class TestZoneDefinitions(NeonWhiteTestBase):
    options = {
        "local_ability_zones": "per_vanilla_mission"
    }

    def test_items(self):

        for item in self.multiworld.itempool:
            print(item)

    def test_zone_definitions(self) -> None:

        # for level in neon_white_level_name_internal.keys():
        #     print(level, level_id(level), default_mission_of(level))

        # for i,zone in enumerate(possible_zones()):
        #     print(i, zone)

        # ???
        ...

    def test_absolution_all_access_allowed(self):
        ...
        # When granted ability packs, absolution should be reachable
        # bob_level_id = sm64_entrances_to_level["Bob-omb Battlefield"]
        # bob_entrance_id = self.world.area_connections[bob_level_id]
        # bob_entrance = sm64_level_to_entrances[bob_entrance_id]
        # self.assertTrue(self.can_reach_region(bob_entrance))
