# Battleships
Single player battleships, via CLI or GUI using [pygame](https://www.pygame.org) and [pygame_gui](https://github.com/MyreMylar/pygame_gui)

## Requirements

 - Python 3.9+

## How to install

1. Clone or download as zip this repo.
2. At this point you can run the CLI version of the game.
```
python battleships_cli.py
```
3. To run the GUI version or the grid dump utility you need to install some python packages.
This can be done 2 ways:
   - Manually installing each package (Pillow,pygame,pygame-gui,clipboard,pyperclip).
   - Running the following command in a command prompt (the pip command is a default option during the Python install):
    ```
    pip install -r requirements.txt
    ```
4. At this point you can run all versions of the game and utilities
   - battleships_cli.py : the command line version of the battleships game.
   - battleships_gui.pyw : the graphical version of the battleships game.
   - battleships_dump.py : generate a game grid, including ship placements, via the command line that is dumped to a txt and a png file. Used to quickly visualize grids, for testing (and cheating if you are so inclined). 
   - battleships_test.py : used for unit tests.

## Screenshots of the CLI version

![cli_shots](https://user-images.githubusercontent.com/14842426/138297124-d0511385-72f2-4c61-8cfc-3242a23ff240.png)

## Screenshots of the GUI version

![gui_shots_menu](https://user-images.githubusercontent.com/14842426/138297251-a4a7b9e0-3156-4c34-9f25-a6d89a404bea.png)

![gui_shots_game](https://user-images.githubusercontent.com/14842426/138297289-3397d6a9-dff2-4bea-9e08-6f23ec431ee2.png)
