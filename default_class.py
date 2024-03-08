CONDITION_SUCCESS = True # 正常运行

class default_container_template():
    def __init__(self):
        self.container_label = ""
        self.description = ""
        self.function_list = []
        self.create_date = ""
        self.version = "0" # 用数字表示
        self.type = "Default_Template"
        self.task_list = []
        self.task_template = []
    
    def interface(self, system_pkg):
        return (CONDITION_SUCCESS, None)
    
    def update_info(self, system_pkg):
        return (CONDITION_SUCCESS, None)
    
    def backup_list(self):
        function_list = []
        for func in self.function_list:
            function_list.append([func.label, func.version, func.type])
        task_template_list = []
        for task_template in self.task_template:
            task = task_template()
            task_template_list.append([task.type, task.version])
        return [self.type, self.version, self.container_label, self.create_date, function_list, task_template_list, self.description]
    
    def build(self, build_list:list, system_pkg:dict):
        self.container_label = build_list[2]
        self.create_date = build_list[3]
        # 添加class_func
        function_pair_list = build_list[4].split(" ")
        for pair_index in range(0, len(function_pair_list), 3):
            func_label, func_version, func_type = function_pair_list[pair_index],function_pair_list[pair_index + 1], function_pair_list[pair_index + 2]
            for index in range(len(system_pkg["class_func"])):
                func = system_pkg["class_func"][index]()
                info_list = func.get_info()
                if (func_label == info_list[0]) and (func_version == info_list[1]) and (func_type == info_list[2]):
                    # 去重判断
                    same = False
                    for i in self.function_list:
                        if (func_label == i.label) and (func_version == i.version) and (func.type == i.type):
                            same = True
                            break
                    if same == False: self.function_list.append(func)
        # 添加task模板
        task_pair_list = build_list[5].split(" ")
        for pair_index in range(0, len(task_pair_list), 2):
            task_type, task_version = task_pair_list[pair_index], task_pair_list[pair_index + 1]
            for index in range(len(system_pkg["default_task_template_list"])):
                task = system_pkg["default_task_template_list"][index]()
                if (task_type == task.type) and (task_version == task.version):
                    self.task_template.append(system_pkg["default_task_template_list"][index])
        self.description = build_list[6]
        return None

class default_task_template():
    def __init__(self):
        self.create_date = ""
        self.version = "0"
        self.type = "Default_Template"
        self.date = ""
        self.attribute = ""
        self.content = ""
        self.comment = ""
    
    def update(self, info_dict):
        """用于在new和reload时一次性补充所有内容
        
        字典包含self.create_date, self.date, self.attribute, self.content, self.comment"""
        self.create_date = info_dict["create_date"]
        self.date = info_dict["date"]
        self.attribute = info_dict["attribute"]
        self.content = info_dict["content"]
        self.comment = info_dict["comment"]
    
    def backup(self):
        return None
    
    def backup_list(self):
        return [self.type, self.version, self.create_date, self.date, self.attribute, self.content, self.comment]
    
    def build(self, build_list:list):
        self.create_date = build_list[2]
        self.date = build_list[3]
        self.attribute = build_list[4]
        self.content = build_list[5]
        self.comment = build_list[6]