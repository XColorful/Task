from default_class import extra_tasker_template
from .class_func import label_tasker_func
from .interface import label_interface
from .update_info import label_update_info
from .function import is_valid_input

class label_tasker(extra_tasker_template):
    version = "label"
    introduction = "label类Tasker"
    def __init__(self):
        super().__init__() # 继承父类
        self.function_list.append(label_tasker_func())
        self.create_date = ""
        self.description = ""
        
        self.convenient_input = False
        self.attr_input_map = {} # {"input1": map, "input2": map, ...}
    
    def interface(self, system_pkg):
        return_tuple = label_interface(self, system_pkg)
        return return_tuple
    
    def update_info(self, system_pkg):
        return_tuple = label_update_info(self, system_pkg)
        return return_tuple
    
    def check_attr_map_input(self, attr_map_input) -> bool:
        attr_map_pair = self.make_attr_map(attr_map_input)
        if len(attr_map_pair == 2):
            return True
        else:
            return False
        
    def make_attr_map(self, attr_map_input):
        return attr_map_input.split("|||", 1)
    
    def update_attr_map(self, attr_map_input):
        """label类tasker更改attr_map"""
        attr_map_pair = self.make_attr_map(attr_map_input)
        self.attr_input_map[ attr_map_pair[0] ] = attr_map_pair[1]
        
    def backup_list(self):
        return_list = super().backup_list()
        
        convenient_input_condition = "1" if self.convenient_input == True else "0"
        return_list.append(convenient_input_condition)
        
        attr_map_list = []
        for key, value in self.attr_input_map.items():
            attr_map_list.append(f"{key}|||{value}")
        return_list += attr_map_list

        return return_list
    
    def build(self, build_list: list, system_pkg: dict) -> bool:
        for i in build_list:
            if not is_valid_input(i):
                return False
        
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
        
        # 便捷输入
        if build_list[7] == "1":
            self.convenient_input = True
        elif build_list[7] == "0":
            self.convenient_input = False
        else:
            return False
        
        # label类task属性
        for attr_map_input in build_list[8:]:
            if self.check_attr_map_input(attr_map_input) == True:
                self.update_attr_map(attr_map_input)
            else:
                return False
        
        
        return True