class default_method_template():
    def __init__(self):
        self.label = ""
        self.version = "0"
        self.type = "Default_Template"
        self.method_list = []
    
    def method_info(self):
        return [self.label, self.version, self.type]
    
    def analyze(self, command_list:list, container_list:list, system_pkg:dict): # 分析是否存在可用指令，返回(bool，[标签，版本，类型])
        command = command_list[0]
        if not command in self.method_list:
            return (False, self.method_info() + [str(self.method_list)])
        return (system_pkg["CONDITION_SUCCESS"], None, self.method_info())

    def proceed(self, command_list:list, container_list:list, system_pkg:dict):
        command = command_list[0]
        command_parameter = command_list[1]
        proceed_method = getattr(self, command)
        return_tuple = proceed_method(command_parameter, container_list, system_pkg)
        return return_tuple