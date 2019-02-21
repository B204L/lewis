import sc2
from sc2 import Race
from sc2.player import Bot

from main import lewis
from main2 import lewis2

def main():
    sc2.run_game(sc2.maps.get("(2)AcidPlantLE"), [
        Bot(Race.Protoss, lewis()),
        Bot(Race.Protoss, lewis2())
    ], realtime=False)

if __name__ == '__main__':
	main()