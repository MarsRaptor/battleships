class Menu:

    class MenuOption:
        def __init__(self,index,option_prefix:str,prompt:str,handler) -> None:
            self.index = index
            self.option_prefix = option_prefix
            self.prompt_lines:list[str] = []
            self.handler = handler

            self.add_prompt_line("[{}] {}".format(index,prompt))

        def add_prompt_line(self,line:str)->None:
            self.prompt_lines.append("{}{}".format(self.option_prefix,line))
            
    def __init__(self,option_prefix:str) -> None:
        self.option_prefix = option_prefix
        self.header:list[str] = []
        self.options:list[Menu.MenuOption] = []
        self.footer:list[str] = []
    
    def create_option(self,prompt:str,handler=lambda : ()):
        option = Menu.MenuOption(len(self.options),self.option_prefix,prompt,handler)
        self.options.append(option)
        return option
    
    def select_option(self,index):
        if index < len(self.options):
            return self.options[index].handler
        else:
            return None

    def to_lines(self)->list[str]:
        lines :list[str] = []
        lines.extend(self.header)
        for opt in self.options:
            lines.extend(opt.prompt_lines)
        lines.extend(self.footer)
        return lines