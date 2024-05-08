from datetime import datetime
from default_class_func import extra_tasker_func_template
from .function import convert_to_int, YYYY_MM_DD, YYYY_MM_DD_HH_MM, get_not_end_timer_index, show_unfinished_timer

def check_tasker(tasker, system_pkg) -> None:
    for task_template in tasker.task_template:
        if task_template.version == "timer":
            return True
    system_pkg["system_msg"](f"Tasker（{tasker.tasker_label}）缺少timer类task")
    return False
def make_timer_template(tasker) -> object | None:
    """此函数默认tasker.task_template含有timer类task"""
    for task_template in tasker.task_template:
        if task_template.version == "timer":
            return task_template()
def create_timer_template(tasker, system_pkg) -> object | None:
    if not check_tasker(tasker, system_pkg):
        return None
    timer_task = make_timer_template(tasker)
    return timer_task
def get_tasker_config(tasker) -> dict:
    config_dict = {"timer_task_df_attribute":"",
                   "timer_task_prefix":"",
                   "timer_task_df_content":""}
    try:
        config_dict["timer_task_df_attribute"] = tasker.timer_task_df_attribute
        config_dict["timer_task_prefix"] = tasker.timer_task_prefix
        config_dict["timer_task_df_content"] = tasker.timer_task_df_content
    except AttributeError: pass
    return config_dict
def check_YYYY_MM_DD_HH_SS_format(date_str) -> bool:
    try:
        datetime.strptime(date_str, '%Y_%m_%d-%H:%M')
        return True
    except ValueError:
        return False
def get_YYYY_MM_DD_HH_SS_input(adjuct_str, system_pkg, allow_empty = False) -> str | bool:
    while True:
        current_YYYY_MM_DD_HH_SS = YYYY_MM_DD_HH_MM()
        input_conditon, user_input = system_pkg["block_input"](f"{adjuct_str}日期({current_YYYY_MM_DD_HH_SS})")
        # 检查输入
        if input_conditon == False: return False # EXIT
        elif input_conditon == None:
            if allow_empty == False:
                return current_YYYY_MM_DD_HH_SS # ""
            else: return ""
        # 检查日期是否存在
        if check_YYYY_MM_DD_HH_SS_format(user_input):
            return user_input
        else:
            system_pkg["normal_msg"](f"日期格式\"{user_input[1]}\"错误")
            system_pkg["tips_msg"]("格式：YYYY_MM_DD-HH:SS")
            continue
def get_start_time_input(system_pkg):
    return get_YYYY_MM_DD_HH_SS_input("start", system_pkg)
def get_attribute_input(system_pkg) -> str | bool:
    input_condition, user_input = system_pkg["block_input"]("属性(可选)")
    if input_condition == False: return False # EXIT
    elif input_condition == None: return "N/A" # ""
    return user_input
def get_content_input(system_pkg) -> str | bool:
    system_pkg["tips_msg"]("输入\"n\"即可使用默认配置的输入")
    input_condition, user_input = system_pkg["strict_input"]("内容")
    if input_condition == False: return False
    return user_input
def get_comment_input(system_pkg) -> str | bool:
    input_condition, user_input = system_pkg["block_input"]("注释(可选)")
    if input_condition == False: return False # EXIT
    elif input_condition == None: return "" # ""
    return user_input
def get_end_time_input(system_pkg):
    return get_YYYY_MM_DD_HH_SS_input("end", system_pkg, allow_empty=True)
def input_timer_task_info(tasker_config, system_pkg) -> list[str] | bool:
    input_list = []
    for input_func in [get_start_time_input, # start_time
                       get_attribute_input, # attribute
                       get_content_input, # content
                       get_comment_input, # comment
                       get_end_time_input]: # end_time
        user_input = input_func(system_pkg)
        if user_input == False: return False
        input_list.append(user_input)
    current_date = YYYY_MM_DD()
    input_list.append(current_date) # create_date
    build_list = [system_pkg["TYPE_EXTRA_TASKER"], "timer"] + [""] * 6
    build_list[2] = current_date # create_date
    build_list[3] = input_list[0] # start_time
    build_list[4] = input_list[4] # end_time
    # attribute
    timer_task_df_attribute = tasker_config["timer_task_df_attribute"]
    build_list[5] = input_list[1] if (input_list[1] != "N/A") else timer_task_df_attribute
    # content
    timer_task_prefix = tasker_config["timer_task_prefix"]
    timer_task_df_content = tasker_config["timer_task_df_content"]
    if input_list[2] == "n":
        if timer_task_df_content != "":
            build_list[6] = timer_task_df_content
        else:
            system_pkg["system_msg"]("Tasker未配置默认timer类task内容(保留原输入)")
    build_list[6] = timer_task_prefix + build_list[6]
    build_list[7] = input_list[3] # comment
    return build_list

def show_task_info(timer_task, task_index, system_pkg):
    system_pkg["normal_msg"](f"[{task_index}]|<{timer_task.attribute}>|{timer_task.content}")
    system_pkg["body_msg"]([f"start_time:{timer_task.start_time}",
                            f"end_time:{timer_task.end_time}",
                            f"comment:{timer_task.comment}"])

def get_unfinished_timer_index(parameter, tasker, system_pkg) -> int | bool:
    user_input = parameter
    if user_input == "":
        # 显示未完成的timer类task
        not_end_timer_index = get_not_end_timer_index(tasker)
        if not_end_timer_index == []:
            system_pkg["system_msg"]("无未完成的timer类task")
            return None
        else:
            show_unfinished_timer(not_end_timer_index, tasker, system_pkg)
        user_input = system_pkg["normal_input"](f"输入指示索引")
    # EXIT
    if user_input == system_pkg["EXIT"]: return False
    
    convert_condition = convert_to_int(user_input)
    if convert_condition == None:
        system_pkg["system_msg"](f"指示索引\"{user_input}\"格式错误")
        return None
    select_index = convert_condition
    # 判断索引是否符合
    try:
        return not_end_timer_index[select_index]
    except IndexError:
        system_pkg["system_msg"](f"指示索引\"{select_index}\"不符合")
        return False


def show_set_config_guide(system_pkg):
    system_pkg["tips_msg"]("输入<Enter>跳过设置")
    system_pkg["tips_msg"]("输入\"n\"清除原先预设")
def set_timer_task_df_attribute(tasker, system_pkg) -> bool | None:
    system_pkg["normal_msg"](f"原timer默认属性：{tasker.timer_task_df_attribute}")
    input_condition, user_input = system_pkg["block_input"]("设置timer默认属性")

    if input_condition == False: return False
    elif user_input == "n":
        tasker.timer_task_df_attribute = ""
        system_pkg["system_msg"]("已清除默认timer默认属性")
    elif input_condition == None: return None
    else:
        tasker.timer_task_df_attribute = user_input
        system_pkg["system_msg"](f"默认timer属性更改为{tasker.timer_task_df_attribute}")
    return None
def set_timer_task_prefix(tasker, system_pkg):
    system_pkg["normal_msg"](f"原timer默认内容前缀：{tasker.timer_task_prefix}")
    input_condition, user_input = system_pkg["block_input"]("设置timer默认内容前缀")
    
    if input_condition == False: return False
    elif user_input == "n":
        tasker.timer_task_prefix = ""
        system_pkg["system_msg"]("已清除timer默认内容前缀")
    elif input_condition == None: return None
    else:
        tasker.timer_task_prefix = user_input
        system_pkg["system_msg"](f"默认timer默认内容前缀更改为{tasker.timer_task_prefix}")
    return None
def set_timer_task_df_content(tasker, system_pkg):
    system_pkg["normal_msg"](f"原timer默认内容：{tasker.timer_task_df_content}")
    input_condition, user_input = system_pkg["block_input"]("设置timer默认内容")
    
    if input_condition == False: return False
    elif user_input == "n":
        tasker.timer_task_df_content = ""
        system_pkg["system_msg"]("已清除timer默认内容")
    elif input_condition == None: return None
    else:
        tasker.timer_task_df_content = user_input
        system_pkg["system_msg"](f"默认timer默认内容更改为{tasker.timer_task_df_content}")
    return None


class timer_tasker_func(extra_tasker_func_template):
    def __init__(self):
        super().__init__()
        self.label = "timer_tasker_func"
        self.version = "timer"
        self.function_list = ["new", "edit", "config", "delete", "search", "end"]
        self.create_date = YYYY_MM_DD()
    
    def __str__(self):
        return super().__str__()
    
    def get_info(self):
        return super().get_info()
    
    def proceed(self, cmd_list:list, tasker, system_pkg:dict):
        super().proceed(cmd_list, tasker, system_pkg)
    
    def new(self, parameter, tasker, system_pkg) -> None:
        """创建timer类task，暂无可用参数"""
        # 创建timer类task
        timer_task = create_timer_template(tasker, system_pkg)
        if timer_task == None: return None
        
        # 补充task信息
        tasker_config = get_tasker_config(tasker)
        build_list = input_timer_task_info(tasker_config, system_pkg)
        if build_list != False:
            timer_task.build(build_list)
        # 显示创建的task
        show_task_info(timer_task, len(tasker.task_list), system_pkg)
        tasker.task_list.append(timer_task)
        return None

    def edit(self, parameter, tasker, system_pkg) -> None:
        pass

    def config(self, parameter, tasker, system_pkg) -> None:
        show_set_config_guide(system_pkg)
        for func in [set_timer_task_df_attribute,
                     set_timer_task_prefix,
                     set_timer_task_df_content]:
            if func(tasker, system_pkg) == False: return None

    def delete(self, parameter, tasker, system_pkg) -> None:
        pass

    def search(self, parameter, tasker, system_pkg) -> None:
        pass

    def end(self, parameter, tasker, system_pkg) -> None:
        """输入参数为指示索引（第几个未完成的timer类task）"""
        unfinished_timer_index = get_unfinished_timer_index(parameter, tasker, system_pkg)
        if unfinished_timer_index == None:
            return None
        current_YYYY_MM_DD_HH_MM = YYYY_MM_DD_HH_MM()
        tasker.task_list[unfinished_timer_index].end_time = current_YYYY_MM_DD_HH_MM
        return None