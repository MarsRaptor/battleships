from os import system,name as os_name

def cls():
    system('cls' if os_name=='nt' else 'clear')

def print_lines(lines:list[str],clear:bool= True)->None:
    if clear : cls()
    for line in lines: print(line)