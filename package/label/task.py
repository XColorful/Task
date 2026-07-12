from default_class import extra_task_template
from .function import is_valid_input

class label_task(extra_task_template):
    version = "label"
    def __init__(self):
        super().__init__() # 继承父类
        # extra attributes here
        self.create_date = "" # YYYY_MM_DD
        self.content = ""
        self.label_list = [] # [ [attr, label], [attr, label], ... ]
        
    def __str__(self):
        return f"{self.create_date}|{self.content}|label：{len(self.label_list)}"
    
    def check_label(self, label_input) -> bool:
        try:
            if (len(label_input.split("|||", 1)) == 2) and ("|||" in label_input):
                return True
            else:
                return False
        except:
            return False
        
    def make_label_pair(self, label_input):
        attr, label = label_input.split("|||", 1)
        label_pair = [attr, label]
        return label_pair
    
    def delete_label(self, label_index) -> bool:
        try:
            del self.label_list[label_index]
            return True
        except IndexError: pass
        return False
    
    def edit_label(self, label_index, label_input) -> bool:
        if self.check_label(label_input) == False:
            return False
        
        try:
            label_pair = self.make_label_pair(label_input)
            self.label_list[label_index] = label_pair
        except IndexError:
            return False
        
        return True
    
    def add_label(self, label_input):
        label_pair = self.make_label_pair(label_input)
        self.label_list.append(label_pair)
        
    
    def update(self, info_dict:dict, system_pkg:dict):
        """更新task所有属性
        
        info_dict格式：
        {"create_date":str, "self.content":str, "label_list":list[str]}"""
        self.create_date = info_dict["create_date"]
        
        if info_dict["content"] != "":
            self.content = info_dict["content"]
        else:
            system_pkg["system_msg"]("内容不能为空，取消更新task内容")
            return None
        
        for label_input in info_dict["label_list"]:
            if self.check_label(label_input) == True:
                continue
            else:
                system_pkg["system_msg"]("label_list格式有误，取消更新task标签列表")
        # 重置label_list
        self.label_list = []
        for label_input in info_dict["label_list"]:
            self.add_label(label_input)
        
        return None
    
    def backup_list(self) -> tuple:
        """用于创建build_list"""
        backup_dict_list = []
        
        backup_dict_list.append(self.type)
        backup_dict_list.append(self.version)
        backup_dict_list.append(self.create_date)
        backup_dict_list.append(self.content)
        
        for label_pair in self.label_list:
            label_input = f"{label_pair[0]}|||{label_pair[1]}"
            backup_dict_list.append(label_input)
        
        return backup_dict_list
    
    def build(self, build_list: list) -> bool:
        """build_list格式：
        ["self.type", "self.version", "self.create_date", "self.content", "attr|||content", "attr|||content", ...]"""
        for i in build_list:
            if not is_valid_input(i): return False
        
        try:
            self.create_date = build_list[2]
            self.content = build_list[3]
        except IndexError:
            return False
        
        for i in range(4, len(build_list) ):
            label_input = build_list[i]
            if self.check_label(label_input) == False:
                return False
            self.add_label(label_input)
        
        return True