from random import seed as randseed, randint,choice as randchoice
from .ships import ShipType, Ship,ship_type_compare,SHIP_CELL_PADDING,SHIP_WIDTH
from math import ceil,floor
import logging

# ======================
# grid mapping:
#   x = cols
#   y = rows
# ======================


class BattleGrid:
    """Representation of a grid, upon which ships are placed."""

    def __init__(self,grid_width:int,grid_height:int,ships:list[ShipType],seed:int) -> None:
        self.width = grid_width
        """Width of the grid, resized automatically if need be. Do not set directly, use set_width instead."""
        self.height = grid_height
        """Height of the grid, resized automatically if need be. Do not set directly, use set_height instead."""
        self.seed = seed
        """Random seed of the grid, used to generate ship placements procedurally."""
        self.ships = ships
        self.placed_ships: list[Ship] = []
        self.missed_shots: set[Ship] = set()
        self.selected_cell:int = 0

        self.__is_bounds_forced__ = False
        self.__is_ships_sorted__ = False
        self.__is_generated__ = False
    
    def set_width(self,w:int):
        self.width = w
        self.__is_bounds_forced__ = False
    def set_height(self,h:int):
        self.height = h
        self.__is_bounds_forced__ = False

    def get_number_ships_for_type(self,ship_type:ShipType):
        return sum( (lambda t : t == ship_type)(t) for t in self.ships)

    def set_number_ships_for_type(self,ship_type:ShipType,amount:int):
        if amount >= 0: 
            number_diff = amount - self.get_number_ships_for_type(ship_type)
            if number_diff > 0:
                for _ in range(number_diff): self.ships.append(ship_type)
                self.__is_ships_sorted__ = False
                self.__is_bounds_forced__ = False
            elif number_diff < 0:
                for _ in range(-1 * number_diff): self.ships.remove(ship_type)
                self.__is_ships_sorted__ = False
                self.__is_bounds_forced__ = False

    def sort_ships(self) -> None:
        self.ships.sort(key=ship_type_compare,reverse=True)
        self.__is_ships_sorted__ = True
    
    def calculate_min_bounds(self) -> int:
        if len(self.ships)>0:
            min_size :int = max(ceil((len(self.ships) * SHIP_WIDTH + len(self.ships) * SHIP_CELL_PADDING - 1)/2), self.ships[0].value)
            return min_size
        else:
            return 0

    def force_bounds(self) -> None:

        if not self.__is_ships_sorted__ : self.sort_ships()

        logging.debug("Checking grid bounds...")
        min_size :int = self.calculate_min_bounds()
        if self.width < min_size:
            logging.debug("Resizing grid width from {} to minimum bounds ({}) for ship count {}.".format(self.width, min_size,len(self.ships)))
            self.width = min_size
        if self.height < min_size:
            logging.debug("Resizing grid height from {} to minimum bounds ({}) for ship count {}.".format(self.height,min_size,len(self.ships)))
            self.height = min_size
        self.__is_bounds_forced__ = True
        
    def adjust_ship_to_bounds(self,ship:Ship)  -> None:
        if not self.__is_bounds_forced__ : self.force_bounds()
        logging.debug("Checking ship is in bounds...")
        if ship.anchor < 0 : ship.anchor = ship.anchor % self.width
        while(ship.anchor > self.width * self.height):
            ship.anchor -= self.width
            
        if ship.is_horizontal == True:
            anchor_x = ship.anchor % self.width
            overlap = anchor_x + ship.ship_type.value - self.width
            if overlap > 0:
                logging.debug("Ship with anchor {anchor} out of horizontal bounds.".format(anchor=ship.anchor))
                ship.anchor -= overlap
                logging.debug("Ship anchor moved to cell {anchor}".format(anchor=ship.anchor))
        else:
            anchor_y = floor(ship.anchor / self.width)
            overlap = anchor_y + ship.ship_type.value - self.height
            if overlap > 0:
                logging.debug("Ship with anchor {anchor} out of vertical bounds.".format(anchor=ship.anchor))
                ship.anchor -= overlap * self.width
                logging.debug("Ship anchor moved to cell {anchor}".format(anchor=ship.anchor))                
    
    def place_ship(self,ship:Ship,occupied_cells:list[int]):
        if not self.__is_bounds_forced__ : self.force_bounds()

        self.adjust_ship_to_bounds(ship)

        ship.placement_cells = []
        ship.occupied_cells = []

        anchor_x = ship.anchor % self.width
        anchor_y = floor(ship.anchor / self.width)

        scan_end_x = (anchor_x + ship.ship_type.value + SHIP_CELL_PADDING ) if (ship.is_horizontal) else (anchor_x + SHIP_WIDTH + 1)
        scan_end_y = (anchor_y + SHIP_WIDTH + 1) if (ship.is_horizontal) else (anchor_y + ship.ship_type.value + SHIP_CELL_PADDING )

        for x in range(anchor_x,scan_end_x):
            for y in range(anchor_y,scan_end_y):
                if x >=0 and x < self.width and y >= 0 and y < self.height:                   
                    ship.occupied_cells.append(x + self.width * y)
                    if x >= anchor_x and x < scan_end_x - 1 and y >= anchor_y and y < scan_end_y - 1:    
                        ship.placement_cells.append(x + self.width * y)       
                        
        cell_collision = [cell_index for cell_index in ship.occupied_cells if cell_index in occupied_cells]
        if len(cell_collision) < 1:
            occupied_cells.extend(ship.occupied_cells)
            self.placed_ships.append(ship)
            return True
        else:
            return False
        
                
    def generate(self):
        self.__is_generated__ = False
        logging.debug("Generating ship placements on grid:")
        if not self.__is_ships_sorted__ : self.sort_ships()
        if not self.__is_bounds_forced__ : self.force_bounds()
        logging.debug("Setting seed to {seed}...".format(seed=self.seed))
        randseed(self.seed)

        grid_size = self.width*self.height
        occupied_cells = []
        while(len(self.ships)>0):
            placed = False

            ship = Ship(randint(0,grid_size-1), randchoice([True,False]), self.ships.pop(0))

            while(not placed):            
                
                placed = self.place_ship(ship,occupied_cells)     
                if not placed:
                    ship.anchor = randint(0,grid_size-1)
                    ship.is_horizontal = randchoice([True,False])

        self.__is_generated__ = True         

    def get_ship_for_cell(self,cell_index:int):
        if not self.__is_generated__:
            return None
        for ship in self.placed_ships:
            if cell_index in ship.placement_cells:
                return ship
        return None
    
    def get_ship_for_pos(self,x:int,y:int):
        return self.get_ship_for_cell(x + self.width * y)
    
    def hit_cell(self,cell_index:int):
        is_hit = False
        ship = self.get_ship_for_cell(cell_index)
        if ship != None:
            ship.hits.append(cell_index)
            is_hit=True
        else:
            self.missed_shots.add(cell_index)
        return is_hit

    def hit_pos(self,x:int,y:int):
        return self.hit_cell(x + self.width * y)
                    

    



