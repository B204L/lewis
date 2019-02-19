import sc2
import random
from sc2 import run_game, maps, Race, Difficulty, game_info, position, Result
from sc2.player import Bot, Computer
from sc2.game_info import *
from sc2.constants import *
from sc2.position import *
from sc2.unit import Unit
from sc2.ids.buff_id import BuffId
positions = []

####define locations as global vars and append to positions[]####
rand_townhalls = self.units(NEXUS).random
enemy_start = self.known_enemy_structures

rand_struct_pos = self.units(PYLON).random_on_distance(2, 8)
positions.append(rand_struct_pos)

rand_nexus_pos = self.units(NEXUS).random
positions.append(rand_nexus_pos)

#needs to find enemy start on 4 player maps
rand_proxy_pos = enemy_start.position.towards_with_random_angle(self.game_info.map_center, random.randrange(70, 100))
positions.append(rand_proxy_pos)

main_ramp = self.main_base_ramp
positions.append(main_ramp)

natural_expansion =

third_expansion = 

fourth_expansion = 

fifth_expansion = 

enemy_main = 

enemy_natural = 

random_map_location = 
####define actions below####

####build structure####

async def expo_nexus(self):
    if self.can_afford(NEXUS):
        await self.expand_now()

async def base_pylon(self):
    if not self.already_pending(PYLON):
        nexuses = self.units(NEXUS).random
        pos = nexuses.position.towards_with_random_angle(self.game_info.map_center, random.randrange(0,10))#to2.random_on_distance(4)
        if self.units(NEXUS).exists:
            if self.can_afford(PYLON):
                await self.build(PYLON, near=pos)

async def supply_pylon(self):
    pylons = self.units(PYLON).random
    if self.units(PYLON).exists:
        if self.can_afford(PYLON):
            await self.build(PYLON, near=pylons)

async def build_gas(self):
    for nexus in self.units(NEXUS).ready:
        empty_geysers = self.state.vespene_geyser.closer_than(10.0, nexus)
        for empty_geyser in empty_geysers:
            if not self.can_afford(ASSIMILATOR):
                break
            worker = self.select_build_worker(empty_geyser.position)
            if worker is None:
                break
            if not self.units(ASSIMILATOR).closer_than(1.0, empty_geyser).exists and self.units(GATEWAY).exists and self.supply_left <= 16:
                await self.do(worker.build(ASSIMILATOR, empty_geyser))

async def build_gateway(self):
    if self.units(PYLON).ready.exists:
        pylon = self.units(PYLON).ready.random
        if self.can_afford(GATEWAY):
            await self.build(GATEWAY, near=rand_struct_pos)

async def build_cybercore(self):
    if self.units(PYLON).ready.exists and self.units(GATEWAY).ready.exists:
        pylon = self.units(PYLON).ready.random
        if not self.units(CYBERNETICSCORE):
            if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                await self.build(CYBERNETICSCORE, near=rand_struct_pos)

async def build_forge(self):
    if self.units(PYLON).ready.exists:
        pylon = self.units(PYLON).ready.random
        if self.can_afford(FORGE):
            await self.build(FORGE, near=rand_struct_pos)

async def build_robo(self):
    if self.units(PYLON).ready.exists:
        pylon = self.units(PYLON).ready.random
        if self.can_afford(ROBOTICSFACILITY):
            await self.build(ROBOTICSFACILITY, near=rand_struct_pos)

async def build_stargate(self):
    if self.units(PYLON).ready.exists:
        pylon = self.units(PYLON).ready.random
        if self.can_afford(STARGATE):
            await self.build(STARGATE, near=rand_struct_pos)

async def build_twilight(self):
    if self.units(PYLON).ready.exists:
        pylon = self.units(PYLON).ready.random
        if not self.units(TWILIGHTCOUNCIL):
            if self.can_afford(TWILIGHTCOUNCIL) and not self.already_pending(TWILIGHTCOUNCIL):
                await self.build(TWILIGHTCOUNCIL, near=rand_struct_pos)

async def build_shrine(self):
    if self.units(PYLON).ready.exists:
        pylon = self.units(PYLON).ready.random
        if not self.units(DARKSHRINE):
            if self.can_afford(DARKSHRINE) and self.units(TWILIGHTCOUNCIL).ready.exists and not self.already_pending(DARKSHRINE):
                await self.build(DARKSHRINE, near=rand_struct_pos)

async def build_fleet(self):
    if self.units(PYLON).ready.exists:
        pylon = self.units(PYLON).ready.random
        if not self.units(FLEETBEACON):
            if self.can_afford(FLEETBEACON) and self.units(STARGATE).ready.exists and not self.already_pending(FLEETBEACON):
                await self.build(FLEETBEACON, near=rand_struct_pos)

async def build_archives(self):
    if self.units(PYLON).ready.exists:
        pylon = self.units(PYLON).ready.random
        if not self.units(TEMPLARARCHIVES):
            if self.can_afford(TEMPLARARCHIVES) and self.units(TWILIGHTCOUNCIL).ready.exists and not self.already_pending(TEMPLARARCHIVES):
                await self.build(TEMPLARARCHIVES, near=rand_struct_pos)

async def build_robobay(self):
    if self.units(PYLON).ready.exists:
        pylon = self.units(PYLON).ready.random
        if not self.units(ROBOTICSBAY):
            if self.can_afford(ROBOTICSBAY) and self.units(ROBOTICSFACILITY).ready.exists and not self.already_pending(ROBOTICSBAY):
                await self.build(ROBOTICSBAY, near=rand_struct_pos) 

async def build_cannon(self):
    if self.units(PYLON).ready.exists:
        pylon = self.units(PYLON).ready.random
        if self.can_afford(PHOTONCANNON) and self.units(FORGE).ready.exists:
            await self.build(PHOTOCANNON, near=self.units(NEXUS).ready.random)

async def build_battery(self):
    if self.units(PYLON).ready.exists:
        pylon = self.units(PYLON).ready.random
        if self.can_afford(SHIELDBATTERY) and self.units(CYBERNETICSCORE).ready.exists:
            await self.build(SHIELDBATTERY, near=rand_struct_pos)