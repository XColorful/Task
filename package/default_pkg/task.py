from default_class import default_task_template

class default_task(default_task_template):
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
        return super().backup_list()
    
    def build(self, build_list:list):
        super().build(build_list)