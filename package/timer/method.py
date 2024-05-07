from default_method import default_method_template

class timer_task_method(default_method_template):
    def __init__(self):
        super().__init__() # 继承父类
        self.label = "timer_task_method"
        self.version = "timer"
        self.method_list = ["timer"]
    
    def method_info(self):
        return super().method_info()
    
    def analyze(self, cmd_list:list, tasker_list:list, system_pkg:dict): # 分析是否存在可用指令，返回(bool，[标签，版本，类型])
        return super().analyze(cmd_list, tasker_list, system_pkg)

    def proceed(self, cmd_list:list, tasker_list:list, system_pkg:dict):
        return super().proceed(cmd_list, tasker_list, system_pkg)
    
    def timer(self, cmd_parameter:str, tasker_list:list, system_pkg:dict) -> tuple:
        """参数输入格式为YYYY_MM_DD"""
        # 继续选择输入'u'，'t', 'all'（默认为all）
        # u -> 当天未完成
        # t -> 当天完成
        # all -> 包含当天的都算
        return (system_pkg["CONDITION_SUCCESS"], "")