from default_class_func import default_tasker_func_template, extra_tasker_func_template
from .function import YYYY_MM_DD

class df_class_func_template(default_tasker_func_template):
    def __init__(self):
        super().__init__() # 继承父类
        self.label = "df_class_func_template"
        self.version = "1.0"
        self.function_list = ["test"]
        # 供调试时查看信息用，不可见
        self.create_date = YYYY_MM_DD()
    
    def __str__(self):
        return super().__str__()
    
    def get_info(self):
        return super().get_info()

    def proceed(self, command_list:list, tasker, system_pkg:dict):
        return super().proceed(command_list, tasker, system_pkg)
    
    def test(self, parameter, tasker, system_pkg) -> list[int]:
        system_pkg["normal_msg"]("test:class_func_template")
        system_pkg["body_msg"]([f"tasker.tasker_name:{tasker.tasker_name}"])
        if parameter != "":
            system_pkg["normal_msg"]("test:parameter")
            system_pkg["body_msg"]([parameter])


class ex_class_func_template(extra_tasker_func_template):
    def __init__(self):
        super().__init__()
        self.label = "ex_class_func_template"
        self.version = "ex_template"
        self.function_list = ["test"]
        self.create_date = YYYY_MM_DD()
    
    def __str__(self):
        return super().__str__()
    
    def get_info(self):
        return super().get_info()
    
    def proceed(self, cmd_list:list, tasker, system_pkg:dict):
        super().proceed(cmd_list, tasker, system_pkg)
    
    def test(self, parameter, tasker, system_pkg) -> None:
        system_pkg["normal_msg"]("test:class_func_template")
        system_pkg["body_msg"]([f"tasker.tasker_name:{tasker.tasker_name}"])
        if parameter != "":
            system_pkg["normal_msg"]("test:parameter")
            system_pkg["body_msg"]([parameter])