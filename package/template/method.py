from default_method import default_method_template

class method_template(default_method_template):
    def __init__(self):
        super().__init__() # 继承父类
        self.label = "method_template"
        self.version = "1.0"
        self.method_list = ["test"]
    
    def method_info(self):
        return super().method_info()
    
    def analyze(self, cmd_list:list, tasker_list:list, system_pkg:dict): # 分析是否存在可用指令，返回(bool，[标签，版本，类型])
        return super().analyze(cmd_list, tasker_list, system_pkg)

    def proceed(self, cmd_list:list, tasker_list:list, system_pkg:dict):
        return super().proceed(cmd_list, tasker_list, system_pkg)
    
    def method(self, cmd_parameter:str, tasker_list:list, system_pkg:dict) -> tuple:
        system_pkg["normal_msg"]("test:method_template")
        system_pkg["body_msg"]([f"method.label:{self.label}"])
        if cmd_parameter != "":
            system_pkg["normal_msg"]("test:cmd_parameter")
        return (system_pkg["CONDITION_SUCCESS"], "method_template test")