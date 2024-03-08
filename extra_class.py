from default_class import default_container_template, default_task_template

class extra_container_template(default_container_template):
    def __init__(self):
        super().__init__() #继承父类
        self.container_label = ""
        self.description = ""
        self.function_list = []
        self.create_date = ""
        self.version = "0" # 用字符串表示
        self.type = "Extra_Template"
        self.task_list = []
        self.task_template = []

    def interface(self, system_pkg):
        return (system_pkg["CONDITION_SUCCESS"], None)
    
    def update_info(self, system_pkg):
        return (system_pkg["CONDITION_SUCCESS"], None)

class extra_task_template(default_task_template):
    def __init__(self):
        super().__init__() #继承父类
        self.create_date = ""
        self.version = "0" # 用字符串表示
        self.type = "Extra_Template"
        self.date = ""
        self.attribute = ""
        self.content = ""
        self.comment = ""
    
    def update(self, info_dict):
        super().update(info_dict) # 保留原始方式
    
    def backup(self):
        return None