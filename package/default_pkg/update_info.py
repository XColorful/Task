from .function import convert_to_float, YYYY_MM_DD, table_task_template_instance, select_valid_index

def default_update_info(self, system_pkg):
    block_list = system_pkg["BLOCK_LIST"] + [" "]
    
    if self.tasker_label == "": # 添加容器标签
        return_tuple = system_pkg["strict_input"]("输入容器标签", block_list, system_pkg)
        if return_tuple[0] == False: return (system_pkg["CONDITION_SUCCESS"], "取消输入容器标签")
        self.tasker_label = return_tuple[1]
    
    if self.description == "": # 添加容器描述
        return_tuple = system_pkg["strict_input"]("输入容器描述", block_list, system_pkg)
        if return_tuple[0] == False: return (system_pkg["CONDITION_SUCCESS"], "取消输入容器描述")
        self.description = return_tuple[1]
    
    if self.task_template == []:
        system_pkg["system_msg"]("无可用的task模板")
        # 筛选符合版本的task模板类型
        task_template_list = []
        task_instance_list = []
        for task_template in system_pkg["df_task_template_list"]:
            task_instance = task_template()
            if task_instance.type != self.type: continue
            if convert_to_float(str(task_instance.version)) > convert_to_float(str(self.version)): continue # 高版本则不兼容
            task_template_list.append(task_template)
            task_instance_list.append(task_instance)
        # 展示task模板类型
        if task_template_list == []: # 无可用task模板类型
            system_pkg["system_msg"]("没有可用的task模板类型")
            return (system_pkg["CONDITION_SUCCESS"], "无可用task模板类型")
        else: table_task_template_instance(task_instance_list, system_pkg) # 有可用task模板类型
        # 选择需要的task模板
        system_pkg["tips_msg"]("用单个空格分隔索引，输入<Enter>则全选")
        user_input = system_pkg["normal_input"]("输入索引")
        if user_input == system_pkg["EXIT"]: return (system_pkg["CONDITION_SUCCESS"], "取消选择task模板类型")
        select_index_list = select_valid_index(user_input, task_template_list)
        if select_index_list == []: return (system_pkg["CONDITION_SUCCESS"], "无选中task模板类型")
        for index in select_index_list:
            self.task_template.append(task_template_list[index])
    
    if self.create_date == "": # 更新创建日期
        self.create_date = YYYY_MM_DD()
    
    return (system_pkg["CONDITION_SUCCESS"], "更新容器信息")