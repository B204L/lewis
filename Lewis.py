import sc2
import random
import math
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
import build_order

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
        self.top_spawn = False
        self.probeScout = False
        self.opponentRace = 1
        self.baseSearched = False
        self.scouts_and_spots = {}
        self.be_defensive = True
    
    def select_target(self, state):
        return self.enemy_start_locations[0]

    def select_mid(self, state):
        return self.game_info.map_center

    def on_end(self, game_result):
        print('--- on_end called ---')
        print(game_result)        

        if game_result == Result.Victory and self.top_spawn == True:
            np.save("data/test_data/structure_coords/acid_plant/top/pylonCoords/{}.npy".format(str(int(time.time()))), np.array(self.pylonCoords))
            np.save("data/test_data/structure_coords/acid_plant/top/nexusCoords/{}.npy".format(str(int(time.time()))), np.array(self.nexusCoords))
            np.save("data/test_data/structure_coords/acid_plant/top/gateCoords/{}.npy".format(str(int(time.time()))), np.array(self.gateCoords))
            np.save("data/test_data/structure_coords/acid_plant/top/warpCoords/{}.npy".format(str(int(time.time()))), np.array(self.warpCoords))
            np.save("data/test_data/structure_coords/acid_plant/top/coreCoords/{}.npy".format(str(int(time.time()))), np.array(self.coreCoords))
            np.save("data/test_data/structure_coords/acid_plant/top/roboCoords/{}.npy".format(str(int(time.time()))), np.array(self.roboCoords))
            np.save("data/test_data/structure_coords/acid_plant/top/forgeCoords/{}.npy".format(str(int(time.time()))), np.array(self.forgeCoords))
            np.save("data/test_data/structure_coords/acid_plant/top/twilightCoords/{}.npy".format(str(int(time.time()))), np.array(self.twilightCoords))

        if game_result == Result.Victory and self.top_spawn == False:
            np.save("data/test_data/structure_coords/acid_plant/bottom/pylonCoords/{}.npy".format(str(int(time.time()))), np.array(self.pylonCoords))
            np.save("data/test_data/structure_coords/acid_plant/bottom/nexusCoords/{}.npy".format(str(int(time.time()))), np.array(self.nexusCoords))
            np.save("data/test_data/structure_coords/acid_plant/bottom/gateCoords/{}.npy".format(str(int(time.time()))), np.array(self.gateCoords))
            np.save("data/test_data/structure_coords/acid_plant/bottom/warpCoords/{}.npy".format(str(int(time.time()))), np.array(self.warpCoords))
            np.save("data/test_data/structure_coords/acid_plant/bottom/coreCoords/{}.npy".format(str(int(time.time()))), np.array(self.coreCoords))
            np.save("data/test_data/structure_coords/acid_plant/bottom/roboCoords/{}.npy".format(str(int(time.time()))), np.array(self.roboCoords))
            np.save("data/test_data/structure_coords/acid_plant/bottom/forgeCoords/{}.npy".format(str(int(time.time()))), np.array(self.forgeCoords))
            np.save("data/test_data/structure_coords/acid_plant/bottom/twilightCoords/{}.npy".format(str(int(time.time()))), np.array(self.twilightCoords))

    async def on_step(self, iteration):
        self.iteration = iteration
        self.game_time = self.iteration / self.ITERATIONS_PER_MINUTE
        if iteration == 0:
            self.gameStart()

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
        await self.starting_pos()
        await self.scout()
        await self.defense_base()
        #await self.chat()
        #await self.scout()
        await self.do_actions(self.actions)
        # empty list to be ready for new actions in the next frame
        self.actions = []

    def gameStart(self):
        if self.enemy_race == Race.Zerg:
            self.opponentRace = 2
        elif self.enemy_race == Race.Protoss:
            self.opponentRace = 3
        elif self.opponentRace == Race.Terran:
            self.opponentRace = 4
        else:
            self.opponentRace = 5

    def random_location_variance(self, location):
        x = location[0]
        y = location[1]

        x += random.randrange(-15,15)
        y += random.randrange(-15,15)

        if x < 0:
            print("x below")
            x = 0
        if y < 0:
            print("y below")
            y = 0
        if x > self.game_info.map_size[0]:
            print("x above")
            x = self.game_info.map_size[0]
        if y > self.game_info.map_size[1]:
            print("y above")
            y = self.game_info.map_size[1]

        go_to = position.Point2(position.Pointlike((x,y)))

        return go_to


    async def chat(self):
        if self.game_time <= .09:
            await self._client.chat_send('im lewis 1!', team_only=False)

    async def starting_pos(self):
        if self.start_location == (26.5, 137.5):
            self.top_spawn = True

    async def structure_positions(self):

            for pylon in self.units(PYLON):
                if pylon.position not in self.pylonCoords:
                    self.pylonCoords.append(pylon.position)

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
                        self.actions.append(nexus.train(PROBE))
                        #await self.do(nexus.train(PROBE))
        #print (self.known_enemy_units)

    async def scout(self):
        self.expand_dis_dir = {}
        for el in self.expansion_locations:
            distance_to_enemy_start = el.distance_to(self.enemy_start_locations[0])
            self.expand_dis_dir[distance_to_enemy_start] = el

        self.ordered_exp_distances = sorted(k for k in self.expand_dis_dir)

        existing_ids = [unit.tag for unit in self.units]
        to_be_removed = []
        for noted_scout in self.scouts_and_spots:
            if noted_scout not in existing_ids:
                to_be_removed.append(noted_scout)

        for scout in to_be_removed:
            del self.scouts_and_spots[scout]

        if len(self.units(ROBOTICSFACILITY).ready) == 0:
            unit_type = PROBE
            unit_limit = 1
        else:
            unit_type = OBSERVER
            unit_limit = 3

        assign_scout = True

        if unit_type == PROBE:
            for unit in self.units(PROBE):
                if unit.tag in self.scouts_and_spots:
                    assign_scout = False

        if assign_scout:
            if len(self.units(unit_type).idle) > 0:
                for obs in self.units(unit_type).idle[:unit_limit]:
                    if obs.tag not in self.scouts_and_spots:
                        for dist in self.ordered_exp_distances:
                            try:
                                location = self.expand_dis_dir[dist] #next(value for key, value in self.expand_dis_dir.items() if key == dist)
                                active_locations = [self.scouts_and_spots[k] for k in self.scouts_and_spots]

                                if location not in active_locations:
                                    if unit_type == PROBE:
                                        for unit in self.units(PROBE):
                                            if unit.tag in self.scouts_and_spots:
                                                continue

                                    self.actions.append(obs.move(location))
                                    self.scouts_and_spots[obs.tag] = location
                                    break
                            except Exception as e:
                                pass

        for obs in self.units(unit_type):
            if obs.tag in self.scouts_and_spots:
                if obs in [probe for probe in self.units(PROBE)] and self.game_time <= 2.2:
                    self.actions.append(obs.move(self.random_location_variance(self.scouts_and_spots[obs.tag])))

    async def build_pylons(self):
        if self.supply_left < 7 and not self.already_pending(PYLON):
            nexuses = self.units(NEXUS).random
            #pos = nexuses.position.towards_with_random_angle(self.game_info.map_center, random.randrange(0,10))#to2.random_on_distance(4)
            max_difference = math.pi
            pos = nexuses.position.towards_with_random_angle(nexuses.position, random.randrange(0,15))
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
            if self.units(GATEWAY).amount < 2 and self.can_afford(GATEWAY) and not self.units(WARPGATE).exists:
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
            if self.can_afford(STALKER) and self.units(STALKER).amount <= 4 and self.units(WARPGATE).amount == 0 and self.units(CYBERNETICSCORE).ready:
                await self.do(gateway.train(STALKER))

    def find_target(self, state):
        if len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]

    async def rush_defense(self):
        if self.units(STALKER).amount > 0:
            if len(self.known_enemy_units) >= 1:
                for s in self.units(STALKER).idle:
                    self.actions.append(s.attack(random.choice(self.known_enemy_units)))
                    #await self.do(s.attack(random.choice(self.known_enemy_units)))
        if self.units(ZEALOT).amount > 0:
            if len(self.known_enemy_units) >= 1:
                for s in self.units(ZEALOT).idle:
                    self.actions.append(s.attack(random.choice(self.known_enemy_units)))
                    #await self.do(s.attack(random.choice(self.known_enemy_units)))
        if self.units(IMMORTAL).amount > 0:
            if len(self.known_enemy_units) >= 1:
                for s in self.units(IMMORTAL).idle:
                    self.actions.append(s.attack(random.choice(self.known_enemy_units)))
                    #await self.do(s.attack(random.choice(self.known_enemy_units)))

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
        self.be_defensive = False
        army = (self.units(ZEALOT) | self.units(IMMORTAL) | self.units(STALKER)).idle
        if army.amount >= 50:
            for unit in army:
                if not self.known_enemy_units:  
                    self.actions.append(unit.attack(self.enemy_start_locations[0]))
                else:
                    nexuses = self.units(NEXUS).ready.random
                    closest_enemy = self.known_enemy_units.closest_to(unit)
                    self.actions.append(unit.attack(closest_enemy))

    async def control_fighting_army(self):
        if not self.known_enemy_units and self.be_defensive == False:
            return
        army = self.units(ZEALOT) | self.units(STALKER) | self.units(IMMORTAL)
        enemy_fighters = self.known_enemy_units.filter(
            lambda u: u.can_attack or u.type_id in {BUNKER, SPINECRAWLERUPROOTED, SPINECRAWLER, PHOTONCANNON}
        )
        for unit in army:
            if enemy_fighters and self.be_defensive == False:
                in_range_enemies = enemy_fighters.in_attack_range_of(unit)
                if in_range_enemies:
                    lowest_hp = min(in_range_enemies, key=lambda e: e.health + e.shield)
                    self.actions.append(unit.attack(lowest_hp))
                else:
                    self.actions.append(unit.move(enemy_fighters.closest_to(unit)))
            else:
                self.actions.append(unit.attack(self.known_enemy_units.closest_to(unit)))

    async def defense_base(self):
        if self.be_defensive == True:
            #gather capable units for defensing beautiful pylons
            #consider adding units to tag with defender
            army = self.units(ZEALOT) | self.units(STALKER) | self.units(IMMORTAL)
            enemyUnits = self.known_enemy_units
            nexuses = self.units(NEXUS).exists
            max_difference = math.pi
            dangerRadius = nexuses.position.towards_with_random_angle(nexuses.position, random.randrange(0,15))
            #tell units to attack enemies in range of defensible pylons
            for unit in army:
                if enemyUnits(near=dangerRadius):
                    in_range_enemies = enemy_fighters.in_attack_range_of(unit)
                    if in_range_enemies:
                        lowest_hp = min(in_range_enemies, key=lambda e: e.health + e.shield)
                        self.actions.append(unit.attack(lowest_hp))
                    else:
                        self.actions.append(unit.move(enemy_fighters.closest_to(unit)))
                else:
                    self.actions.append(unit.move(dangerRadius))

run_game(maps.get("(2)AcidPlantLE"), [
    Bot(Race.Protoss, lewis()),
    Computer(Race.Zerg, Difficulty.VeryHard)
    #Bot(Race.Protoss, lewis2())
    ], realtime=False)