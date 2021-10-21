import enum

SHIP_CELL_PADDING = 1
SHIP_WIDTH = 1

class ShipType(enum.Enum):
    CRUISER = 4
    ESCORTE = 3
    TORPEDO = 2
    SUBMARINE = 1

def ship_type_compare(ship_type:ShipType)->int:
    return ship_type.value

class Ship:
    """Representation of a ship placed on a grid."""
    def __init__(self,anchor:int,is_horizontal:bool,ship_type:ShipType) -> None:
        self.anchor=anchor 
        """Top left cell index of the ship on the grid"""
        self.is_horizontal=is_horizontal
        self.ship_type=ship_type

        self.placement_cells: list[int] = []
        """Actual cell indices of the ship on the grid"""
        self.occupied_cells: list[int] = []
        """Occupied cell indices of the ship on the grid, including padding"""
        self.hits: list[int] = []
        """Ship cells that have been hit"""
    
    def is_destroyed(self):
        if len(self.placement_cells) < 1:
            return False
        return len(self.hits) == len(self.placement_cells)

    def __str__(self):
        """String representation of the ship"""
        return "<{} {} placements={} padding={}>".format(
            self.ship_type.name,"HORIZONTAL" if self.is_horizontal else "VERTICAL",
            str(self.placement_cells),str([cell_index for cell_index in self.occupied_cells if cell_index not in self.placement_cells])
            )
    def __repr__(self):
        return self.__str__()

