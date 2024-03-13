from .function import convert_to_int, table_class_func

def interface_info(system_pkg, show_msg = True):
    interface_label = "default_interface"
    interface_version = "1.0"
    interface_type = "Default_Template"
    table_list=[]
    heading = ["interface标签", "interface版本", "interface类型"]
    table_list.append(heading)
    table_list.append([interface_label, interface_version, interface_type])
    if show_msg == True: system_pkg["table_msg"](table_list)
    return [interface_label, interface_version, interface_type]

def interface_help(system_pkg):
    system_pkg["tips_msg"]("以\"/\"开头强制识别为指令")
    system_pkg["tips_msg"]("以\"+\"开头强制执行指令search，输入作为参数")
    system_pkg["tips_msg"]("用空格分隔指令与内容")
    system_pkg["tips_msg"]("输入\"/info\"执行interface内置info功能")

def default_interface(container, system_pkg): # container -> container
    """输入时默认执行search
    
    """
    system_pkg["tips_msg"]("输入\"/info\"获取更多信息")
    show_task = True
    while True:
        # 显示最后8项task
        if show_task == True:
            system_pkg["normal_msg"](f"--------{container.container_label}--------")
            MAX_INDEX_TASK_LIST = len(container.task_list) - 1 # task_list最大索引
            show_task_list = container.task_list[-8:]
            show_index = MAX_INDEX_TASK_LIST - len(show_task_list) + 1
            for task in show_task_list:
                system_pkg["normal_msg"](f"{show_index}|{task}")
                show_index += 1
        # 查看是否有可用的class_func
        function_list = container.function_list
        if function_list == []: system_pkg["system_msg"]("无可用的class_func")
        # 用户输入
        user_input = system_pkg["normal_input"](f"{container.container_label}")
        # 输入类型预筛选
        if user_input == system_pkg["EXIT"]: return (system_pkg["CONDITION_SUCCESS"], f"{container.container_label}.interface界面")
        if user_input == "":
            show_task = False
            continue
        if user_input == "/info":
            interface_info(system_pkg)
            table_class_func(function_list, system_pkg)
            interface_help(system_pkg)
            continue
        # 判断指令类型
        command_list = user_input.split(" ", 1)
        if command_list[0] == " ":
            system_pkg["system_msg"]("输入不能以空格开头")
            system_pkg["tips_msg"]("输入\"/info\"获取更多信息")
            continue
        if user_input[0] == "/": command_list = user_input[1:].split(" ", 1)
        elif user_input[0] == "+": command_list = ["search", user_input[1:]]
        command = command_list[0]
        # 查找可用指令
        default_function = False
        available_func_index = []
        for class_func_index in range(0, len(function_list)):
            for function in function_list[class_func_index].function_list:
                if command == function:
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
            convert_result = convert_to_int(command)
            if convert_result != None: # 执行搜索，参数为int索引
                # 执行默认function
                if default_function == True:
                    command_list = ["search", convert_result]
                    default_proceed_function.proceed(command_list, container, system_pkg)
                    show_task = False
                continue
            else: # 既不为可用指令，又不为非负索引
                system_pkg["system_msg"](f"没有可用的指令\"{command}\"")
                system_pkg["tips_msg"]("输入\"/info\"获取更多信息")
                # 执行默认function
                if default_function == True:
                    command_list = ["search", user_input]
                    default_proceed_function.proceed(command_list, container, system_pkg)
                    show_task = False
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
        proceed_function.proceed(command_list, container, system_pkg)
        show_task = True