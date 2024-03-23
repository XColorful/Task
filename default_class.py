# tasker.interface()--------+--------+--------+--------+--------+--------+--------+--------+ Begin
from function import convert_to_int, table_class_func

def interface_info(system_pkg, show_msg = True):
    interface_label = "default_interface"
    interface_version = "1.0"
    interface_type = "Default_Template"
    info_list = [interface_label, interface_version, interface_type]
    if show_msg == True:
        table_list=[]
        heading = ["interface标签", "interface版本", "interface类型"]
        table_list.append(heading)
        table_list.append(info_list)
        system_pkg["table_msg"](table_list)
    return info_list

def interface_help(system_pkg):
    system_pkg["tips_msg"]("以\"/\"开头强制识别为指令")
    system_pkg["tips_msg"]("以\"+\"开头强制执行指令search，输入作为参数")
    system_pkg["tips_msg"]("用空格分隔指令与内容")
    system_pkg["tips_msg"]("输入\"/info\"执行interface内置info功能")

def default_interface(tasker, system_pkg): # tasker -> tasker
    """输入时默认执行search
    
    """
    system_pkg["tips_msg"]("输入\"/info\"获取更多信息")
    show_task = True
    while True:
        # 显示最后8项task
        if show_task == True:
            system_pkg["normal_msg"](f"--------{tasker.tasker_label}--------")
            MAX_INDEX_TASK_LIST = len(tasker.task_list) - 1 # task_list最大索引
            show_task_list = tasker.task_list[-8:]
            show_index = MAX_INDEX_TASK_LIST - len(show_task_list) + 1
            for task in show_task_list:
                system_pkg["normal_msg"](f"{show_index}|{task}")
                show_index += 1
        # 查看是否有可用的class_func
        function_list = tasker.function_list
        if function_list == []: system_pkg["system_msg"]("无可用的class_func")
        # 用户输入
        user_input = system_pkg["normal_input"](f"{tasker.tasker_label}")
        # 输入类型预筛选
        if user_input == system_pkg["EXIT"]: return (system_pkg["CONDITION_SUCCESS"], f"{tasker.tasker_label}.interface界面")
        if user_input == "":
            show_task = False
            continue
        if user_input == "/info":
            interface_info(system_pkg)
            table_class_func(function_list, system_pkg)
            interface_help(system_pkg)
            continue
        # 判断指令类型
        cmd_list = user_input.split(" ", 1)
        if cmd_list[0] == " ":
            system_pkg["system_msg"]("输入不能以空格开头")
            system_pkg["tips_msg"]("输入\"/info\"获取更多信息")
            continue
        if user_input[0] == "/": cmd_list = user_input[1:].split(" ", 1)
        elif user_input[0] == "+": cmd_list = ["search", user_input[1:]]
        cmd = cmd_list[0]
        # 查找可用指令
        default_function = False
        available_func_index = []
        for class_func_index in range(0, len(function_list)):
            for function in function_list[class_func_index].function_list:
                if cmd == function:
                    available_func_index.append(class_func_index)
                if function == "search": # 本interface默认执行的功能
                    default_function = True
                    default_proceed_function = function_list[class_func_index]
        available_func_index_len = len(available_func_index)
        # 选择指令
        if available_func_index_len == 1: # 仅有一个可用指令
            proceed_function = function_list[available_func_index[0]]
        elif available_func_index_len == 0: # 没有找到指令
            # 尝试识别为索引
            convert_result = convert_to_int(cmd)
            if convert_result != None: # 执行搜索，参数为int索引
                # 执行默认function
                if default_function == True:
                    cmd_list = ["search", convert_result]
                    default_proceed_function.proceed(cmd_list, tasker, system_pkg)
                    show_task = False
                continue
            else: # 既不为可用指令，又不为非负索引
                system_pkg["system_msg"](f"没有可用的指令\"{cmd}\"")
                system_pkg["tips_msg"]("输入\"/info\"获取更多信息")
                # 执行默认function
                if default_function == True:
                    cmd_list = ["search", user_input]
                    default_proceed_function.proceed(cmd_list, tasker, system_pkg)
                    show_task = False
                continue
        else: # 有多个可用指令
            show_function_list = []
            for index in available_func_index:
                show_function_list.append(function_list[index])
            table_class_func(show_function_list, system_pkg)
            user_input = system_pkg["normal_input"]("输入索引")
            convert_result = convert_to_int(user_input)
            if convert_result != None:
                if 0 <= convert_result < len(show_function_list):
                    proceed_function = function_list[convert_result]
                else:
                    system_pkg["system_msg"](f"索引\"{user_input}\"不存在"); continue
        # 执行指令
        proceed_function.proceed(cmd_list, tasker, system_pkg)
        show_task = True
# tasker.interface()--------+--------+--------+--------+--------+--------+--------+--------+ End


class default_tasker_template():
    version = "0" # 用数字表示
    type = "Default_Template"
    def __init__(self):
        self.tasker_label = ""
        self.description = ""
        self.function_list = []
        self.create_date = ""
        self.task_list = []
        self.task_template = []
    
    def interface(self, system_pkg):
        """默认的interface"""
        return default_interface(self, system_pkg)
    
    def update_info(self, system_pkg):
        return (system_pkg["CONDITION_SUCCESS"], None)
    
    def backup_list(self):
        function_list = []
        for func in self.function_list:
            function_list.append([func.label, func.version, func.type])
        task_template_list = []
        for task_template in self.task_template:
            task = task_template()
            task_template_list.append([task.type, task.version])
        return [self.type, self.version, self.tasker_label, self.create_date, function_list, task_template_list, self.description]
    
    def build(self, build_list:list, system_pkg:dict):
        self.tasker_label = build_list[2]
        self.create_date = build_list[3]
        # 添加class_func
        function_pair_list = build_list[4].split(" ")
        for pair_index in range(0, len(function_pair_list), 3):
            func_label, func_version, func_type = function_pair_list[pair_index],function_pair_list[pair_index + 1], function_pair_list[pair_index + 2]
            for index in range(len(system_pkg["class_func_list"])):
                func = system_pkg["class_func_list"][index]()
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
            for index in range(len(system_pkg["df_task_template_list"])):
                task = system_pkg["df_task_template_list"][index]()
                if (task_type == task.type) and (task_version == task.version):
                    self.task_template.append(system_pkg["df_task_template_list"][index])
        self.description = build_list[6]
        return None

class default_task_template():
    version = "0"
    type = "Default_Template"
    def __init__(self):
        self.create_date = ""
        self.date = ""
        self.attribute = ""
        self.content = ""
        self.comment = ""
    
    def update(self, info_dict:dict, system_pkg:dict):
        """用于在默认class_func中new(), reload()一次性补充所有内容
        
        字典包含self.create_date, self.date, self.attribute, self.content, self.comment"""
        try: create_date, date, attribute, content, comment = info_dict["create_date"], info_dict["date"], info_dict["attribute"], info_dict["content"], info_dict["comment"]
        except KeyError:
            system_pkg["system_msg"]("更新task失败，列表[create_date, date, attribute, content, comment]读取失败")
            return None
        self.create_date = create_date
        self.date = date
        self.attribute = attribute
        self.content = content
        self.comment = comment
    
    def backup(self):
        return f"{self.type}||||{self.version}||||{self.create_date}||||{self.date}||||{self.attribute}||||{self.content}||||{self.comment}"
    
    def backup_list(self):
        return [self.type, self.version, self.create_date, self.date, self.attribute, self.content, self.comment]
    
    def build(self, build_list:list):
        self.create_date = build_list[2]
        self.date = build_list[3]
        self.attribute = build_list[4]
        self.content = build_list[5]
        self.comment = build_list[6]

class extra_tasker_template(default_tasker_template):
    version = "0" # 用字符串表示
    type = "Extra_Template"
    def __init__(self):
        super().__init__() #继承父类
        self.description = ""

    def interface(self, system_pkg):
        return super().interface(system_pkg)
    
    def update_info(self, system_pkg):
        return (system_pkg["CONDITION_SUCCESS"], None)
    
    def backup_list(self):
        return super().backup_list()
    
    def build(self):
        return None

class extra_task_template(default_task_template):
    version = "" # 用字符串表示，不能为数字（应不能被float()转换）
    type = "Extra_Template"
    def __init__(self):
        super().__init__() #继承父类
    
    def update(self, info_dict:dict):
        return None
    
    def backup(self):
        return None
    
    def backup_list(self):
        return []
    
    def build(self, build_list:list):
        pass