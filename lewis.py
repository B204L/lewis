import sc2
import random
from sc2 import run_game, maps, Race, Difficulty, game_info
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, GATEWAY, CYBERNETICSCORE, STALKER

class justaBot(sc2.BotAI):
    async def on_step(self, iteration):
        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        await self.build_gas()
        await self.expand()
        await self.build_gateway()
        await self.build_cybercore()
        await self.train_stalker()
        await self.stalker_attack()

    async def build_workers(self):
        for nexus in self.units(NEXUS).ready.noqueue:
            if self.can_afford(PROBE):
                await self.do(nexus.train(PROBE))

    async def build_pylons(self):
        if self.supply_left < 5 and not self.already_pending(PYLON):
            nexuses = self.units(NEXUS).ready
            if nexuses.exists:
                if self.can_afford(PYLON):
                    await self.build(PYLON, near=nexuses.first)

    async def build_gas(self):
        for nexus in self.units(NEXUS).ready:
            empty_geysers = self.state.vespene_geyser.closer_than(10.0, nexus)
            for empty_geyser in empty_geysers:
                if not self.can_afford(ASSIMILATOR):
                    break
                worker = self.select_build_worker(empty_geyser.position)
                if worker is None:
                    break
                if not self.units(ASSIMILATOR).closer_than(1.0, empty_geyser).exists:
                    await self.do(worker.build(ASSIMILATOR, empty_geyser))

    async def expand(self):
        if self.units(NEXUS).amount < 2 and self.can_afford(NEXUS):
            await self.expand_now()

    async def build_gateway(self):
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random
            if self.units(GATEWAY).amount < 1 and self.can_afford(GATEWAY):
                await self.build(GATEWAY, near=pylon)
            if self.units(GATEWAY).amount < 4 and self.units(NEXUS).amount == 2 and self.can_afford(GATEWAY):
                await self.build(GATEWAY, near=pylon)

    async def build_cybercore(self):
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random
            if self.units(GATEWAY).ready.exists:
                if not self.units(CYBERNETICSCORE):
                    if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                         await self.build(CYBERNETICSCORE, near=pylon)

    async def train_stalker(self):
         for gateway in self.units(GATEWAY).ready.noqueue:
            if self.can_afford(STALKER) and self.units(NEXUS).amount == 2 and self.supply_left > 0:
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

        elif self.units(STALKER).amount > 3:
            if len(self.known_enemy_units) > 0:
                for s in self.units(STALKER).idle:
                    await self.do(s.attack(random.choice(self.known_enemy_units)))


run_game(maps.get("(2)AcidPlantLE"), [
    Bot(Race.Protoss, justaBot()),
    Computer(Race.Terran, Difficulty.Hard)
    ], realtime=False)