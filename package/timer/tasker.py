from default_class import extra_tasker_template
from .class_func import timer_tasker_func
from .interface import timer_interface
from .update_info import timer_update_info

class timer_tasker(extra_tasker_template):
    version = "timer"
    introduction = "timer类Tasker"
    def __init__(self):
        super().__init__() # 继承父类
        self.function_list.append(timer_tasker_func())
        self.description = ""
        self.timer_task_df_attribute = ""
        self.timer_task_prefix = ""
        self.timer_task_df_content = ""
    
    def interface(self, system_pkg): # 仅有一种，不可修改
        if self.create_date == "": # 如果create_date为空（未补充过Tasker信息）
            return_tuple = self.update_info(system_pkg)
            if self.create_date == "": return return_tuple # 如果未补充完信息
        
        system_pkg["head_msg"](self.tasker_label)
        
        return_tuple = timer_interface(self, system_pkg)
        return return_tuple
    
    def update_info(self, system_pkg): # 仅有一种，不可修改
        return_tuple = timer_update_info(self, system_pkg)
        return return_tuple
    
    def backup_list(self):
        return_list = super().backup_list()
        return_list += [self.timer_task_df_attribute, self.timer_task_prefix, self.timer_task_df_content]
        return return_list
    
    def build(self, build_list: list, system_pkg: dict):
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
            try:
                task_type, task_version = task_pair_list[pair_index], task_pair_list[pair_index + 1]
            except IndexError: #备份文件无task模板数据
                return False
            for index, task_template in enumerate(system_pkg["ex_task_template_list"]):
                task = task_template()
                if (task_type == task.type) and (task_version == task.version):
                    self.task_template.append(task_template)
        self.description = build_list[6]
        # 专用于timer类task（供class_func读取）
        self.timer_task_df_attribute = build_list[7]
        self.timer_task_prefix = build_list[8]
        self.timer_task_df_content = build_list[9]
        return None