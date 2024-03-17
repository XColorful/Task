class default_method_template():
    def __init__(self):
        self.label = ""
        self.version = "0"
        self.type = "Default_Template"
        self.method_list = []
    
    def method_info(self):
        return [self.label, self.version, self.type]
    
    def analyze(self, cmd_list:list, tasker_list:list, system_pkg:dict): # 分析是否存在可用指令，返回(bool，[标签，版本，类型])
        cmd = cmd_list[0]
        method_info = self.method_info() + [str(self.method_list)]
        if not cmd in self.method_list:
            return (False, method_info)
        return (system_pkg["CONDITION_SUCCESS"], method_info, self.method_info())

    def proceed(self, cmd_list:list, tasker_list:list, system_pkg:dict):
        cmd = cmd_list[0]
        cmd_parameter = cmd_list[1]
        proceed_method = getattr(self, cmd)
        return_tuple = proceed_method(cmd_parameter, tasker_list, system_pkg)
        return return_tuple