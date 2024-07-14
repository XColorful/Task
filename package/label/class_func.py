from default_class_func import extra_tasker_func_template
from .function import YYYY_MM_DD

class label_tasker_func(extra_tasker_func_template):
    def __init__(self):
        super().__init__()
        self.label = "label_tasker_func"
        self.version = "label"
        self.function_list = ["new", "delete", "edit", "search", "config"]
        self.create_date = YYYY_MM_DD()
    
    def __str__(self):
        return super().__str__()
    
    def get_info(self):
        return super().get_info()
    
    def proceed(self, cmd_list:list, tasker, system_pkg:dict):
        super().proceed(cmd_list, tasker, system_pkg)
    
    def new(self, parameter, tasker, system_pkg) -> None:
        return None
    
    def delete(self, parameter, tasker, system_pkg) -> None:
        return None
    
    def edit(self, parameter, tasker, system_pkg) -> None:
        return None
    
    def search(self, parameter, tasker, system_pkg) -> None:
        return None
    
    def config(self, parameter, tasker, system_pkg) -> None:
        return None


class label_analyze_func(extra_tasker_func_template):
    def __init__(self):
        super().__init__()
        self.label = "label_tasker_func"
        self.version = "label"
        self.function_list = ["details", "list_label"]
        self.create_date = YYYY_MM_DD()
    
    def __str__(self):
        return super().__str__()
    
    def get_info(self):
        return super().get_info()
    
    def proceed(self, cmd_list:list, tasker, system_pkg:dict):
        super().proceed(cmd_list, tasker, system_pkg)
    
    def list_label(self, parameter, tasker, system_pkg) -> None:
        """统计相关数据"""
        return None
    
    def list_label(self, parameter, tasker, system_pkg) -> None:
        """输入标签，查找，分析相关信息"""
        return None