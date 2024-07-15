from os import getcwd
from default_method import default_method_template
from .function import YYYY_MM_DD, input_is_YYYY_MM_DD, input_is_YYYY_MM_DD_HH_SS, convert_to_int, show_task_info, check_timer_u, check_timer_t, check_timer_all

def get_date_input(system_pkg) -> str | None:
    current_date = YYYY_MM_DD()
    user_input = system_pkg["normal_input"](f"输入日期（默认{current_date}）")
    if user_input == system_pkg["EXIT"]:
        return None
    elif user_input == "":
        return current_date
    else:
        return user_input
            

def select_YYYY_MM_DD(user_input:str, system_pkg) -> str | None:
    if user_input == "":
        user_input = get_date_input(system_pkg)
    if user_input == system_pkg["EXIT"]: return None
    
    if input_is_YYYY_MM_DD(user_input):
        return user_input
    else:
        system_pkg["system_pkg"](f"日期{user_input}格式不符")
        return None

def get_split_parameter(user_input) -> str:
    try:
        return user_input.split(" ")[1]
    except IndexError:
        return ""

def get_split_parameters(user_input) -> list[str]:
    try:
        return user_input.split(" ")
    except IndexError:
        return []

def show_check_func_info(system_pkg):
    system_pkg["table_msg"]([["序号", "类型", "描述"],
                                ["1", "unfinished", "给定日期下未完成的timer_task"],
                                ["2", "today", "给定日期内持续timer_task"],
                                ["3", "all", "在给定日期内持续的tiemr_task"]], heading = True)

def get_check_func(user_input:str, system_pkg):
    """返回值为function或None"""
    check_func_list = [check_timer_u, check_timer_t, check_timer_all]
    
    if user_input == "":
        show_check_func_info(system_pkg)
        system_pkg["tips_msg"]("输入序号或任意字母")
        user_input = system_pkg["normal_input"]("选择判断类型")
    
    if user_input == system_pkg["EXIT"]: return None
    else:
        # 索引
        try:
            index = convert_to_int(user_input)
            if index != None:
                if index >= 0: index -= 1
                return check_func_list[index]
        except IndexError:
            system_pkg["system_msg"](f"索引{user_input}不符")
            return None
        # 字符匹配
        for index, func_str in enumerate(["unfinished", "today", "all"]):
            if user_input in func_str:
                return check_func_list[index]
        return None

def get_date_parameter(parameter_list:list[str]) -> str:
    try:
        if parameter_list [0] == "" and parameter_list[1] != "":
            return YYYY_MM_DD()
        return parameter_list[0]
    except IndexError:
        return ""

def get_func_parameter(parameter_list:list[str]) -> str:
    try:
        return parameter_list[1]
    except IndexError:
        return ""

def get_timer_tasker_index(tasker_list) -> list[int]:
    index_list = []
    for index, tasker in enumerate(tasker_list):
        if tasker.version == "timer":
            index_list.append(index)
    return index_list

def get_match_func_timer_index_list(tasker_list, timer_tasker_index, date_YYYY_MM_DD, check_func) -> list[list]:
    """返回列表格式：
    
    [ [tasker_index, [task_index, task_index] ],
    
    [ [tasker_index, [task_index, task_index] ] ] ]"""
    return_list = []
    for tasker_index in timer_tasker_index:
        return_list.append([tasker_index, []])
        
        # 检查timer_task是否匹配
        for task_index, timer_task in enumerate(tasker_list[tasker_index].task_list):
            if check_func(timer_task, date_YYYY_MM_DD):
                return_list[-1][1].append(task_index)
    return return_list

def show_matched_result(matched_index_list, tasker_list, system_pkg):
    display_index = 1
    
    for tasker_index, task_index_list in matched_index_list:
        tasker = tasker_list[tasker_index]
        
        if task_index_list != []:
            # tasker名称
            system_pkg["head_msg"](f"{tasker.tasker_label}")
            # task
            for task_index in task_index_list:
                show_task_info(tasker.task_list[task_index], str(display_index), system_pkg)
                display_index += 1
        else:
            continue

def write_matched_result(matched_index_list, tasker_list, system_pkg):
    working_dir = getcwd()
    timer_txt_dir = working_dir + "/timer.txt"
    with open(timer_txt_dir, "w", encoding = "utf-8") as f:
        total_count = 0
        for tasker_index, task_index_list in matched_index_list:
            tasker = tasker_list[tasker_index]
            if task_index_list != []:
                display_index = 1
                f.write(f"+-------+-------+-------{tasker.tasker_label}-------+-------+-------+\n")
                for task_index in task_index_list:
                    task = tasker.task_list[task_index]
                    
                    # start_time
                    if input_is_YYYY_MM_DD_HH_SS(task.start_time):
                        start_time = task.start_time
                    else:
                        start_time = "start_time Error"
                    
                    # end_time
                    if task.end_time == "":
                        end_time = " " * 16
                    elif input_is_YYYY_MM_DD_HH_SS(task.end_time):
                        end_time = task.end_time
                    else:
                        end_time = "end_time Error  "
                    # comment
                    comment = "" if task.comment == "" else f"|{task.comment}"
                    
                    f.write(f"\t[{display_index}]|{start_time}|{end_time}|<{task.attribute}>|{task.content}{comment}\n")
                    display_index += 1
                    total_count += 1
        f.write("/end\n")
        f.write(f"已保存至\".\\timer.txt\"\n")
        f.write(f"共计{total_count}项\n")
        f.write(f"当前工作目录{working_dir}\n")
        f.write(f"完整路径{timer_txt_dir}\n")
        f.write(f"方法timer_task_method，版本timer，使用指令timer\n")
        system_pkg["system_msg"](f"已保存至\".\\timer.txt\"")
        system_pkg["body_msg"]([f"共计{total_count}项",
                                f"当前工作目录{working_dir}",
                                f"完整路径{timer_txt_dir}",
                                f"方法timer_task_method，版本timer，使用指令timer"])

class timer_task_method(default_method_template):
    def __init__(self):
        super().__init__() # 继承父类
        self.label = "timer_task_method"
        self.version = "timer"
        self.method_list = ["timer"]
    
    def method_info(self):
        return super().method_info()
    
    def analyze(self, cmd_list:list, tasker_list:list, system_pkg:dict): # 分析是否存在可用指令，返回(bool，[标签，版本，类型])
        return super().analyze(cmd_list, tasker_list, system_pkg)

    def proceed(self, cmd_list:list, tasker_list:list, system_pkg:dict):
        return super().proceed(cmd_list, tasker_list, system_pkg)
    
    def timer(self, cmd_parameter:str, tasker_list:list, system_pkg:dict) -> tuple:
        """第一参数为YYYY_MM_DD，第二参数为n, t, a"""
        timer_tasker_index = get_timer_tasker_index(tasker_list)
        if timer_tasker_index == []:
            system_pkg["system_msg"]("没有timer类tasker供操作")
            return (system_pkg["CONDITION_SUCCESS"], "无可执行timer操作的tasker")
        
        parameter_list = get_split_parameters(cmd_parameter)
        date_parameter = get_date_parameter(parameter_list)
        func_parameter = get_func_parameter(parameter_list)
        
        date_YYYY_MM_DD = select_YYYY_MM_DD(date_parameter, system_pkg)
        if date_YYYY_MM_DD == None:
            return (system_pkg["CONDITION_SUCCESS"], "取消选择timer操作日期")
        
        check_func = get_check_func(func_parameter, system_pkg)
        if check_func == None:
            return (system_pkg["CONDITION_SUCCESS"], "取消选择timer操作功能")
        
        matched_index_list = get_match_func_timer_index_list(tasker_list, timer_tasker_index, date_YYYY_MM_DD, check_func)
        
        show_matched_result(matched_index_list, tasker_list, system_pkg)
        write_matched_result(matched_index_list, tasker_list, system_pkg)
        
        return (system_pkg["CONDITION_SUCCESS"], "")