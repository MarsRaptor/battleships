import pygame
import pygame_gui
from math import floor
from sys import exit as sys_exit,maxsize
from game.components import BattleGrid,ShipType
from game.util import is_int
from random import randint
import clipboard as c
import logging
from os import path, makedirs,sep

#=== LOGGING CONSTANTS
LOGGING_FOLDER = ".log"
LOGGING_FILE = "battleships_gui.log"
LOGGING_LVL  = logging.WARNING
#===

class Menu:
    def __init__(self,window_surface:pygame.Surface) -> None:
        self.grid = BattleGrid(0,0,[ShipType.SUBMARINE]*4+[ShipType.TORPEDO]*3+[ShipType.ESCORTE]*2+[ShipType.CRUISER],randint(0,maxsize))
        self.clock = pygame.time.Clock()
        self.manager = pygame_gui.UIManager((800, 600))
        self.window_surface = window_surface
        self.background = pygame.Surface((800, 600))
        self.background.fill(pygame.Color('#000000'))
        self.title_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((150, 20), (500, 100)),
            manager=self.manager,
            starting_layer_height=1
        )
        self.title_text = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, 0), (500, 100)),
            text='Battleships',
            manager=self.manager,
            container=self.title_panel,
        )
        self.main_menu_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((150, 140), (500, 440)),
            manager=self.manager,
            starting_layer_height=1
        )
        self.main_menu_new_game_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((50, 40), (400, 100)),
            text='NEW GAME',
            manager=self.manager,
            container=self.main_menu_panel,
        )
        self.main_menu_howto_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((50, 170), (400, 100)),
            text='HOW TO PLAY',
            manager=self.manager,
            container=self.main_menu_panel,
        )
        self.main_menu_quit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((50, 300), (400, 100)),
            text='QUIT',
            manager=self.manager,
            container=self.main_menu_panel,
        )

        self.howto_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((150, 140), (500, 440)),
            manager=self.manager,
            starting_layer_height=1
        )
        self.howto_text = pygame_gui.elements.UITextBox(
            html_text="Dems the rules",
            relative_rect=pygame.Rect((45, 40), (400, 300)),
            manager=self.manager,
            container=self.howto_panel,
        )
        self.howto_back_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((45, 365), (400, 40)),
            text='BACK',
            manager=self.manager,
            container=self.howto_panel,
        )
        self.howto_panel.hide()

        self.new_game_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((150, 140), (500, 440)),
            manager=self.manager,
            starting_layer_height=1
        )
        self.new_game_panel.hide()
        
        self.grid_width_text = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 30), (115, 50)),
            text='Grid width: ',
            manager=self.manager,
            container=self.new_game_panel,
        )
        self.grid_width_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((125, 40), (300, 50)),
            manager=self.manager,
            container=self.new_game_panel
        )
        self.grid_width_input.set_text(str(self.grid.width))

        self.grid_height_text = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 60), (115, 50)),
            text='Grid height: ',
            manager=self.manager,
            container=self.new_game_panel,
        )
        self.grid_height_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((125, 70), (300, 50)),
            manager=self.manager,
            container=self.new_game_panel
        )
        self.grid_height_input.set_text(str(self.grid.height))

        self.grid_seed_text = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 90), (115, 50)),
            text='Grid seed: ',
            manager=self.manager,
            container=self.new_game_panel,
        )
        self.grid_seed_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((125, 100), (300, 50)),
            manager=self.manager,
            container=self.new_game_panel
        )
        self.grid_seed_input.set_text(str(self.grid.seed))

        self.grid_boats_text = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 120), (115, 50)),
            text='Grid boats: ',
            manager=self.manager,
            container=self.new_game_panel,
        )
        self.grid_boats_inputs : dict = {}
        shiptypes_counter=0
        for data in ShipType:
            count_for_type = sum( (lambda ship_type : ship_type == data)(x) for x in self.grid.ships)
            self.grid_boats_inputs[data.name]={
                "label": pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect((20, 150 + shiptypes_counter * 30), (115, 50)),
                    text=data.name,
                    manager=self.manager,
                    container=self.new_game_panel,
                ),
                "input" :pygame_gui.elements.UITextEntryLine(
                    relative_rect=pygame.Rect((135, 160 + shiptypes_counter * 30), (290, 50)),
                    manager=self.manager,
                    container=self.new_game_panel
                )
            }
            self.grid_boats_inputs[data.name]["input"].set_text(str(count_for_type))
            shiptypes_counter +=1
        
        self.new_game_back_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((45, 365), (400, 40)),
            text='BACK',
            manager=self.manager,
            container=self.new_game_panel,
        )

        self.new_game_start_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((45, 300), (400, 60)),
            text='START GAME',
            manager=self.manager,
            container=self.new_game_panel,
        )

    
    def game_logic(self):
        is_running = True
        time_delta = self.clock.tick(60)/1000.0
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                is_running = False

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.main_menu_quit_button:
                        sys_exit()
                    elif event.ui_element == self.main_menu_new_game_button:
                        self.main_menu_panel.hide()
                        self.howto_panel.hide()
                        self.new_game_panel.show()
                    elif event.ui_element == self.main_menu_howto_button:
                        self.new_game_panel.hide()
                        self.main_menu_panel.hide()
                        self.howto_panel.show()
                    elif event.ui_element == self.howto_back_button:
                        self.howto_panel.hide()
                        self.new_game_panel.hide()
                        self.main_menu_panel.show() 
                    elif event.ui_element == self.new_game_back_button:
                        self.howto_panel.hide()
                        self.new_game_panel.hide()
                        self.main_menu_panel.show() 
                    elif event.ui_element == self.new_game_start_button:
                        self.howto_panel.hide()
                        self.new_game_panel.hide()
                        self.main_menu_panel.show() 

                        if is_int(self.grid_width_input.text):
                            width = int(self.grid_width_input.text)
                            if width >= self.grid.calculate_min_bounds() and width < maxsize:
                                self.grid.set_width(width)
                        if is_int(self.grid_height_input.text):
                            height = int(self.grid_height_input.text)
                            if height >= self.grid.calculate_min_bounds() and height < maxsize:
                                self.grid.set_height(height) 
                        if is_int(self.grid_height_input.text):
                            seed = int(self.grid_seed_input.text)
                            if seed >= 0 and seed < maxsize:
                                self.grid.seed = seed  
                        for data in ShipType:
                            shiptype_input = self.grid_boats_inputs[data.name]["input"]
                            if is_int(shiptype_input.text):
                                amount = int(shiptype_input.text)
                                if amount >= 0 and amount < maxsize:
                                    self.grid.set_number_ships_for_type(data,amount)  
                            
                        Game(self.window_surface,self.grid).loop()
                        self.grid.placed_ships.clear()
                        self.grid.missed_shots.clear()
                        self.grid.seed = randint(0,maxsize)
                        self.grid_width_input.set_text(str(self.grid.width))
                        self.grid_height_input.set_text(str(self.grid.height))
                        self.grid_seed_input.set_text(str(self.grid.seed))
                        for data in ShipType:
                            count_for_type = sum( (lambda ship_type : ship_type == data)(x) for x in self.grid.ships)
                            self.grid_boats_inputs[data.name]["input"].set_text(str(count_for_type))
                        
                if event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                    if event.ui_element == self.grid_width_input:
                        if is_int(self.grid_width_input.text):
                            width = int(self.grid_width_input.text)
                            if width >= self.grid.calculate_min_bounds() and width < maxsize:
                                self.grid.set_width(width)
                    elif event.ui_element == self.grid_height_input:
                        if is_int(self.grid_height_input.text):
                            height = int(self.grid_height_input.text)
                            if height >= self.grid.calculate_min_bounds() and height < maxsize:
                                self.grid.set_height(height)  
                    elif event.ui_element == self.grid_seed_input:
                        if is_int(self.grid_height_input.text):
                            seed = int(self.grid_seed_input.text)
                            if seed >= 0 and seed < maxsize:
                                self.grid.seed = seed    

                    for data in ShipType:
                        shiptype_input = self.grid_boats_inputs[data.name]["input"]
                        if event.ui_element == shiptype_input:
                            if is_int(shiptype_input.text):
                                amount = int(shiptype_input.text)
                                if amount >= 0 and amount < maxsize:
                                    self.grid.set_number_ships_for_type(data,amount)  
                            break
                   
            self.manager.process_events(event)

        self.manager.update(time_delta)

        return is_running

    def draw(self):
        self.window_surface.blit(self.background, (0, 0))
        self.manager.draw_ui(self.window_surface)
        pygame.display.update()

    def loop(self):
        is_running = True
        while is_running:
            is_running = self.game_logic()
            self.draw()

class Game:
    def __init__(self,window_surface:pygame.Surface,battlegrid:BattleGrid) -> None:
        self.grid = Grid(battlegrid,(25,50))
        self.clock = pygame.time.Clock()

        self.manager = pygame_gui.UIManager((800, 600))
        self.window_surface = window_surface
        self.background = pygame.Surface((800, 600))
        self.background.fill(pygame.Color('#000000'))

        self.side_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((540, 50), (240, 491)),
            manager=self.manager,
            starting_layer_height=1
        )

        self.hit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 120), (233, 50)),
            text='Hit',
            manager=self.manager,
            container=self.side_panel,
        )

        self.current_cell_text = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, 0), (233, 50)),
            text='Current cell (0,0)',
            manager=self.manager,
            container=self.side_panel,
        )

        self.remaining_ships_text = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, 180), (150, 50)),
            text='Remaining ships:',
            manager=self.manager,
            container=self.side_panel,
        )

        self.remaining_ships_texts:list[pygame_gui.elements.UILabel] = []        

        self.offset_x_text = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, 30), (115, 50)),
            text='Offset X: ',
            manager=self.manager,
            container=self.side_panel,
        )

        self.offset_x_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((115, 40), (115, 50)),
            manager=self.manager,
            container=self.side_panel
        )
        self.offset_x_input.set_text(str(self.grid.offset_x))

        self.offset_y_text = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, 60), (115, 50)),
            text='Offset Y: ',
            manager=self.manager,
            container=self.side_panel,
        )

        self.offset_y_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((115, 70), (115, 50)),
            manager=self.manager,
            container=self.side_panel
        )
        self.offset_y_input.set_text(str(self.grid.offset_y))

        self.copy_seed_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 388), (233, 50)),
            text='Copy seed to clipboard',
            manager=self.manager,
            container=self.side_panel,
        )

        self.quit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 435), (233, 50)),
            text='Quit',
            manager=self.manager,
            container=self.side_panel,
        )

        self.quit_confirm_dialog = pygame_gui.elements.UIWindow(
            window_display_title="Quit game",
            manager=self.manager,
            rect=pygame.Rect((250, 150), (300, 300))
        )
        self.quit_confirm_dialog.hide()

        self.quit_confirm_dialog_resume_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((35, 30), (200, 50)),
            text='Resume',
            manager=self.manager,
            container=self.quit_confirm_dialog,
        )
        self.quit_confirm_dialog_menu_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((35, 90), (200, 50)),
            text='Quit to main menu',
            manager=self.manager,
            container=self.quit_confirm_dialog,
        )
        self.quit_confirm_dialog_exit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((35, 150), (200, 50)),
            text='Quit to desktop',
            manager=self.manager,
            container=self.quit_confirm_dialog,
        )

        self.win_dialog = pygame_gui.elements.UIWindow(
            window_display_title="You win!",
            manager=self.manager,
            rect=pygame.Rect((250, 150), (300, 300))
        )
        self.win_dialog.hide()
        self.win_dialog_text = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((35, 60), (200, 50)),
            text='Congratulations!',
            manager=self.manager,
            container=self.win_dialog,
        )
        self.win_dialog_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((35, 150), (200, 50)),
            text='Quit to main menu',
            manager=self.manager,
            container=self.win_dialog,
        )

    def game_logic(self):
        is_running = True
        time_delta = self.clock.tick(60)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.hit_button:
                        self.grid.battlegrid.hit_cell(self.grid.battlegrid.selected_cell)
                    elif event.ui_element == self.copy_seed_button:
                        c.copy(self.grid.battlegrid.seed)
                    elif event.ui_element == self.quit_button:
                        self.quit_confirm_dialog.show()
                    elif event.ui_element == self.quit_confirm_dialog_resume_button:
                        self.quit_confirm_dialog.hide()
                    elif event.ui_element == self.quit_confirm_dialog_menu_button:
                        is_running = False
                    elif event.ui_element == self.quit_confirm_dialog_exit_button:
                        sys_exit()
                    elif event.ui_element == self.win_dialog_button:
                        self.win_dialog.hide()
                        is_running = False
                if event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                    if event.ui_element == self.offset_x_input:
                        if is_int(self.offset_x_input.text):
                            offset = int(self.offset_x_input.text)
                            if offset >= 0 and offset < self.grid.battlegrid.width:
                                self.grid.offset_x = offset
                    elif event.ui_element == self.offset_y_input:
                        if is_int(self.offset_y_input.text):
                            offset = int(self.offset_y_input.text)
                            if offset >= 0 and offset < self.grid.battlegrid.height:
                                self.grid.offset_y = offset

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: # 1 == left button
                    self.grid.mouse_click()
                    

            self.manager.process_events(event)
        already_hit = False
        for ship in self.grid.battlegrid.placed_ships:
            if self.grid.battlegrid.selected_cell in ship.hits:
                already_hit = True
                break
        if not already_hit and self.grid.battlegrid.selected_cell not in self.grid.battlegrid.missed_shots:
            self.hit_button.enable()
        else:
            self.hit_button.disable()

        self.grid.mouse_update()

        self.current_cell_text.set_text( "Current cell ({},{})".format(
            self.grid.battlegrid.selected_cell%self.grid.battlegrid.width,
            floor(self.grid.battlegrid.selected_cell/self.grid.battlegrid.width)
        ))

        for t in self.remaining_ships_texts:
            t.remove()
        self.remaining_ships_texts.clear()
        remaining_ships_texts_i=0
        total_ship_remaining = 0
        for data in ShipType:
            count_placed_of_type = sum( (lambda s : s.ship_type == data and not s.is_destroyed())(s) for s in self.grid.battlegrid.placed_ships)
            self.remaining_ships_texts.append(
                pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect((0, 220+remaining_ships_texts_i*30), (233, 50)),
                    text='{:15} x{}'.format(data.name, count_placed_of_type),
                    manager=self.manager,
                    container=self.side_panel,
                )
            )
            remaining_ships_texts_i += 1
            total_ship_remaining+=count_placed_of_type
        if total_ship_remaining < 1:
            self.win_dialog.show()

        self.manager.update(time_delta)

        return is_running

    def draw(self):
        self.window_surface.blit(self.background, (0, 0))
        self.grid.draw(self.window_surface)        
        self.manager.draw_ui(self.window_surface)

        pygame.display.update()

    def loop(self):
        is_running = True
        while is_running:
            is_running = self.game_logic()
            self.draw()

            

def sub_sprite(sprite:pygame.Surface,dx:int,dy:int,dw:int,dh:int,sx:int,sy:int,sw:int,sh:int):
    
    s1 = pygame.Surface((sw,sh),pygame.SRCALPHA, 32).convert_alpha()
    s1.blit(sprite,(-sx,-sy))

    s = pygame.Surface((dw,dh),pygame.SRCALPHA, 32).convert_alpha()
    s.blit(s1,(dx,dy))
    return s

class Grid:

    def __init__(self,grid:BattleGrid,pos=(0,0)) -> None:
        self.battlegrid = grid
        self.battlegrid.generate()
        self.pos = pos
        self.offset_x = 0
        self.offset_y = 0
        self.surface = pygame.Surface((491,491))
        self.sprites = self.__create_sprites()

        self.hovered_cell = 0
    
    def __create_sprites(self):
        grid_sprites  = pygame.image.load("assets/grid_sprites.png").convert_alpha()
        
        surface_ship_anchor_h = sub_sprite(
            sprite=grid_sprites,
            dx=24,
            dy=0,
            dw=48,
            dh=48,
            sx=0,
            sy=0,
            sw = 24,
            sh = 48
        )
        surface_ship_body_h= sub_sprite(
            sprite=grid_sprites,
            dx=0,
            dy=0,
            dw=48,
            dh=48,
            sx=24,
            sy=0,
            sw = 48,
            sh = 48
        )
        surface_ship_tip_h = sub_sprite(
            sprite=grid_sprites,
            dx=0,
            dy=0,
            dw=48,
            dh=48,
            sx=72,
            sy=0,
            sw = 24,
            sh = 48
        )

        surface_ship_single_h = pygame.Surface((48,48),pygame.SRCALPHA, 32).convert_alpha()
        surface_ship_single_h.blit(surface_ship_anchor_h,(-24,0))
        surface_ship_single_h.blit(surface_ship_tip_h,(24,0))

        surface_ship_anchor_v = pygame.transform.rotate(surface_ship_anchor_h.copy(),270)
        surface_ship_body_v = pygame.transform.rotate(surface_ship_body_h.copy(),270)
        surface_ship_tip_v = pygame.transform.rotate(surface_ship_tip_h.copy(),270)
        surface_ship_single_v = pygame.transform.rotate(surface_ship_single_h.copy(),270)

        surface_miss = sub_sprite(grid_sprites,0,0,48,48,0,48,48,48)
        surface_hit = sub_sprite(grid_sprites,0,0,48,48,48,48,48,48)

        return {
            "ship" : {
                "h" : {
                    "anchor" : surface_ship_anchor_h,
                    "body" : surface_ship_body_h,
                    "tip" : surface_ship_tip_h,
                    "single" : surface_ship_single_h
                },
                "v" : {
                    "anchor" : surface_ship_anchor_v,
                    "body" : surface_ship_body_v,
                    "tip" : surface_ship_tip_v,
                    "single" : surface_ship_single_v
                }
            },
            "map": {
                "miss" : surface_miss,
                "hit" : surface_hit,
            }
        }

    def cell_for_pos(self,pos):
        if pos[0] > self.pos[0] and pos[0] < self.pos[0] + 491 and pos[1] > self.pos[1] and pos[1] < self.pos[1] + 491:
            rel_x = pos[0] - self.pos[0]
            rel_y = pos[1] - self.pos[1]
            cell_x = floor(rel_x/(491/10))
            cell_y = floor(rel_y/(491/10))
            if cell_x < self.battlegrid.width and cell_y < self.battlegrid.height:
                return (cell_x) + 10 * (cell_y)
        return -1

    def mouse_click(self):
        mouse_x,mouse_y=pygame.mouse.get_pos()
        if mouse_x >= self.pos[0] and mouse_x < self.pos[0] + 491 and mouse_y >= self.pos[1] and mouse_y < self.pos[1] + 491:
            relative_cell = self.cell_for_pos((mouse_x,mouse_y))
            if relative_cell > -1:
                relative_cell_x = relative_cell%10
                relative_cell_y = floor(relative_cell/10)
                absolute_cell = (self.offset_x+relative_cell_x) + self.battlegrid.width * (self.offset_y+relative_cell_y)
                if absolute_cell< self.battlegrid.width * self.battlegrid.height:
                    self.battlegrid.selected_cell = absolute_cell                    

    def mouse_update(self):
        mouse_x,mouse_y=pygame.mouse.get_pos()
        if mouse_x >= self.pos[0] and mouse_x < self.pos[0] + 491 and mouse_y >= self.pos[1] and mouse_y < self.pos[1] + 491:
            relative_cell = self.cell_for_pos((mouse_x,mouse_y))
            relative_cell_x = relative_cell%10
            relative_cell_y = floor(relative_cell/10)
            absolute_cell = (self.offset_x+relative_cell_x) + self.battlegrid.width * (self.offset_y+relative_cell_y)
            if relative_cell_x>=0 and relative_cell_y>=0 and absolute_cell< self.battlegrid.width * self.battlegrid.height:
                self.hovered_cell = absolute_cell
            else:
                self.hovered_cell = self.battlegrid.selected_cell      
        else:
            self.hovered_cell = self.battlegrid.selected_cell                  

    def draw(self,surface:pygame.Surface):
        self.surface.fill("#000000")
        for y in range(min(10,self.battlegrid.height)):
            for x in range(min(10,self.battlegrid.width)):
                cell_index = (self.offset_x+x) + self.battlegrid.width * (self.offset_y+y)
                is_occupied = False
                pos_x = 1+ x * 48 + x
                pos_y = 1+ y * 48 + y
                if cell_index == self.hovered_cell:
                    pygame.draw.rect(self.surface, pygame.Color(25,80,0),pygame.Rect(pos_x,pos_y,48,48))
                if cell_index == self.battlegrid.selected_cell:
                    pygame.draw.rect(self.surface, pygame.Color(25,80,0),pygame.Rect(pos_x,pos_y,48,48))
                for ship in self.battlegrid.placed_ships: 
                    if cell_index in ship.hits:
                        ship_orientation = "h" if ship.is_horizontal else "v"
                        cell_index_in_ship = ship.placement_cells.index(cell_index)
                        if ship.is_destroyed():                            
                            if cell_index_in_ship == 0:                                                               
                                if cell_index_in_ship == len(ship.placement_cells)-1:                                    
                                    self.surface.blit(self.sprites["ship"][ship_orientation]["single"],(pos_x,pos_y))
                                else:
                                    self.surface.blit(self.sprites["ship"][ship_orientation]["anchor"],(pos_x,pos_y))
                            elif cell_index_in_ship == len(ship.placement_cells)-1:
                                self.surface.blit(self.sprites["ship"][ship_orientation]["tip"],(pos_x,pos_y))
                            else:
                                self.surface.blit(self.sprites["ship"][ship_orientation]["body"],(pos_x,pos_y))
                        else:
                            self.surface.blit(self.sprites["map"]["hit"],(pos_x,pos_y))
                        is_occupied = True
                        break
                if not is_occupied and cell_index in self.battlegrid.missed_shots:
                    self.surface.blit(self.sprites["map"]["miss"],(pos_x,pos_y))
                    is_occupied = True   
        for y in range(12):
            pos_y = y*49
            pygame.draw.line(self.surface, pygame.Color(76,255,0), (0, pos_y), (491, pos_y))          
            for x in range(12):
                pos_x = x*49
                pygame.draw.line(self.surface, pygame.Color(76,255,0), (pos_x, 0), (pos_x, 491))            
        surface.blit(self.surface,self.pos)
                



if __name__ == '__main__':
    if not path.exists(LOGGING_FOLDER):makedirs(LOGGING_FOLDER)
    logging.basicConfig(filename="{}{}{}".format(LOGGING_FOLDER,sep,LOGGING_FILE), encoding='utf-8', level=LOGGING_LVL)
    pygame.init()
    pygame.display.set_caption('Battleships')
    Menu(pygame.display.set_mode((800, 600))).loop()


