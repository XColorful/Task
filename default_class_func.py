class default_tasker_func_template():
    def __init__(self):
        # 确定必要信息
        self.label = ""
        self.version = "0"
        self.type = "Default"
        self.function_list = []
    
    def __str__(self):
        return f"{self.label} {self.version} {self.type}"
    
    def get_info(self):
        return [self.label, self.version, self.type, self.function_list]

    def proceed(self, cmd_list:list, tasker, system_pkg:dict):
        cmd = cmd_list[0]
        try: cmd_parameter = cmd_list[1]
        except IndexError: cmd_parameter = ""
        proceed_function = getattr(self, cmd)
        proceed_function(cmd_parameter, tasker, system_pkg)
        return None

class extra_tasker_func_template(default_tasker_func_template):
    def __init__(self):
        super().__init__() # 继承父类
        self.label = ""
        self.version = ""
        self.type = "Extra"
        self.function_list = []
        
    def __str__(self):
        return super().__str__()
    
    def get_info(self):
        return super().get_info()
    
    def proceed(self, cmd_list:list, tasker, system_pkg:dict):
        super().proceed(cmd_list, tasker, system_pkg)