class default_container_func_template():
    def __init__(self):
        # 确定必要信息
        self.label = ""
        self.version = "0"
        self.type = "Default_Template"
        self.function_list = []
    
    def __str__(self):
        return f"{self.label} {self.version} {self.type}"
    
    def get_info(self):
        return [self.label, self.version, self.type, self.function_list]

    def proceed(self, command_list:list, container, system_pkg:dict):
        command = command_list[0]
        try: command_parameter = command_list[1]
        except IndexError: command_parameter = ""
        proceed_function = getattr(self, command)
        proceed_function(command_parameter, container, system_pkg)
        return None