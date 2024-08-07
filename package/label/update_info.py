from .function import YYYY_MM_DD, input_tasker_attr_input_map, input_tasker_convenient_input

def label_update_info(self, system_pkg) -> tuple:
    block_list = system_pkg["BLOCK_LIST"] + [" "]
    
    if self.tasker_label == "": # 添加Tasker标签
        return_tuple = system_pkg["strict_input"]("输入Tasker标签", block_list, system_pkg)
        if return_tuple[0] == False: return (system_pkg["CONDITION_SUCCESS"], "取消输入Tasker标签")
        self.tasker_label = return_tuple[1]
    
    if self.description == "": # 添加Tasker描述
        return_tuple = system_pkg["strict_input"]("输入Tasker描述", block_list, system_pkg)
        if return_tuple[0] == False: return (system_pkg["CONDITION_SUCCESS"], "取消输入Tasker描述")
        self.description = return_tuple[1]
    
    if self.task_template == []:
        # 筛选符合版本的task模板类型
        for task_template in system_pkg["ex_task_template_list"]:
            if task_template.version != self.version: continue
            self.task_template.append(task_template)
        # 确认是否含有timer模板
        if self.task_template == []: # 无可用task模板类型
            system_pkg["system_msg"](f"没有可用的task模板类型（{self.type}）")
            return (system_pkg["CONDITION_SUCCESS"], f"无可用task模板类型（{self.type}）")
    
    
    if self.attr_input_map == {}:
        system_pkg["tips_msg"]("可在之后使用\"config\"命令更改")
        input_tasker_attr_input_map(self, system_pkg)
    
    input_tasker_convenient_input(self, system_pkg)
    
    
    if self.create_date == "": # 更新创建日期
        self.create_date = YYYY_MM_DD()
    
    return (system_pkg["CONDITION_SUCCESS"], "更新Tasker信息")