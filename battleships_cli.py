from math import floor
from os import get_terminal_size,path, makedirs,sep
from sys import exit as sys_exit,maxsize
from cli import print_lines, Menu
from game.components import BattleGrid,ShipType
from game.util import is_int
from random import randint
import configparser
import logging

#=== LOGGING CONSTANTS
LOGGING_FOLDER = ".log"
LOGGING_FILE = "battleships_cli.log"
LOGGING_LVL  = logging.WARNING
#===

#=== CONFIG CONSTANTS
CONFIG_FILE = "config.ini"
CONFIG_SECTION_DUMP = "DUMP"
CONFIG_SECTION_DUMP_OUTPUT_DIR = "OUTPUT_DIR"
CONFIG_SECTION_ASCII_TABLE_MAP = "ASCII_TABLE_MAP"
CONFIG_SECTION_ASCII_TABLE_MAP_EMPTY = "EMPTY"
CONFIG_SECTION_ASCII_TABLE_MAP_OCCUPIED = "OCCUPIED"
CONFIG_SECTION_ASCII_TABLE_SHIPS = "ASCII_TABLE_SHIPS"
CONFIG_SECTION_ASCII_TABLE_NA = "%"
CONFIG_SECTION_ASCII_TABLE_MAP_HIT = "HIT"
CONFIG_SECTION_ASCII_TABLE_MAP_MISS = "MISS"
#===
#=== MENU CONSTANTS
GAME_HEADER =  ["##########################################","##             BATTLESHIPS              ##","##########################################"]
MENU_TITLE = Menu("# ")
MENU_TITLE.header = GAME_HEADER + ["##============= MAIN MENU ==============##"]
MENU_TITLE.footer = ["##======================================##"]
MENU_NEW = Menu("# ")
MENU_NEW.header =GAME_HEADER + ["##============== NEW GAME ==============##"]
MENU_NEW.footer = ["##======================================##"]
MENU_GAME = Menu("# ")
MENU_GAME.header =GAME_HEADER + ["##============= PLAY GAME ==============##"]
MENU_GAME.footer = ["##======================================##"]
MENU_GAME_RESERVE_OPTION_LINES = 4
for data in ShipType:
    MENU_GAME_RESERVE_OPTION_LINES += 1
MENU_WIN = Menu("# ")
MENU_WIN.header =GAME_HEADER + ["##============== YOU WIN! ==============##"]
MENU_WIN.footer = ["##======================================##"]
#===

def new_game_set_width(grid : BattleGrid):
    min_size = grid.calculate_min_bounds()
    max_size = get_terminal_size().columns
    while True:
        MENU_NEW.options.clear()
        MENU_NEW.create_option("BACK",lambda : new_game(grid))
        MENU_NEW.footer.insert(0,"# [{}-{}] CHANGE WIDTH (width={})".format(min_size,max_size,grid.width))
        print_lines(MENU_NEW.to_lines())    
        MENU_NEW.footer.pop(0)    
        value = input('Choose action [0:{}-{}]: '.format(min_size,max_size,grid.width)).strip()
        if not is_int(value): continue
        value=int(value)
        handler = MENU_NEW.select_option(value)
        if handler != None:
            handler()
            break
        elif value >= min_size and value < max_size:
            MENU_NEW.footer.pop(0)
            grid.set_width(value)
            new_game(grid)
            break

def new_game_set_height(grid : BattleGrid):
    min_size = grid.calculate_min_bounds()
    max_size = get_terminal_size().lines - len(MENU_GAME.header) - len(MENU_GAME.footer) - MENU_GAME_RESERVE_OPTION_LINES # terminal lines - used for prints and options
    while True:
        MENU_NEW.options.clear()
        MENU_NEW.create_option("BACK",lambda : new_game(grid))
        MENU_NEW.footer.insert(0,"# [{}-{}] CHANGE HEIGHT (height={})".format(min_size,max_size,grid.height))
        print_lines(MENU_NEW.to_lines())        
        MENU_NEW.footer.pop(0)
        value = input('Choose action [0:{}-{}]: '.format(min_size,max_size,grid.width)).strip()
        if not is_int(value): continue
        value=int(value)
        handler = MENU_NEW.select_option(value)
        if handler != None:
            handler()
            break
        elif value >= min_size and value < max_size:            
            grid.set_height(value)
            new_game(grid)
            break 
def new_game_set_seed(grid : BattleGrid):
   
    while True:
        MENU_NEW.options.clear()
        MENU_NEW.footer.insert(0,"# [<0] BACK")
        MENU_NEW.footer.insert(0,"# [{}-{}] CHANGE SEED (seed={})".format(0,maxsize,grid.seed))
        print_lines(MENU_NEW.to_lines())        
        MENU_NEW.footer.pop(0)
        MENU_NEW.footer.pop(0)
        value = input('Choose action [<0-{}]: '.format(maxsize)).strip()
        if not is_int(value): continue
        value=int(value)
        if value >=0 : grid.seed = value
        new_game(grid)
        break

def new_game_boats(grid:BattleGrid):
    while True:
        MENU_NEW.options.clear()
        for data in ShipType:
            count_for_type = sum( (lambda ship_type : ship_type == data)(x) for x in grid.ships)  
            MENU_NEW.create_option(
                'CHANGE NUMBER OF {:15} x{}'.format(data.name, count_for_type),
                lambda data=data: new_game_boats_set_number(grid,data) # "data=data" for closure
            )
        MENU_NEW.create_option("BACK",lambda: new_game(grid))
        print_lines(MENU_NEW.to_lines())
        value = input('Choose action [0-{}]: '.format(len(MENU_NEW.options)-1)).strip()
        if not is_int(value): continue
        handler = MENU_NEW.select_option(int(value))
        if handler != None:
            handler()
            break

def new_game_boats_set_number(grid : BattleGrid,ship_type:ShipType):
   
    count_for_type = sum( (lambda _ship_type : _ship_type == ship_type)(x) for x in grid.ships)
    while True:
        MENU_NEW.options.clear()
        MENU_NEW.footer.insert(0,"# [<0] BACK")
        MENU_NEW.footer.insert(0,"# [0-{}] CHANGE NUMBER OF {} (x{})".format(maxsize,ship_type.name,count_for_type))
        print_lines(MENU_NEW.to_lines())        
        MENU_NEW.footer.pop(0)
        MENU_NEW.footer.pop(0)
        value = input('Choose action [<0-{}]: '.format(maxsize)).strip()
        if not is_int(value): continue
        value=int(value)
        if value >=0 : grid.set_number_ships_for_type(ship_type,value)
        new_game_boats(grid)
        break

def game_set_target(grid:BattleGrid):
    while True:
        x = input("Set x: ")
        if not is_int(x): continue
        y = input("Set y: ")
        if not is_int(y): continue
        x = int(x)
        y = int(y)
        index = y * grid.width + x
        if index >=0 and index < grid.width * grid.height:
            grid.selected_cell = index
            break

def print_grid(config:configparser.ConfigParser,grid:BattleGrid):
    for y in range(grid.height):
        line = ""
        for x in range(grid.width):
            cell_index = x + grid.width * y
            is_occupied = False
            for ship in grid.placed_ships: 
                if cell_index in ship.hits:
                    if ship.is_destroyed():
                        line += config[CONFIG_SECTION_ASCII_TABLE_SHIPS].get(ship.ship_type.name, CONFIG_SECTION_ASCII_TABLE_NA)
                    else:
                        line += config[CONFIG_SECTION_ASCII_TABLE_MAP].get(CONFIG_SECTION_ASCII_TABLE_MAP_HIT, CONFIG_SECTION_ASCII_TABLE_NA)
                    is_occupied = True
                    break
            if not is_occupied and cell_index in grid.missed_shots:
                line += config[CONFIG_SECTION_ASCII_TABLE_MAP].get(CONFIG_SECTION_ASCII_TABLE_MAP_MISS, CONFIG_SECTION_ASCII_TABLE_NA)
                is_occupied = True
            if not is_occupied:
                line += config[CONFIG_SECTION_ASCII_TABLE_MAP][CONFIG_SECTION_ASCII_TABLE_MAP_EMPTY]
        print(line)


def you_win(config:configparser.ConfigParser,grid:BattleGrid):
    MENU_WIN.options.clear()
    MENU_WIN.create_option(
        "NEW GAME",
        lambda: new_game(BattleGrid(0,0,[ShipType.SUBMARINE]*4+[ShipType.TORPEDO]*3+[ShipType.ESCORTE]*2+[ShipType.CRUISER],randint(0,maxsize)))
    )
    MENU_WIN.create_option("MAIN MENU", main_menu)
    MENU_WIN.create_option("QUIT",sys_exit)
    while True:
        print_lines(MENU_WIN.to_lines())
        print("Width : {}".format(grid.width))
        print("Height : {}".format(grid.height))
        print("Seed : {}".format(grid.seed))
        print("Ships :")
        ship_cell_count = 0
        for data in ShipType:
            count_placed_of_type = sum( (lambda s : s.ship_type == data)(s) for s in grid.placed_ships)
            print('    {:15} x{}'.format(data.name, count_placed_of_type))
            ship_cell_count += count_placed_of_type * data.value
        print("Shots : {}".format(len(grid.missed_shots) + ship_cell_count))
        print("Misses : {}".format(len(grid.missed_shots)))
        print_grid(config,grid)
        value = input('Choose action [0-{}]: '.format(len(MENU_WIN.options)-1)).strip()
        if not is_int(value): continue
        handler = MENU_WIN.select_option(int(value))
        if handler != None:
            handler()
            break

    

def game_start(grid:BattleGrid):
    #== Load config
    config = configparser.ConfigParser()
    logging.debug("Opening config file : {}".format(CONFIG_FILE))
    config.read(CONFIG_FILE)
    if(len(config.sections())>0):
        logging.debug("Opening config file : {} successful".format(CONFIG_FILE))
    else:
        logging.debug("Opening config file : {} failed".format(CONFIG_FILE))
        return
    #==
    grid.generate()
    while True:
        MENU_GAME.options.clear()
        
        MENU_GAME.create_option(
            "QUIT CURRENT GAME",
            lambda: new_game(BattleGrid(0,0,[ShipType.SUBMARINE]*4+[ShipType.TORPEDO]*3+[ShipType.ESCORTE]*2+[ShipType.CRUISER],randint(0,maxsize)))
        )
        MENU_GAME.create_option(
            "SET TARGET CELL [current=({},{})]".format(grid.selected_cell%grid.width,floor(grid.selected_cell/grid.width)),
            lambda : game_set_target(grid)
        )
        already_hit = False
        for ship in grid.placed_ships:
            if grid.selected_cell in ship.hits:
                already_hit = True
                break
        if not already_hit and grid.selected_cell not in grid.missed_shots:
            MENU_GAME.create_option("SHOOT TARGET",lambda:grid.hit_cell(grid.selected_cell))            
        
        print_lines(MENU_GAME.to_lines())

        print_grid(config,grid)

        print("Remaining ships:")
        total_ship_remaining = 0
        for data in ShipType:
            count_placed_of_type = sum( (lambda s : s.ship_type == data and not s.is_destroyed())(s) for s in grid.placed_ships)
            print('    {:15} x{}'.format(data.name, count_placed_of_type))
            total_ship_remaining += count_placed_of_type
        if total_ship_remaining < 1:
            you_win(config,grid)
            break
        value = input('Choose action [0-{}]: '.format(len(MENU_GAME.options)-1)).strip()
        if not is_int(value): continue
        handler = MENU_GAME.select_option(int(value))
        if handler != None:
            handler()
    main_menu()

def new_game(grid:BattleGrid=BattleGrid(0,0,[ShipType.SUBMARINE]*4+[ShipType.TORPEDO]*3+[ShipType.ESCORTE]*2+[ShipType.CRUISER],randint(0,maxsize))):
    grid.force_bounds()
    while True:
        MENU_NEW.options.clear()
        MENU_NEW.create_option("CHANGE WIDTH (width={})".format(grid.width), lambda : new_game_set_width(grid))
        MENU_NEW.create_option("CHANGE HEIGHT (height={})".format(grid.height), lambda : new_game_set_height(grid))
        MENU_NEW.create_option("CHANGE SEED (seed={})".format(grid.seed), lambda: new_game_set_seed(grid))
        ship_opt = MENU_NEW.create_option("CHANGE BOATS :",lambda:new_game_boats(grid) )
        MENU_NEW.create_option("START GAME", lambda: game_start(grid))
        MENU_NEW.create_option("BACK",main_menu)

        for data in ShipType:
            count_for_type = sum( (lambda ship_type : ship_type == data)(x) for x in grid.ships)
            ship_opt.add_prompt_line('    {:15} x{}'.format(data.name, count_for_type))

        print_lines(MENU_NEW.to_lines())
        value = input('Choose action [0-{}]: '.format(len(MENU_NEW.options)-1)).strip()
        if not is_int(value): continue
        handler = MENU_NEW.select_option(int(value))
        if handler != None:
            handler()
            break        

def main_menu():
    MENU_TITLE.options.clear()
    MENU_TITLE.create_option("NEW GAME",new_game)
    MENU_TITLE.create_option("QUIT",sys_exit)
    while True:
        print_lines(MENU_TITLE.to_lines())
        value = input('Choose action [0-{}]: '.format(len(MENU_TITLE.options)-1)).strip()
        if not is_int(value): continue
        handler = MENU_TITLE.select_option(int(value))
        if handler != None:
            handler()
            break


if __name__ == '__main__':
    if not path.exists(LOGGING_FOLDER):makedirs(LOGGING_FOLDER)
    logging.basicConfig(filename="{}{}{}".format(LOGGING_FOLDER,sep,LOGGING_FILE), encoding='utf-8', level=LOGGING_LVL)
    main_menu()
    