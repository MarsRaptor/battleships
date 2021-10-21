import configparser
from os import sep, path, makedirs
from game import BattleGrid,ShipType
from cli import print_lines
from game.util import is_int
from random import randint
from sys import maxsize,exit as sys_exit
from PIL import Image,ImageColor
import logging

#=== LOGGING CONSTANTS
LOGGING_FOLDER = ".log"
LOGGING_FILE = "battleships_dump.log"
LOGGING_LVL  = logging.DEBUG
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
CONFIG_SECTION_COLOR_TABLE_MAP = "COLOR_TABLE_MAP"
CONFIG_SECTION_COLOR_TABLE_MAP_EMPTY = "EMPTY"
CONFIG_SECTION_COLOR_TABLE_MAP_OCCUPIED = "OCCUPIED"
CONFIG_SECTION_COLOR_TABLE_SHIPS = "COLOR_TABLE_SHIPS"
CONFIG_SECTION_COLOR_TABLE_NA = 0
#===

def grid_to_ascii_dump(config:configparser.ConfigParser,grid:BattleGrid):
    """
    Create lines of characters representing the generated grid
    """

    lines : list[str] = []
    lines.append("================================\n")
    lines.append("=       BATTLESHIPS DUMP       =\n")
    lines.append("================================\n")
    lines.append("width : {}\n".format(grid.width))
    lines.append("height : {}\n".format(grid.height))
    lines.append("seed : {}\n".format(grid.seed))
    lines.append("--------------------------------\n")
    lines.append("\"_\" = EMPTY CELL\n")
    lines.append("\"#\" = SHIP PADDING\n")
    for data in ShipType:
        lines.append("\"{}\" : {}\n".format(config[CONFIG_SECTION_ASCII_TABLE_SHIPS].get(data.name, CONFIG_SECTION_ASCII_TABLE_NA),data.name))
    lines.append("================================\n")
    lines.append("\n")
    for y in range(grid.height):
        line = ""
        for x in range(grid.width):
            cell_index = x + grid.width * y
            is_occupied = False
            for ship in grid.placed_ships:                    
                if cell_index in ship.placement_cells:
                    line += config[CONFIG_SECTION_ASCII_TABLE_SHIPS].get(ship.ship_type.name, CONFIG_SECTION_ASCII_TABLE_NA)
                    is_occupied = True
                    break
                elif cell_index in ship.occupied_cells:
                    line += config[CONFIG_SECTION_ASCII_TABLE_MAP][CONFIG_SECTION_ASCII_TABLE_MAP_OCCUPIED]
                    is_occupied = True
                    break
            if not is_occupied:
                line += config[CONFIG_SECTION_ASCII_TABLE_MAP][CONFIG_SECTION_ASCII_TABLE_MAP_EMPTY]
        lines.append(line + "\n")

    return lines

def generate_image(config:configparser.ConfigParser,grid:BattleGrid):
    """
    Create image representing the generated grid
    """

    img = Image.new( 'RGB', (grid.width,grid.height), 0) # create a new black image
    pixels = img.load()
    for y in range(grid.height):
        for x in range(grid.width):
            cell_index = x + grid.width * y
            is_occupied = False
            for ship in grid.placed_ships:                    
                if cell_index in ship.placement_cells:
                    pixels[x,y] = ImageColor.getrgb(config[CONFIG_SECTION_COLOR_TABLE_SHIPS].get(ship.ship_type.name, CONFIG_SECTION_COLOR_TABLE_NA))
                    is_occupied = True
                    break
                elif cell_index in ship.occupied_cells:
                    pixels[x,y] = ImageColor.getrgb(config[CONFIG_SECTION_COLOR_TABLE_MAP][CONFIG_SECTION_COLOR_TABLE_MAP_OCCUPIED])
                    is_occupied = True
                    break
            if not is_occupied:
                pixels[x,y] = ImageColor.getrgb(config[CONFIG_SECTION_COLOR_TABLE_MAP][CONFIG_SECTION_COLOR_TABLE_MAP_EMPTY])
    return img


def dump_ascii_to_file(filename:str,lines: list[str]):
    """Save created ascii representation of the generated grid to file"""
    
    f = open(filename, "w")               
    f.writelines(lines)
    f.close()

def main():

    #== Load config
    config = configparser.ConfigParser()
    logging.debug("Opening config file : {}".format(CONFIG_FILE))
    config.read(CONFIG_FILE)
    if(len(config.sections())>0):
        logging.debug("Opening config file : {} successful".format(CONFIG_FILE))
    else:
        logging.error("Opening config file : {} failed".format(CONFIG_FILE))
        return
    #==

    #== Initialise grid with defaults
    grid = BattleGrid(0,0,[ShipType.SUBMARINE]*4+[ShipType.TORPEDO]*3+[ShipType.ESCORTE]*2+[ShipType.CRUISER],randint(0,maxsize))
    min_size = grid.calculate_min_bounds()
    grid.force_bounds()
    #==

    info_lines = [
        "Welcome to battleships!",
        "In this mode the ships amounts are not configurable therefor only grids > {}x{} are valid.".format(min_size,min_size)
    ]

    #== Set grid width
    while True:
        print_lines(info_lines)
        value = input("Please input a grid width (leave empty for {}): ".format(min_size)).strip()
        if value == "":
            info_lines.append("Grid width : {}".format(grid.width))
            break
        if not is_int(value): continue
        w=int(value)
        if w < min_size : continue
        grid.set_width(w)
        info_lines.append("Grid width : {}".format(w))
        break
    #==
    #== Set grid height
    while True:
        print_lines(info_lines)
        value = input("Please input a grid height (leave empty for {}): ".format(min_size)).strip()
        if value == "":
            info_lines.append("Grid height : {}".format(grid.height))
            break
        if not is_int(value): continue
        h=int(value)
        if h <min_size : continue
        grid.set_height(h)
        info_lines.append("Grid height : {}".format(h))
        break
    #==
    #== Set grid seed
    while True:
        print_lines(info_lines)
        value = input("Please input a positive integer as seed (leave empty for random): ").strip()
        if value == "":
            info_lines.append("Grid seed : {}".format(grid.seed))
            break
        if not is_int(value): continue
        s=int(value)
        if h <0 : continue
        grid.seed = s
        info_lines.append("Grid seed : {}".format(s))
        break
    #==
    #== Generate grid
    info_lines.append("Generating grid...")
    print_lines(info_lines)
    grid.generate()
    info_lines[-1] += "DONE"
    print_lines(info_lines)
    #==
    #== Create dumped files contents
    dump_lines = grid_to_ascii_dump(config,grid)
    image = generate_image(config,grid)
    #==
    #== Create dumped files and containing folder
    dump_dir = "{}{}battlegrid_{}x{}_{}{}".format(config[CONFIG_SECTION_DUMP][CONFIG_SECTION_DUMP_OUTPUT_DIR],sep,grid.width,grid.height,grid.seed,sep)
    ascii_filename = "{}dump.txt".format(dump_dir)
    image_filename = "{}dump.png".format(dump_dir)
    input("Press any key to exit and dump to files :\n\t- {}\n\t- {}".format(ascii_filename,image_filename))
    if not path.exists(dump_dir):makedirs(dump_dir)
    dump_ascii_to_file(ascii_filename,dump_lines)
    image.save(image_filename)
    #==
    sys_exit()

if __name__ == "__main__":
    if not path.exists(LOGGING_FOLDER):makedirs(LOGGING_FOLDER)
    logging.basicConfig(filename="{}{}{}".format(LOGGING_FOLDER,sep,LOGGING_FILE), encoding='utf-8', level=LOGGING_LVL)
    main()