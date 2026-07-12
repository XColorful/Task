from default_class import default_task_template, extra_task_template

class df_task_template(default_task_template):
    version = "1.0" # 2024_02_15
    def __init__(self):
        super().__init__() # 继承父类
    
    def __str__(self):
        return f"{self.date}|{self.attribute}|{self.content}"
    
    def update(self, info_dict:dict, system_pkg:dict): # 保留原始方式
        super().update(info_dict, system_pkg)
    
    def backup(self):
        return super().backup()
    
    def backup_list(self):
        """用于创建build_list"""
        return super().backup_list()
    
    def build(self, build_list:list):
        super().build(build_list)


class ex_task_template(extra_task_template):
    version = "ex_template"
    def __init__(self):
        super().__init__() # 继承父类
        # extra attributes here
        
    def __str__(self):
        return f"{self.date}|{self.attribute}|{self.content}"
    
    def update(self, info_dict:dict, system_pkg:dict):
        return None
    
    def backup_list(self) -> tuple:
        """用于创建build_list"""
        backup_dict_list = []
        return backup_dict_list
    
    def build(self, build_list: list):
        return None