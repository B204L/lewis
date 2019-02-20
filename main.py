import sc2
import random
#import actions
#import build_orders
#import gather_test_data
from sc2 import run_game, maps, Race, Difficulty, game_info, position, Result
from sc2.player import Bot, Computer
from sc2.game_info import *
from sc2.constants import *
from sc2.position import *
from sc2.unit import Unit
from sc2.ids.buff_id import BuffId
import cv2
import numpy as np
import time

class lewis(sc2.BotAI):
    def __init__(self):
        self.actions = []
        self.MAX_WORKERS = 50
        self.GATEWAY_AMT = 0
        self.WARPGATE_UPGRADE = False
        self.CHARGE_UPGRADE = False
        self.ITERATIONS_PER_MINUTE = 165
        self.pylonCoords = []
        self.nexusCoords = []
        self.gateCoords = []
        self.warpCoords = []
        self.coreCoords = []
        self.roboCoords = []
        self.forgeCoords = []
        self.twilightCoords = []
    
    def select_target(self, state):
        return self.enemy_start_locations[0]

    def select_mid(self, state):
        return self.game_info.map_center

    def on_end(self, game_result):
        print('--- on_end called ---')
        print(game_result)

        if game_result == Result.Victory:
            np.save("test_data/pylonCoords/{}.npy".format(str(int(time.time()))), np.array(self.pylonCoords))
            np.save("test_data/nexusCoords/{}.npy".format(str(int(time.time()))), np.array(self.nexusCoords))
            np.save("test_data/gateCoords/{}.npy".format(str(int(time.time()))), np.array(self.gateCoords))
            np.save("test_data/warpCoords/{}.npy".format(str(int(time.time()))), np.array(self.warpCoords))
            np.save("test_data/coreCoords/{}.npy".format(str(int(time.time()))), np.array(self.coreCoords))
            np.save("test_data/roboCoords/{}.npy".format(str(int(time.time()))), np.array(self.roboCoords))
            np.save("test_data/forgeCoords/{}.npy".format(str(int(time.time()))), np.array(self.forgeCoords))
            np.save("test_data/twilightCoords/{}.npy".format(str(int(time.time()))), np.array(self.twilightCoords))

    async def on_step(self, iteration):
        self.iteration = iteration
        self.game_time = self.iteration / self.ITERATIONS_PER_MINUTE
        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        await self.build_gas()
        await self.expand()
        await self.build_gateway()
        await self.build_cybercore()
        await self.train_stalker()
        await self.rush_defense()
        await self.build_twilight()
        await self.handle_upgrades()
        await self.fourgate()
        await self.boost_probes()
        await self.boost_council()
        await self.boost_warpgate()
        #await self.build_order()
        await self.warp_new_units()
        await self.build_robo()
        await self.train_immortal()
        await self.build_forge()
        await self.boost_forge()
        await self.win_game()
        await self.control_fighting_army()
        #await self.intel()
        await self.structure_positions()

    async def structure_positions(self):
        #expansion_list = []
        #expansion_list.append(self.expansion_locations.keys())

        #list(self.expansion_locations.keys())
        if i > 1:
            first_base = list(self.expansion_locations.keys())[0]
            print(first_base)
            second_base = list(self.expansion_locations.keys())[0]
            print(second_base)
            i + 1

        for pylon in self.units(PYLON):
            if pylon.position not in self.pylonCoords:
                self.pylonCoords.append(pylon.position)
            #print (self.pylonCoords)
        for nexus in self.units(NEXUS):
            if nexus.position not in self.nexusCoords:
                self.nexusCoords.append(nexus.position)

        for gateway in self.units(GATEWAY):
            if gateway.position not in self.gateCoords:
                self.gateCoords.append(gateway.position)

        for warpgate in self.units(WARPGATE):
            if warpgate.position not in self.warpCoords:
                self.warpCoords.append(warpgate.position)

        for cybercore in self.units(CYBERNETICSCORE):
            if cybercore.position not in self.coreCoords:
                self.coreCoords.append(cybercore.position)

        for robo in self.units(ROBOTICSFACILITY):
            if robo.position not in self.roboCoords:
                self.roboCoords.append(robo.position)

        for forge in self.units(FORGE):
            if forge.position not in self.forgeCoords:
                self.forgeCoords.append(forge.position)

        for twilight in self.units(TWILIGHTCOUNCIL):
            if twilight.position not in self.twilightCoords:
                self.twilightCoords.append(twilight.position)

    async def intel(self):
        game_data = np.zeros((self.game_info.map_size[1], self.game_info.map_size[0], 3), np.uint8)
        
        draw_dict = {
                    NEXUS: [15, (0, 255, 0)],
                    PYLON: [3, (20, 235, 0)],
                    PROBE: [1, (55, 200, 0)],

                    ASSIMILATOR: [2, (55, 200, 0)],
                    GATEWAY: [3, (200, 100, 0)],
                    CYBERNETICSCORE: [3, (150, 150, 0)],
                    FORGE: [3, (180, 180, 0)],
                    TWILIGHTCOUNCIL: [3, (200, 200, 0)],
                    ZEALOT: [2, (255, 100, 0)],
                    STALKER: [2, (100, 255, 0)],
                    IMMORTAL: [3, (200, 200, 50)],
                }

        for unit_type in draw_dict:
            for unit in self.units(unit_type).ready:
                pos = unit.position
                cv2.circle(game_data, (int(pos[0]), int(pos[1])), draw_dict[unit_type][0], draw_dict[unit_type][1], -1)

        for enemy_unit in self.known_enemy_units:
            if not enemy_unit.is_structure:
                worker_names = ["probe",
                                "scv",
                                "drone"]
                pos = enemy_unit.position
                if enemy_unit.name.lower() in worker_names:
                    cv2.circle(game_data, (int(pos[0]), int(pos[1])), 1, (55, 0, 155), -1)
                else:
                    cv2.circle(game_data, (int(pos[0]), int(pos[1])), 3, (50, 0, 215), -1)

        flipped = cv2.flip(game_data, 0)
        resized = cv2.resize(flipped, dsize=None, fx=2, fy=2)
        cv2.imshow('Intel', resized)
        cv2.waitKey(1) 

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
            nexuses = self.units(NEXUS).random
            pos = nexuses.position.towards_with_random_angle(self.game_info.map_center, random.randrange(0,10))#to2.random_on_distance(4)
            if self.units(NEXUS).exists:
                if self.can_afford(PYLON):
                    await self.build(PYLON, near=pos)
        
    async def build_order(self):
        if self.supply_left <= 14 and not self.already_pending(PYLON):
            nexuses = self.units(NEXUS).ready
            if self.units(NEXUS).exists and self.can_afford(PYLON):
                await self.build(PYLON, near=nexuses)
        if self.supply_left <= 16 and not self.already_pending(GATEWAY):
            if self.can_afford(GATEWAY) and not self.units(GATEWAY).exists:
                pylon = self.units(PYLON).ready.random
                await self.build(GATEWAY, near=pylon)

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

    async def warp_new_units(self):
        for warpgate in self.units(WARPGATE).ready:
            abilities = await self.get_available_abilities(warpgate)
            if AbilityId.WARPGATETRAIN_ZEALOT in abilities and self.units(STALKER).amount >= 7:
                pylon = self.units(PYLON).ready.random
                pos = pylon.position.to2.random_on_distance(4)
                placement = await self.find_placement(AbilityId.WARPGATETRAIN_ZEALOT, pos, placement_step=1)
                if placement is None:
                    print("Can't Place")
                    return
                await self.do(warpgate.warp_in(ZEALOT, placement))
            if AbilityId.WARPGATETRAIN_STALKER in abilities and self.units(STALKER).amount <= 7:
                pylon = self.units(PYLON).ready.random
                pos = pylon.position.to2.random_on_distance(4)
                placement = await self.find_placement(AbilityId.WARPGATETRAIN_STALKER, pos, placement_step=1)
                if placement is None:
                    print("Can't Place")
                    return
                await self.do(warpgate.warp_in(STALKER, placement))

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
                if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities and not self.WARPGATE_UPGRADE:
                    await self.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, ccore))
                    self.WARPGATE_UPGRADE = True

    async def boost_council(self):
        if self.units(TWILIGHTCOUNCIL).exists and self.units(TWILIGHTCOUNCIL).ready:
            nexus = self.units(NEXUS).ready.random
            council = self.units(TWILIGHTCOUNCIL).ready.first
            if not council.has_buff(BuffId.CHRONOBOOSTENERGYCOST) and self.has_ability(RESEARCH_CHARGE, council):
                abilities = await self.get_available_abilities(nexus)
                if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities and not self.CHARGE_UPGRADE:
                    await self.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, council))
                    self.CHARGE_UPGRADE = True
            #if not council.has_buff(BuffId.CHRONOBOOSTENERGYCOST) and self.has_ability(RESEARCH_BLINK, council):
            #    abilities = await self.get_available_abilities(nexus)
            #    if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities:
            #        await self.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, council))

    async def boost_forge(self):
        if self.units(FORGE).exists and self.units(FORGE).ready and self.CHARGE_UPGRADE == True and self.WARPGATE_UPGRADE == True:
            nexus = self.units(NEXUS).ready.random
            forges = self.units(FORGE).ready.random
            if not forges.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                abilities = await self.get_available_abilities(nexus)
                if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities:
                    await self.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, forges))

    async def expand(self):
        if self.units(NEXUS).amount < 2 and self.can_afford(NEXUS):
            await self.expand_now()
        if self.units(NEXUS).amount <= 2 and self.game_time >= 8.00:
            await self.expand_now()
            self.MAX_WORKERS = 80

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
                if self.can_afford(GATEWAY) and gatecount < 8 and self.units(WARPGATE).amount < 8 and self.units(GATEWAY).amount < 8 and self.already_pending(GATEWAY) < 4 and self.minerals >= 800:
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
        if self.units(TWILIGHTCOUNCIL).exists:
            pylon = self.units(PYLON).ready.random
            if not self.units(ROBOTICSFACILITY):
                if self.can_afford(ROBOTICSFACILITY) and not self.already_pending(ROBOTICSFACILITY):
                    await self.build(ROBOTICSFACILITY, near=pylon)

    async def train_immortal(self):
        if self.units(ROBOTICSFACILITY).ready.exists:
            robo = self.units(ROBOTICSFACILITY).ready.random
            if self.can_afford(IMMORTAL) and self.units(IMMORTAL).amount < 2 and robo.noqueue:
                await self.do(robo.train(IMMORTAL))
            if self.can_afford(IMMORTAL) and self.minerals >= 800 and robo.noqueue:
                await self.do(robo.train(IMMORTAL))

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

    async def rush_defense(self):
        if self.units(STALKER).amount > 1:
            if len(self.known_enemy_units) > 1:
                for s in self.units(STALKER).idle:
                    await self.do(s.attack(random.choice(self.known_enemy_units)))
        if self.units(ZEALOT).amount > 2:
            if len(self.known_enemy_units) > 1:
                for s in self.units(ZEALOT).idle:
                    await self.do(s.attack(random.choice(self.known_enemy_units)))
        if self.units(IMMORTAL).amount > 0:
            if len(self.known_enemy_units) > 1:
                for s in self.units(IMMORTAL).idle:
                    await self.do(s.attack(random.choice(self.known_enemy_units)))

    async def build_forge(self):
        if self.units(TWILIGHTCOUNCIL).exists:
            pylon = self.units(PYLON).ready.random
            forgecount = self.units(FORGE).amount + self.already_pending(FORGE)
            if self.can_afford(FORGE) and forgecount <= 1:
                await self.build(FORGE, near=pylon)

    async def handle_upgrades(self):
        if self.units(CYBERNETICSCORE).ready.exists:
            cybercore = self.units(CYBERNETICSCORE).first
            if cybercore.noqueue and self.has_ability(RESEARCH_WARPGATE, cybercore):
                if self.can_afford(RESEARCH_WARPGATE) and not self.units(WARPGATE).exists:
                    await self.do(cybercore(RESEARCH_WARPGATE))

        if self.units(TWILIGHTCOUNCIL).ready.exists:
            twilight = self.units(TWILIGHTCOUNCIL).first
            if twilight.noqueue and await self.has_ability(RESEARCH_CHARGE, twilight):
                if self.can_afford(RESEARCH_CHARGE):
                    await self.do(twilight(RESEARCH_CHARGE))
                return
            #elif await self.has_ability(RESEARCH_BLINK, twilight):
            #    if self.can_afford(RESEARCH_BLINK) and twilight.noqueue:
            #        await self.do(twilight(RESEARCH_BLINK))
        if self.units(FORGE).ready.exists:
            forge_weapons = self.units(FORGE).ready.random
            if forge_weapons.noqueue and await self.has_ability(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1, forge_weapons):
                if self.can_afford(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1):
                    await self.do(forge_weapons(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1))
                return
            if forge_weapons.noqueue and await self.has_ability(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2, forge_weapons):
                if self.can_afford(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2):
                    await self.do(forge_weapons(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2))
                return
            if forge_weapons.noqueue and await self.has_ability(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL3, forge_weapons):
                if self.can_afford(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL3):
                    await self.do(forge_weapons(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL3))
                return

        if self.units(FORGE).ready.exists:
            forge_armor = self.units(FORGE).ready.random
            if forge_armor.noqueue and await self.has_ability(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1, forge_armor):
                if self.can_afford(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1):
                    await self.do(forge_armor(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1))
                return
            if forge_armor.noqueue and await self.has_ability(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL2, forge_armor):
                if self.can_afford(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL2):
                    await self.do(forge_armor(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL2))
                return
            if forge_armor.noqueue and await self.has_ability(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL3, forge_armor):
                if self.can_afford(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL3):
                    await self.do(forge_armor(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL3))
                return

    async def win_game(self):
        army = (self.units(ZEALOT) | self.units(IMMORTAL) | self.units(STALKER)).idle
        # wait with first attack until we have 5 units
        if army.amount >= 40:
            for unit in army:
                # we dont see anything, go to enemy start location (only works on 2 player maps)
                if not self.known_enemy_units:  
                    self.actions.append(unit.attack(self.enemy_start_locations[0]))
                    await self.do_actions(self.actions)
                    self.actions = []
                # otherwise, attack closest unit
                else:
                    nexuses = self.units(NEXUS).ready.random
                    pos = nexuses.position.towards_with_random_angle(self.game_info.map_center, random.randrange(5,10))#to2.random_on_distance(4)
                    #closest_enemy = self.known_enemy_units.closest_to(unit)
                    self.actions.append(unit.attack(pos))
                    await self.do_actions(self.actions)
                    self.actions = []

    async def control_fighting_army(self):
        # no need to do anything here if we dont see anything
        if not self.known_enemy_units:
            return
        army = self.units(ZEALOT) | self.units(STALKER) | self.units(IMMORTAL)
        # create selection of dangerous enemy units.
        # bunker and uprooted spine dont have weapon, but should be in that selection
        # also add spinecrawler and cannon if they are not ready yet and have no weapon
        enemy_fighters = self.known_enemy_units.filter(
            lambda u: u.can_attack or u.type_id in {BUNKER, SPINECRAWLERUPROOTED, SPINECRAWLER, PHOTONCANNON}
        )
        for unit in army:
            if enemy_fighters:
                # select enemies in range
                in_range_enemies = enemy_fighters.in_attack_range_of(unit)
                if in_range_enemies:
                    # attack enemy with lowest hp of the ones in range
                    lowest_hp = min(in_range_enemies, key=lambda e: e.health + e.shield)
                    self.actions.append(unit.attack(lowest_hp))
                else:
                    # no unit in range, go to closest
                    self.actions.append(unit.move(enemy_fighters.closest_to(unit)))
            else:
                # no dangerous enemy at all, attack closest of everything
                self.actions.append(unit.attack(self.known_enemy_units.closest_to(unit)))

run_game(maps.get("(2)AcidPlantLE"), [
    Bot(Race.Protoss, lewis()),
    Computer(Race.Zerg, Difficulty.VeryHard)
    ], realtime=False)