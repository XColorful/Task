from default_class import extra_task_template

class account_task(extra_task_template):
    def __init__(self):
        super().__init__() # 继承父类
        self.version = "account"
        self.account_label = ""
        
    
    def __str__(self):
        return f"{self.date}|{self.attribute}|{self.content}"
    
    def update(self, info_dict:dict, system_pkg:dict):
        # 必要内容
        try:
            create_date, account_type, label, password = info_dict["create_date", "account_type", "label", "password"]
        except KeyError:
            system_pkg["system_msg"]("更新task失败，列表[create_date, account_type, label, password]读取失败")
            return None
        self.create_date = create_date
        self.account_type = account_type
        self.label = label
        self.password = password
        # 可选内容
        for info_key in self.info_key:
            try:
                self.info[info_key] = info_dict[info_key]
                continue
            except KeyError:
                continue
        return None
    
    def backup(self):
        if self.create_date == "": return "" # 未创建的task不返回备份
        return f"{self.type}||||{self.version}||||{self.create_date}||||{self.date}||||{self.attribute}||||{self.content}||||{self.comment}"
    
    def backup_list(self):
        # 
        return []
    
    def build(self, build_list: list):
        # 
        return None