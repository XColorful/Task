from default_method import default_method_template
from .function import convert_to_int, convert_to_float, table_container_function_list, table_class_func, table_show_container_func

class container_manager(default_method_template):
    def __init__(self):
        super().__init__() # 继承父类
        self.label = "container_manager"
        self.version = "1.0"
        self.method_list = ["add_func", "del_func"]
    
    def method_info(self):
        return super().method_info()
    
    def analyze(self, cmd_list:list, container_list:list, system_pkg:dict): # 分析是否存在可用指令，返回(bool，[标签，版本，类型])
        return super().analyze(cmd_list, container_list, system_pkg)

    def proceed(self, cmd_list:list, container_list:list, system_pkg:dict):
        return super().proceed(cmd_list, container_list, system_pkg)
    
    def add_func(self, cmd_parameter:str, container_list:list, system_pkg:dict):
        # 选取container
        get_index = "" # 用于get的索引
        MAX_INDEX = len(container_list) - 1
        if MAX_INDEX == -1:
            system_pkg["system_msg"]("container_list为空")
            return (system_pkg["CONDITION_SUCCESS"], "container_list为空")
        # 展示container.function_list
        table_container_function_list(range(0, MAX_INDEX +1), container_list, system_pkg)
        # 获取container_list索引值
        while get_index == "":
            # 获取user_input
            if cmd_parameter != "": # 有参数则跳过首次获取user_input
                user_input = cmd_parameter
            else:
                system_pkg["tips_msg"]("匹配首个符合的标签，输入\"exit\"退出")
                user_input = system_pkg["normal_input"]("输入索引或标签")
            if user_input == "exit": return (system_pkg["CONDITION_SUCCESS"], "exit")
            
            if user_input != "": # 用户输入不为空字符串
                # 索引判断
                convert_result = convert_to_int(user_input)
                if convert_result != None:
                    if 0 <= convert_result <= MAX_INDEX:
                        get_index = convert_result
                        break
                # 标签判断
                index_list = []
                for container_index in range(0, MAX_INDEX + 1): # 对于每一个container
                    container_label = container_list[container_index].container_label
                    if user_input in container_label:
                        index_list.append(container_index)
                        if user_input == container_label:
                            index_list = [container_index]
                            break # 完全匹配则退出

                if len(index_list) == 1: # 用户输入有一项匹配，自动获取索引
                    get_index = index_list[0]
                    break
                elif len(index_list) == 0: # 用户输入非空字符串，但没有匹配
                    system_pkg["system_msg"](f"没有找到\"{user_input}\"")
                else: # 用户输入有多项匹配，仅显示筛选的container
                    table_container_function_list(index_list, container_list, system_pkg)
        # 显示container信息
        container_index = get_index
        container = container_list[container_index]
        system_pkg["head_msg"](f"{container.container_label}")
        system_pkg["body_msg"](container.function_list)
        # 显示所有可用功能
        class_func_list = system_pkg["class_func_list"]
        class_func_label_list = table_class_func(range(len(class_func_list)), class_func_list, system_pkg)
        # 选取功能
        get_index = ""
        index_list = []
        MAX_FUNC_INDEX = len(class_func_list) - 1
        while get_index == "":
            system_pkg["tips_msg"]("匹配首个符合的标签或func，输入\"exit\"退出")
            user_input = system_pkg["normal_input"]("选取func")
            if user_input == "exit": return (system_pkg["CONDITION_SUCCESS"], "exit")
            if user_input != "": # 用户输入不为空字符串
                # 索引判断
                convert_result = convert_to_int(user_input)
                if convert_result != None:
                    if 0 <= convert_result <= MAX_FUNC_INDEX:
                        get_index = convert_result
                        break
                # 标签，func判断
                index_list = []
                for func_index in range(0, MAX_FUNC_INDEX + 1): # 对于每一个container
                    func_instance = class_func_list[func_index]()
                    func_label = func_instance.label
                    if user_input in func_label:
                        index_list.append(func_index)
                        if user_input == func_label:
                            index_list = [func_index]
                            break # 完全匹配func标签则退出
                        for func in class_func_label_list[func_index]:
                            if user_input == func:
                                index_list = [func_index]
                                break # 完全匹配func则退出
                if len(index_list) == 1: # 用户输入有一项匹配，自动获取索引
                    get_index = index_list[0]
                    break
                elif len(index_list) == 0: # 用户输入非空字符串，但没有匹配
                    system_pkg["system_msg"](f"没有找到\"{user_input}\"")
                else: # 用户输入有多项匹配，仅显示筛选的container
                    table_class_func(index_list, class_func_list, system_pkg)
        
        class_func_index = get_index
        class_func = class_func_list[class_func_index]()
        class_func_type = class_func.type
        container_type = container.type
        class_func_version = class_func.version
        container_version = container.version
        # container为默认类型
        if container_type == system_pkg["TYPE_DEFAULT_CONTAINER"]:
            # class_func为extra类型
            if class_func_type == system_pkg["TYPE_EXTRA_CLASS_FUNC"]:
                system_pkg["system_msg"](f"默认Tasker类型不支持Extra类型class_func")
                return (system_pkg["CONDITION_SUCCESS"], f"\"{class_func.label}\"（extra类型）不支持Tasker\"{container.container_label}\"")
            # class_func为default类型
            else: # 进行版本比较
                class_func_version = convert_to_float(class_func.version) # 转换为float类型或None
                if class_func_version == None:
                    system_pkg["system_msg"](f"class_func\"{class_func.label}\"版本格式错误")
                    return (system_pkg["CONDITION_SUCCESS"], f"\"{class_func.label}\"版本格式错误")
                else:
                    if class_func_version > convert_to_float(container_version):
                        system_pkg["system_msg"](f"class_func\"{class_func.label}\"版本不支持")
                        return (system_pkg["CONDITION_SUCCESS"], f"\"{class_func.label}\"版本不支持Tasker\"{container.container_label}\"")
        # container为extra类型
        elif container_type == system_pkg["TYPE_EXTRA_CONTAINER"]:
            # class_func为extra类型
            if class_func_type == system_pkg["TYPE_EXTRA_CLASS_FUNC"]:
                if class_func_version != container_version: # extra版本不同
                    system_pkg["system_msg"](f"Tasker\"{container_type}\"（extra类型）仅支持相同版本的class_func（extra类型）")
                    return (system_pkg["CONDITION_SUCCESS"], f"\"{class_func.label}\"（extra类型）不支持Tasker\"{container.container_label}\"（extra类型）")
            # class_func为default类型
            else: # 进行默认版本比较
                suit_task = False
                error_task = False
                for task_template in container.task_template:
                    task = task_template()
                    task_version = convert_to_float(task.version)
                    if task_version == None: continue # 跳过extra类型
                    if convert_to_float(class_func_version) > task_version:
                        error_task = True
                        break
                    else: suit_task = True
                if error_task == True:
                    system_pkg["system_msg"](f"Tasker\"{container.container_label}\"（extra类型）内包含低版本task类型模板")
                    return (system_pkg["CONDITION_SUCCESS"], f"\"{class_func.label}\"（extra类型）不支持Tasker\"{container.container_label}\"（extra类型）（含有低版本task模板）")
                if suit_task == False:
                    system_pkg["system_msg"](f"Tasker\"{container.container_label}\"（extra类型）内无可用的默认task类型模板")
                    return (system_pkg["CONDITION_SUCCESS"], f"\"{class_func.label}\"（extra类型）不支持Tasker\"{container.container_label}\"（extra类型）（无可用的默认task模板）")
        # container为未知类型
        else:
            system_pkg["system_msg"]("Tasker类型错误")
            return (system_pkg["CONDITION_FAIL"], f"Tasker{container.container_label}类型（{container_type}）异常")
        # 确认是否添加
        user_input = system_pkg["normal_input"]("确认添加(y/n)")
        if user_input == "y":
            container.function_list.append(class_func)
            system_pkg["system_msg"](f"已添加\"{class_func.label}\"")
            return (system_pkg["CONDITION_SUCCESS"], f"{container.container_label}.function_list添加\"{class_func.label}\"")
        return (system_pkg["CONDITION_SUCCESS"], "取消添加class_func")

    def del_func(self, cmd_parameter:str, container_list:list, system_pkg:dict):
        # 选取container
        get_index = "" # 用于get的索引
        MAX_INDEX = len(container_list) - 1
        if MAX_INDEX == -1:
            system_pkg["system_msg"]("container_list为空")
            return (system_pkg["CONDITION_SUCCESS"], "container_list为空")
        # 展示container.function_list
        table_container_function_list(range(0, MAX_INDEX +1), container_list, system_pkg)
        # 获取container_list索引值
        while get_index == "":
            # 获取user_input
            if cmd_parameter != "": # 有参数则跳过首次获取user_input
                user_input = cmd_parameter
            else:
                system_pkg["tips_msg"]("匹配符合的标签，输入\"exit\"退出")
                user_input = system_pkg["normal_input"]("输入索引或标签")
            if user_input == "exit": return (system_pkg["CONDITION_SUCCESS"], "exit")
            
            if user_input != "": # 用户输入不为空字符串
                # 索引判断
                convert_result = convert_to_int(user_input)
                if convert_result != None:
                    if 0 <= convert_result <= MAX_INDEX:
                        get_index = convert_result
                        break
                # 标签判断
                index_list = []
                for container_index in range(0, MAX_INDEX + 1): # 对于每一个container
                    container_label = container_list[container_index].container_label
                    if user_input in container_label:
                        index_list.append(container_index)
                        if user_input == container_label:
                            index_list = [container_index]
                            break # 完全匹配则退出

                if len(index_list) == 1: # 用户输入有一项匹配，自动获取索引
                    get_index = index_list[0]
                    break
                elif len(index_list) == 0: # 用户输入非空字符串，但没有匹配
                    system_pkg["system_msg"](f"没有找到\"{user_input}\"")
                else: # 用户输入有多项匹配，仅显示筛选的container
                    table_container_function_list(index_list, container_list, system_pkg)
        # 显示container, function_list
        container_index = get_index
        system_pkg["head_msg"](f"{container_list[container_index].container_label}")
        function_list = container_list[container_index].function_list
        func_label_list = table_show_container_func(range(len(function_list)), function_list, system_pkg)
        get_index = ""
        index_list = []
        MAX_FUNC_INDEX = len(function_list) - 1
        while get_index == "":
            system_pkg["tips_msg"]("匹配符合的索引或func标签，输入\"exit\"退出")
            user_input = system_pkg["normal_input"]("选取func")
            if user_input == "exit": return (system_pkg["CONDITION_SUCCESS"], "exit")
            if user_input != "": # 用户输入不为空字符串
                # 索引判断
                convert_result = convert_to_int(user_input)
                if convert_result != None:
                    if 0 <= convert_result <= MAX_FUNC_INDEX:
                        get_index = convert_result
                        break
                # 标签判断
                index_list = []
                for func_index in range(0, MAX_FUNC_INDEX + 1): # 对于每一个container
                    func_label = func_label_list[func_index]
                    if user_input in func_label:
                        index_list.append(func_index)
                        if user_input == func_label:
                            index_list = [func_index]
                            break # 完全匹配func标签则退出
                if len(index_list) == 1: # 用户输入有一项匹配，自动获取索引
                    get_index = index_list[0]
                    break
                elif len(index_list) == 0: # 用户输入非空字符串，但没有匹配
                    system_pkg["system_msg"](f"没有找到\"{user_input}\"")
                else: # 用户输入有多项匹配，仅显示筛选的container
                    table_show_container_func(index_list, function_list, system_pkg)
        # container_index
        func_index = get_index
        func_label = function_list[func_index].label
        user_input = system_pkg["normal_input"](f"删除\"{func_label}\"(y/n)")
        if user_input == "y":
            del container_list[container_index].function_list[func_index]
            system_pkg["system_msg"](f"已删除\"{func_label}\"")
            return (system_pkg["CONDITION_SUCCESS"], f"{container_list[container_index].container_label}.function_list删除\"{func_label}\"")
        return (system_pkg["CONDITION_SUCCESS"], "删除class_func")