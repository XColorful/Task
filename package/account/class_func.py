from default_class_func import extra_container_func_template
from .function import YYYY_MM_DD

class account_container_func(extra_container_func_template):
    def __init__(self):
        super().__init__() # 继承父类
        self.label = "account_container_func"
        self.version = "account"
        self.function_list = []
        self.create_date = YYYY_MM_DD()
    
    def __str__(self):
        return super().__str__()
    
    def get_info(self):
        return super().get_info()
    
    def proceed(self, command_list:list, container, system_pkg:dict):
        super().proceed(command_list, container, system_pkg)