from .function import convert_to_int, YYYY_MM_DD, get_not_end_timer_index, show_unfinished_timer
from datetime import datetime, timedelta

def show_recent_timer_task(tasker, system_pkg) -> None:
    recent_task_list = tasker.task_list[-9:]
    if recent_task_list == []: return None
    
    table_list = []
    heading = ["索引", "start_time", "end_time", "属性", "内容", "注释"]
    table_list.append(heading)
    
    start_index = len(tasker.task_list) - len(recent_task_list)
    for timer_task in recent_task_list:
        table_list.append([str(start_index),
                           str(timer_task.start_time),
                           str(timer_task.end_time),
                           str(timer_task.attribute),
                           str(timer_task.content),
                           str(timer_task.comment)])
        start_index += 1
    
    system_pkg["table_msg"](table_list, heading = True)
def interface_pre_show(info_dict, tasker, system_pkg):
    if tasker.function_list == []:
        system_pkg["system_msg"]("无可用的class_func")
    # 显示未完成的timer
    if info_dict["show_not_end_timer"] == True:
        show_unfinished_timer(info_dict["not_end_timer_index"], tasker, system_pkg)
    # 显示最近几项timer类task
    show_recent_timer_task(tasker, system_pkg)
def analyze_input(str_input) -> dict:
    """返回dict{"cmd":str, "parameter":str}"""
    if str_input == "":
        return {"cmd":"", "parameter":""}
    if str_input[0] == "+":
        return {"cmd":"search", "parameter":str_input}
    elif str_input[0] == "/":
        try:
            str_input = str_input[1:]
        except IndexError: return {"cmd":"", "parameter":""}
    
    str_input = str_input.split(" ", 1)
    try:
        parameter = str_input[1]
    except IndexError: parameter = ""
    
    return {"cmd":str_input[0], "parameter":parameter}
def get_interface_input(system_pkg) -> dict | bool:
    while True:
        interface_input = system_pkg["normal_input"]()
        input_dict = analyze_input(interface_input)
        if input_dict["cmd"] == "": continue
        elif input_dict["cmd"] == system_pkg["EXIT"]: return False
        
        return input_dict
def get_cmd_index_list(cmd, tasker):
    cmd_index_list = []
    for index, func in enumerate(tasker.function_list):
        if cmd in func.function_list:
            cmd_index_list.append(index)
    return cmd_index_list
def show_cmd_list(cmd_index_list, tasker, system_pkg) -> list[tuple]:
    """["功能类", "版本", "适用类型", "指令集"]
    
    在输出列表前添加索引，从0开始
    """
    table_list = []
    heading = ["索引", "功能类", "版本", "适用类型", "指令集"]
    table_list.append(heading)
    for i in range(cmd_index_list):
        func_index = cmd_index_list[i]
        func = tasker.function_list[func_index]
        table_list.append([str(i),
                           str(func.label),
                           str(func.version),
                           str(func.type),
                           str(func.function_list)])
        index += 1
    system_pkg["table_msg"](table_list, heading = True)
def choose_cmd(cmd_index_list, tasker, system_pkg) -> int | None:
    if len(cmd_index_list) == 0:
        return None
    elif len(cmd_index_list) == 1:
        return cmd_index_list[0]
    show_cmd_list(cmd_index_list, tasker, system_pkg)
    user_input = system_pkg["normal_input"]("选择指令（输入索引）")
    try:
        user_input = int(user_input)
        return cmd_index_list[user_input]
    except ValueError:
        system_pkg["system_msg"](f"\"{user_input}\"不为数字索引")
    except IndexError:
        system_pkg["system_msg"](f"\"{user_input}\"不在索引范围内")
    return None
def proceed_func(cmd_pair, func_index, tasker, system_pkg):
    tasker.function_list[func_index].proceed(cmd_pair, tasker, system_pkg)
def optimized_get_not_end_timer_index(not_end_timer_index, tasker):
    """挖坑，以后可以优化一下（估计懒得优化）"""
    return get_not_end_timer_index(tasker)


def timer_interface(tasker, system_pkg):
    """
    """
    show_info_dict = {"not_end_timer_index":get_not_end_timer_index(tasker),
                      "show_not_end_timer":True}
    while True:
        # interface预显示内容
        interface_pre_show(show_info_dict, tasker, system_pkg)
        # 获取输入
        interface_input_dict = get_interface_input(system_pkg)
        if interface_input_dict == False: return (system_pkg["CONDITION_SUCCESS"], f"{tasker.tasker_label}.interface界面")
        #获取指令索引
        cmd = interface_input_dict["cmd"]
        parameter = interface_input_dict["parameter"]
        cmd_index_list = get_cmd_index_list(cmd, tasker)
        func_index = choose_cmd(cmd_index_list, tasker, system_pkg)
        if func_index == None: continue
        # 执行指令
        proceed_func([cmd, parameter], func_index, tasker, system_pkg)
        # 刷新未完成的timer列表（索引）
        show_info_dict["not_end_timer_index"] = optimized_get_not_end_timer_index(show_info_dict["not_end_timer_index"], tasker)
        show_info_dict["show_not_end_timer"] = True