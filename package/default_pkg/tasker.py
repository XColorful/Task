from default_class import default_tasker_template
from .class_func import default_tasker_func

class default_tasker(default_tasker_template):
    version = "1.0" # 2024_02_15
    introduction = "默认类型Tasker"
    def __init__(self):
        super().__init__() # 继承父类
        self.function_list.append(default_tasker_func()) # Default版本仅有一种，不可修改
    
    def interface(self, system_pkg): # 仅有一种，不可修改
        if self.create_date == "": # 如果create_date为空（未补充过Tasker信息）
            return_tuple = self.update_info(system_pkg)
            if self.create_date == "": return return_tuple # 如果未补充完信息
        
        system_pkg["head_msg"](self.tasker_label)
        # 使用默认interface
        return_tuple = super().interface(system_pkg)
        return return_tuple
    
    def update_info(self, system_pkg): # 仅有一种，不可修改
        return_tuple = super().update_info(system_pkg)
        return return_tuple
    
    def backup_list(self):
        return super().backup_list()
    
    def build(self, build_list: list, system_pkg: dict):
        return super().build(build_list, system_pkg)