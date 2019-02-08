import sc2
import random
from sc2 import run_game, maps, Race, Difficulty, game_info
from sc2.player import Bot, Computer
from sc2.game_info import *
from sc2.constants import *
from sc2.position import *
from sc2.ids.buff_id import BuffId
#import cv2
#import numpy

class justaBot(sc2.BotAI):
    def __init__(self):
        self.MAX_WORKERS = 50
        self.GATEWAY_AMT = 0

    async def on_step(self, state):
        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        await self.build_gas()
        await self.expand()
        await self.build_gateway()
        await self.build_cybercore()
        await self.train_stalker()
        await self.stalker_attack()
        await self.build_twilight()
        await self.handle_upgrades()
        await self.fourgate()
        await self.boost_probes()
        await self.boost_council()
        await self.boost_warpgate()
        await self.build_robo()

    async def has_ability(self, ability, unit):
        abilities = await self.get_available_abilities(unit)
        if ability in abilities:
            return True
        else:
            return False

    async def build_workers(self):
        if len(self.units(NEXUS))*22 > len(self.units(PROBE)):
            if len(self.units(PROBE)) < self.MAX_WORKERS:
                for nexus in self.units(NEXUS).ready.noqueue:
                   if self.can_afford(PROBE):
                        await self.do(nexus.train(PROBE))

    async def build_pylons(self):
        if self.supply_left < 7 and not self.already_pending(PYLON):
            nexuses = self.units(NEXUS).ready
            #pos = self.start_location
            pos = self.start_location.position.towards_with_random_angle(self.game_info.map_center, random.randrange(5,10))
            if nexuses.exists:
                if self.can_afford(PYLON):
                    await self.build(PYLON, near=pos)

    async def build_gas(self):
        for nexus in self.units(NEXUS).ready:
            empty_geysers = self.state.vespene_geyser.closer_than(10.0, nexus)
            for empty_geyser in empty_geysers:
                if not self.can_afford(ASSIMILATOR):
                    break
                worker = self.select_build_worker(empty_geyser.position)
                if worker is None:
                    break
                if not self.units(ASSIMILATOR).closer_than(1.0, empty_geyser).exists and self.units(GATEWAY).exists:
                    await self.do(worker.build(ASSIMILATOR, empty_geyser))

    async def boost_probes(self):
        nexus = self.units(NEXUS).ready.random
        if not nexus.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
            abilities = await self.get_available_abilities(nexus)
            if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities and self.units(PROBE).amount <= 25:
                await self.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus))
        
    async def boost_warpgate(self):
        if self.units(CYBERNETICSCORE).exists and self.units(CYBERNETICSCORE).ready:
            nexus = self.units(NEXUS).ready.random
            ccore = self.units(CYBERNETICSCORE).ready.first
            if not ccore.has_buff(BuffId.CHRONOBOOSTENERGYCOST) and self.has_ability(RESEARCH_WARPGATE, ccore):
                abilities = await self.get_available_abilities(nexus)
                if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities:
                    await self.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, ccore))

    async def boost_council(self):
        if self.units(TWILIGHTCOUNCIL).exists and self.units(TWILIGHTCOUNCIL).ready:
            nexus = self.units(NEXUS).ready.random
            council = self.units(TWILIGHTCOUNCIL).ready.first
            if not council.has_buff(BuffId.CHRONOBOOSTENERGYCOST) and self.has_ability(RESEARCH_CHARGE, council):
                abilities = await self.get_available_abilities(nexus)
                if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities:
                    await self.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, council))

    async def expand(self):
        if self.units(NEXUS).amount < 2 and self.can_afford(NEXUS):
            await self.expand_now()

    async def build_gateway(self):
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random
            if self.units(GATEWAY).amount < 1 and self.can_afford(GATEWAY) and not self.units(WARPGATE).exists:
                await self.build(GATEWAY, near=pylon)

    async def fourgate(self):
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random
            gatecount = self.units(GATEWAY).amount + self.units(WARPGATE).amount + self.already_pending(GATEWAY)
            if self.units(WARPGATE).ready.exists:
                if self.can_afford(GATEWAY) and gatecount < 4 and self.units(WARPGATE).amount < 4 and self.units(GATEWAY).amount < 4 and self.already_pending(GATEWAY) < 2:
                    await self.build(GATEWAY, near=pylon)

    async def build_cybercore(self):
        if self.units(PYLON).ready.exists and self.units(PROBE).amount >= 21:
            pylon = self.units(PYLON).ready.random
            if self.units(GATEWAY).ready.exists:
                if not self.units(CYBERNETICSCORE):
                    if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                        await self.build(CYBERNETICSCORE, near=pylon)

    async def build_twilight(self):
        if self.units(CYBERNETICSCORE).ready.exists:
            pylon = self.units(PYLON).ready.random
            if not self.units(TWILIGHTCOUNCIL):
                if self.can_afford(TWILIGHTCOUNCIL) and not self.already_pending(TWILIGHTCOUNCIL):
                    await self.build(TWILIGHTCOUNCIL, near=pylon)

    async def build_robo(self):
        if self.units(TWILIGHTCOUNCIL).ready.exists:
            pos = self.start_location.position.towards_with_random_angle(self.game_info.map_center, random.randrange(5,10))
            if not self.units(ROBOTICSFACILITY):
                if self.can_afford(ROBOTICSFACILITY) and not self.already_pending(ROBOTICSFACILITY):
                    await self.build(ROBOTICSFACILITY, near=pos)

    async def train_stalker(self):
        for gateway in self.units(GATEWAY).ready.noqueue:
            if self.can_afford(STALKER) and self.units(STALKER).amount <= 2 and self.units(WARPGATE).amount == 0 and self.units(CYBERNETICSCORE).ready:
                await self.do(gateway.train(STALKER))

    def find_target(self, state):
        if len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]

    async def stalker_attack(self):
        if self.units(STALKER).amount > 15:
            for s in self.units(STALKER).idle:
                await self.do(s.attack(self.find_target(self.state)))

        elif self.units(STALKER).amount >= 2:
            if len(self.known_enemy_units) > 0:
                for s in self.units(STALKER).idle:
                    await self.do(s.attack(random.choice(self.known_enemy_units)))

    async def handle_upgrades(self):
        if self.units(CYBERNETICSCORE).ready.exists:
            cybercore = self.units(CYBERNETICSCORE).first
            if cybercore.noqueue and self.has_ability(RESEARCH_WARPGATE, cybercore):
                if self.can_afford(RESEARCH_WARPGATE):
                    await self.do(cybercore(RESEARCH_WARPGATE))

        if self.units(TWILIGHTCOUNCIL).ready.exists:
            twilight = self.units(TWILIGHTCOUNCIL).first
            if twilight.noqueue and await self.has_ability(RESEARCH_CHARGE, twilight):
                if self.can_afford(RESEARCH_CHARGE):
                    await self.do(twilight(RESEARCH_CHARGE))
                return
            elif await self.has_ability(RESEARCH_BLINK, twilight):
                if self.can_afford(RESEARCH_BLINK) and twilight.noqueue:
                    await self.do(twilight(RESEARCH_BLINK))


run_game(maps.get("(2)AcidPlantLE"), [
    Bot(Race.Protoss, justaBot()),
    Computer(Race.Terran, Difficulty.Hard)
    ], realtime=False)