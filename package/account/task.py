from default_class import extra_task_template

class account_task(extra_task_template):
    def __init__(self):
        super().__init__() # 继承父类
        self.version = "account"
        self.create_date = ""
        self.last_date = ""
        self.account_type = ""
        self.label = "" # 用户起的标签，默认设定为account_type
        self.password = "" # 密码可以为空
        self.dict = {"description":[],
                     "login_name":[],
                     "verified_phone":[],
                     "verified_email":[],
                     "linked_account":[],
                     "secure_question":[],
                     "other_info":[],
                     "password_history":[]} # 值均为str_list
        
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
    
    def backup_list(self):
        backup_dict_list = []
        for key, value in self.dict.items(): # 遍历account信息, key -> str, value -> list[str]
            if value != []: # 仅备份非空信息
                # 防御式检查
                for item in value:
                    if "|||" in item:
                        return False
                backup_str = "|||".join([key] + value)
                backup_dict_list.append(backup_str)
                # 格式形如 key|||value[0]|||value[1]
        return [self.type, self.version,
                self.create_date, self.last_date, self.account_type, self.label, self.password] \
                + backup_dict_list
    
    def build(self, build_list: list):
        # 固定属性
        self.type = build_list[0]
        self.version = build_list[1]
        self.create_date = build_list[2]
        self.last_date = build_list[3]
        self.account_type = build_list[4]
        self.label = build_list[5]
        self.password = build_list[6]
        # self.dict
        for backup_str in build_list[7:]:
            value_list = backup_str.split("|||")
            try:
                key : str = value_list[0]
                value : list = value_list[1:]
                self.dict[key] = value
            except KeyError:
                return False
        return None