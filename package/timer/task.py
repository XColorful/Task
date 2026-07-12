from default_class import default_task_template, extra_task_template

class timer_task(extra_task_template):
    version = "timer"
    def __init__(self):
        super().__init__() # 继承父类
        self.create_date = "" # YYYY_MM_DD
        self.start_time = "" # YYYY_MM_DD-HH:MM
        self.end_time = "" # YYYY_MM_DD-HH:MM
        self.attribute = ""
        self.content = ""
        self.comment = ""
        
    def __str__(self):
        return f"{self.start_time}|{self.end_time}|{self.attribute}|{self.content}"
    
    def update(self, info_dict:dict, system_pkg:dict):
        try:
            create_date, start_time, end_time, attribute, content, comment = info_dict["create_date", "start_time", "end_time", "attribute", "content", "comment"]
        except KeyError:
            system_pkg["system_msg"]("更新task失败，列表[create_date, start_time, end_time, attribute, content, comment]读取失败")
            return None
        self.create_date = create_date
        self.start_time = start_time
        self.end_time = end_time
        self.attribute = attribute
        self.content = content
        self.comment = comment
        return None
    
    def backup_list(self) -> tuple:
        backup_dict_list = []
        backup_dict_list += [self.type, self.version]
        backup_dict_list += [self.create_date, self.start_time, self.end_time, self.attribute, self.content, self.comment]
        return backup_dict_list
    
    def build(self, build_list: list):
        self.create_date = build_list[2]
        self.start_time, self.end_time, self.attribute, self.content, self.comment = build_list[3], build_list[4], build_list[5], build_list[6], build_list[7]
        return None