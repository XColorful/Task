from default_class import default_task_template

class default_task(default_task_template):
    def __init__(self):
        super().__init__() # 继承父类
        self.version = "1.0" # 2024_02_15
    
    def __str__(self):
        return f"{self.date}|{self.attribute}|{self.content}"
    
    def update(self, info_dict:dict, system_pkg:dict): # 保留原始方式
        super().update(info_dict, system_pkg)
    
    def backup(self):
        if self.create_date == "": return "" # 未创建的task不返回备份
        return f"{self.type}||||{self.version}||||{self.create_date}||||{self.date}||||{self.attribute}||||{self.content}||||{self.comment}"