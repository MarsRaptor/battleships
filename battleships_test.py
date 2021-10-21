import unittest
from game import BattleGrid,ShipType,Ship,SHIP_CELL_PADDING,SHIP_WIDTH
from math import ceil

class TestShipMethods(unittest.TestCase):
    def test_1_is_destroyed(self):
        ship = Ship(0,True,ShipType.CRUISER)
        self.assertFalse(ship.is_destroyed())
        ship.placement_cells.extend([0,1,2,3])
        ship.occupied_cells.extend([0,1,2,3,4,5,6,7,8,9])
        self.assertFalse(ship.is_destroyed())
        ship.hits.append(0)
        self.assertFalse(ship.is_destroyed())
        ship.hits.extend([1,2,3])
        self.assertTrue(ship.is_destroyed())

class TestBattleGridMethods(unittest.TestCase):

    def test_1_set_width(self):
        W = 100
        g = BattleGrid(0,0,[],0)
        g.set_width(W)
        self.assertEqual(g.width, W)
        self.assertFalse(g.__is_bounds_forced__)

    def test_2_set_height(self):
        H = 100
        g = BattleGrid(0,0,[],0)
        g.set_height(H)
        self.assertEqual(g.height, H)
        self.assertFalse(g.__is_bounds_forced__)
    
    def test_3_get_number_ships_for_type(self):
        g = BattleGrid(0,0,[ShipType.CRUISER],0)
        nb_cruisers = g.get_number_ships_for_type(ShipType.CRUISER)
        nb_submarines = g.get_number_ships_for_type(ShipType.SUBMARINE)
        self.assertEqual(nb_cruisers, 1)
        self.assertEqual(nb_submarines, 0)

    def test_4_set_number_ships_for_type(self):
        N = 25
        g = BattleGrid(0,0,[],0)
        nb_cruisers_before = g.get_number_ships_for_type(ShipType.CRUISER)
        g.set_number_ships_for_type(ShipType.CRUISER,N)
        nb_cruisers_after = g.get_number_ships_for_type(ShipType.CRUISER)
        self.assertNotEqual(nb_cruisers_before,nb_cruisers_after)
        self.assertEqual(nb_cruisers_before,0)
        self.assertEqual(nb_cruisers_after,N)

    def test_5_sort_ships(self):
        g = BattleGrid(0,0,[ShipType.SUBMARINE,ShipType.CRUISER],0)
        first_ship_before = g.ships[0]
        sorted_flag_before = g.__is_ships_sorted__
        g.sort_ships()
        first_ship_after = g.ships[0]
        sorted_flag_after = g.__is_ships_sorted__
        self.assertNotEqual(sorted_flag_before,sorted_flag_after)
        self.assertTrue(sorted_flag_after)
        self.assertNotEqual(first_ship_before.name,first_ship_after.name)
        self.assertEqual(first_ship_after.name,ShipType.CRUISER.name)
    
    def test_6_calculate_min_bounds(self):
        g = BattleGrid(0,0,[],0)
        min_bounds_empty = g.calculate_min_bounds()
        g.set_number_ships_for_type(ShipType.CRUISER,1)
        min_bounds_one_cruiser = g.calculate_min_bounds()
        g.set_number_ships_for_type(ShipType.CRUISER,10)
        min_bounds_ten_cruiser = g.calculate_min_bounds()
        
        self.assertEqual(min_bounds_empty,0)
        self.assertEqual(min_bounds_one_cruiser,ShipType.CRUISER.value)
        self.assertEqual(min_bounds_ten_cruiser,ceil((10 * SHIP_WIDTH + 10 * SHIP_CELL_PADDING - 1)/2))
    
    def test_7_force_bounds(self):
        W1 = 25
        H1 = 13
        W2 = 3
        H2 = 3
        g = BattleGrid(0,0,[ShipType.SUBMARINE,ShipType.CRUISER],0)

        g.force_bounds()
        self.assertEqual(g.width, ShipType.CRUISER.value)
        self.assertEqual(g.height, ShipType.CRUISER.value)
        self.assertTrue(g.__is_bounds_forced__)

        g.set_width(W1)
        g.set_height(H1)
        g.force_bounds()
        self.assertEqual(g.width, W1)
        self.assertEqual(g.height, H1)
        self.assertTrue(g.__is_bounds_forced__)

        g.set_width(W2)
        g.set_height(H2)
        g.force_bounds()
        self.assertNotEqual(g.width, W2)
        self.assertNotEqual(g.height, H2)
        self.assertEqual(g.width, ShipType.CRUISER.value)
        self.assertEqual(g.height, ShipType.CRUISER.value)
        self.assertTrue(g.__is_bounds_forced__)

    def test_8_adjust_ship_to_bounds(self):
        g = BattleGrid(0,0,[ShipType.CRUISER],0)
        ship = Ship(0,True,ShipType.CRUISER)

        ship.anchor = 0
        g.adjust_ship_to_bounds(ship)
        self.assertEqual(ship.anchor, 0)
        ship.anchor = 3
        g.adjust_ship_to_bounds(ship)
        self.assertEqual(ship.anchor, 0)
        ship.anchor = 29
        g.adjust_ship_to_bounds(ship)
        self.assertEqual(ship.anchor, 12)

        ship.is_horizontal = False
        ship.anchor = 0
        g.adjust_ship_to_bounds(ship)
        self.assertEqual(ship.anchor, 0)
        ship.anchor = 3
        g.adjust_ship_to_bounds(ship)
        self.assertEqual(ship.anchor, 3)
        ship.anchor = 29
        g.adjust_ship_to_bounds(ship)
        self.assertEqual(ship.anchor, 1)

    def test_9_place_ship(self):
        g = BattleGrid(4,4,[],0)
        occupied_cells:list[int] = []

        occupied_cells.clear()
        ship_1_placed = g.place_ship(Ship(-3,True,ShipType.CRUISER),occupied_cells)
        ship_2_placed = g.place_ship(Ship(4 ,True,ShipType.CRUISER),occupied_cells)
        ship_3_placed = g.place_ship(Ship(10 ,True,ShipType.CRUISER),occupied_cells)
        self.assertTrue(ship_1_placed)
        self.assertFalse(ship_2_placed)
        self.assertTrue(ship_3_placed)

        occupied_cells.clear()
        ship_4_placed = g.place_ship(Ship(0,False,ShipType.TORPEDO),occupied_cells)
        ship_5_placed = g.place_ship(Ship(5,False,ShipType.ESCORTE),occupied_cells)
        ship_6_placed = g.place_ship(Ship(7,False,ShipType.CRUISER),occupied_cells)
        self.assertTrue(ship_4_placed)
        self.assertFalse(ship_5_placed)
        self.assertTrue(ship_6_placed)
    
    def test_10_generate(self):
        g = BattleGrid(0,0,[],0)

        g.generate()
        self.assertEqual(g.width, 0)
        self.assertEqual(g.height, 0)
        self.assertEqual(g.seed, 0)
        self.assertTrue(g.__is_generated__)
        self.assertTrue(g.__is_bounds_forced__)
        self.assertTrue(g.__is_ships_sorted__)

        g.set_number_ships_for_type(ShipType.CRUISER,1)
        g.set_number_ships_for_type(ShipType.ESCORTE,2)
        g.set_number_ships_for_type(ShipType.TORPEDO,3)
        g.set_number_ships_for_type(ShipType.SUBMARINE,4)
        g.generate()
        self.assertEqual(g.width, 10)
        self.assertEqual(g.height, 10)
        self.assertEqual(g.seed, 0)
        self.assertTrue(g.__is_generated__)
        self.assertTrue(g.__is_bounds_forced__)
        self.assertTrue(g.__is_ships_sorted__)
        self.assertEqual(len(g.ships),0)
        self.assertEqual(len(g.placed_ships),10)
        
        # tests procedural placement is repeatable
        expected_placement_cells = [
            [49, 59, 69, 79],
            [25,5,15],
            [65,75,85],
            [51,61],
            [97,87],
            [8,7],
            [11],
            [90],
            [93],
            [30]
        ]
        for i in range(10):
            self.assertEqual(set(g.placed_ships[i].placement_cells),set(expected_placement_cells[i]))
    
    def test_11_get_ship_for_cell(self):
        g = BattleGrid(0,0,[],0)
        g.generate()
        self.assertEqual(g.get_ship_for_cell(0),None)
        g.set_number_ships_for_type(ShipType.CRUISER,1)
        g.generate()
        ship = g.get_ship_for_cell(0)
        self.assertNotEqual(ship,None)
        self.assertEqual(ship.ship_type, ShipType.CRUISER)
    
    def test_12_get_ship_for_pos(self):
        g = BattleGrid(0,0,[],0)
        g.generate()
        self.assertEqual(g.get_ship_for_pos(0,0),None)
        g.set_number_ships_for_type(ShipType.CRUISER,1)
        g.generate()
        ship = g.get_ship_for_pos(0,0)
        self.assertNotEqual(ship,None)
        self.assertEqual(ship.ship_type, ShipType.CRUISER)

    def test_13_hit_cell(self):
        g = BattleGrid(0,0,[],0)
        g.generate()
        self.assertFalse(g.hit_cell(0))
        g.set_number_ships_for_type(ShipType.CRUISER,1)
        g.generate()
        self.assertTrue(g.hit_cell(0))
        self.assertFalse(g.hit_cell(10))

    def test_12_hit_pos(self):
        g = BattleGrid(0,0,[],0)
        g.generate()
        self.assertFalse(g.hit_pos(0,0))
        g.set_number_ships_for_type(ShipType.CRUISER,1)
        g.generate()
        self.assertTrue(g.hit_pos(0,0))
        self.assertFalse(g.hit_pos(0,4))

if __name__ == '__main__':
    unittest.main(verbosity=2)