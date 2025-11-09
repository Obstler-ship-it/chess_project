import logging
from game_controller import GameController

def main():
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    controller = GameController()
    controller.run()

if __name__ == "__main__":
    main()