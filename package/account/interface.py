from datetime import datetime
from .function import convert_to_int, table_class_func, settings_help

def a_is_later_than_b(time_a:str, time_b:str) -> bool:
    date_format = "%Y_%m_%d"
    try:
        if len(time_a) != 10: return False
        date_a = datetime.strptime(time_a, date_format)
    except ValueError: return False

    try:
        if len(time_b) != 10: return True
        date_b = datetime.strptime(time_b, date_format)
    except ValueError: return True

    return date_a > date_b

def show_account_tasker_info(tasker, system_pkg):
    total_account = 0
    last_date = ""
    for task in tasker.task_list:
        if task.version == "account":
            total_account += 1
        if a_is_later_than_b(task.last_date, last_date):
            last_date = task.last_date
    table_list = [[f"--------{tasker.tasker_label}--------"], [f"task总数：{total_account}"], [f"最新密码日期：{last_date}"]]
    system_pkg["table_msg"](table_list, heading = False)
    
def interface_info(system_pkg, show_msg = True):
    interface_label = "account_interface"
    interface_version = "account"
    interface_type = "Extra"
    info_list = [interface_label, interface_version, interface_type]
    if show_msg == True:
        table_list = []
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
    settings_help(system_pkg)

def show_interface(tasker, system_pkg):
    """显示account统计简略信息，不显示account类型以外的task
    
    """
    system_pkg["tips_msg"]("输入\"/info\"获取更多信息")
    system_pkg["tips_msg"]("注意：未指定指令将默认执行search功能")
    show_account_tasker_info(tasker, system_pkg)

def account_interface(tasker, system_pkg): # tasker -> tasker
    """
    """
    show_account_interface = True
    while True:
        # 显示account_interface
        if show_account_interface == True: show_interface(tasker, system_pkg)
        # 查看是否有可用的class_func
        function_list = tasker.function_list
        if function_list == []: system_pkg["system_msg"]("无可用的class_func")
        # 用户输入
        user_input = system_pkg["normal_input"](f"{tasker.tasker_label}")
        # 输入类型筛选
        if user_input == system_pkg["EXIT"]: return (system_pkg["CONDITION_SUCCESS"], f"{tasker.tasker_label}.interface界面")
        if user_input == "":
            show_account_interface = False
            continue
        if user_input == "/info":
            interface_info(system_pkg)
            table_class_func(function_list, system_pkg)
            interface_help(system_pkg)
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
                    show_account_interface = False
                continue
            else: # 既不为可用指令，又不为非负索引
                system_pkg["system_msg"](f"没有可用的指令\"{cmd}\"")
                system_pkg["tips_msg"]("输入\"/info\"获取更多信息")
                # 执行默认function
                if default_function == True:
                    cmd_list = ["search", user_input]
                    default_proceed_function.proceed(cmd_list, tasker, system_pkg)
                    show_account_interface = False
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
        show_account_interface = True