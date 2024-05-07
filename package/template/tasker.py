from default_class import default_tasker_template
from default_class import extra_tasker_template
from .class_func import df_class_func_template, ex_class_func_template
from .interface import df_interface_template, ex_interface_template
from .update_info import ex_update_info

class df_tasker_template(default_tasker_template):
    version = "1.0" # 2024_02_15
    introduction = "Tasker Template"
    def __init__(self):
        super().__init__()
        self.function_list.append(df_class_func_template()) # Default版本仅有一种，不可修改,此处为Template示范
    
    # 实现方式1:使用默认interface
    def interface(self, system_pkg):
        if self.create_date == "":
            return_tuple = self.update_info(system_pkg)
            if self.create_date == "": return return_tuple
        
        system_pkg["head_msg"](self.tasker_label)
        # 使用默认interface
        return_tuple = super().interface(system_pkg)
        return return_tuple
    # 实现方式2:使用新建的interface
    def interface(self, system_pkg):
        return_tuple = df_interface_template(self, system_pkg)
        return return_tuple
    
    def update_info(self, system_pkg):
        return_tuple = super().update_info(system_pkg)
        return return_tuple
    
    def backup_list(self):
        return super().backup_list()
    
    def build(self, build_list: list, system_pkg: dict):
        return super().build(build_list, system_pkg)


class ex_tasker_template(extra_tasker_template):
    version = "ex_template"
    introduction = "extra type tasker template"
    def __init__(self):
        super().__init__() # 继承父类
        self.function_list.append(ex_class_func_template())
        self.description = ""
    
    def interface(self, system_pkg):
        return_tuple = ex_interface_template(self, system_pkg)
        return return_tuple
    
    def update_info(self, system_pkg):
        return_tuple = ex_update_info(self, system_pkg)
        return return_tuple
    
    def backup_list(self):
        return super().backup_list()
    
    def build(self, build_list: list, system_pkg: dict):
        return None