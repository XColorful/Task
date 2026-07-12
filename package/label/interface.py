from .function import get_interface_input

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

def interface_pre_show(tasker, system_pkg):
    # 待补充
    pass

def label_interface(tasker, system_pkg):
    
    while True:
        # interface预显示内容
        interface_pre_show(tasker, system_pkg)
        # 获取输入
        interface_input_dict = get_interface_input(tasker.tasker_label, system_pkg)
        if interface_input_dict == False: return (system_pkg["CONDITION_SUCCESS"], f"{tasker.tasker_label}.interface界面")
        #获取指令索引
        cmd = interface_input_dict["cmd"]
        parameter = interface_input_dict["parameter"]
        cmd_index_list = get_cmd_index_list(cmd, tasker)
        func_index = choose_cmd(cmd_index_list, tasker, system_pkg)
        if func_index == None: continue
        # 执行指令
        proceed_func([cmd, parameter], func_index, tasker, system_pkg)
        # 空行
        system_pkg["normal_msg"]("")