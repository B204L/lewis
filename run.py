import sc2, sys, os, pathlib, RoachRush
from __init__ import run_ladder_game
from sc2 import Race, Difficulty
from sc2.player import Bot, Computer
# Load bot
from Lewis import lewis
bot = Bot(Race.Protoss, lewis())

# Start game
if __name__ == '__main__':
    if "--LadderServer" in sys.argv:
        # Ladder game started by LadderManager
        print("Starting ladder game...")
        result, opponentid = run_ladder_game(bot)
        print(result," against opponent ", opponentid)
    else:
        # Local game
        print("Starting local game...")
        sc2.run_game(sc2.maps.get("(2)AcidPlantLE"), [
            bot, bot2
], realtime=False)