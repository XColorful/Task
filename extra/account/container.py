from default_class import extra_container_template
from .class_func import extra_container_func
from .interface import extra_interface
from .update_info import extra_update_info

class extra_container(extra_container_template):
    def __init__(self):
        super().__init__() # 继承父类
        self.function_list.append(extra_container_func()) # Default_Template版本仅有一种，不可修改
        self.version = "account"
        self.description = "account类容器"
    
    def interface(self, system_pkg): # 仅有一种，不可修改
        if self.create_date == "": # 如果create_date为空（未补充过容器信息）
            return_tuple = self.update_info(system_pkg)
            if self.create_date == "": return return_tuple # 如果未补充完信息
        
        system_pkg["head_msg"](self.container_label)
        
        return_tuple = extra_interface(self, system_pkg)
        return return_tuple
    
    def update_info(self, system_pkg): # 仅有一种，不可修改
        return_tuple = extra_update_info(self, system_pkg)
        return return_tuple
    
    def backup(self):
        return None
    
    def backup_list(self):
        # 
        return []
    
    def build(self, build_list: list, system_pkg: dict):
        # 
        return None