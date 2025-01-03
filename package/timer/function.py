from datetime import datetime, timedelta

def convert_to_int(s:str):
    """返回字符串是否能转换为int，不修改原字符串
    
    接收一个普通字符串，转换失败则返回None"""
    try:
        return int(s)
    except ValueError:
        return None
    except TypeError:
        return None

def YYYY_MM_DD(adjust = "0"):
    """输出格式化日期，正数为添加天数
    
    adjust -> int"""
    now = datetime.now()
    try:
        now += timedelta(days = int(adjust))
    except ValueError:
        print("[Error]adjust must be <int>, please check input.")
        return None
    formatted_date = now.strftime("%Y_%m_%d")
    return formatted_date

def YYYY_MM_DD_HH_MM(adjust = "0"):
    """输出格式化日期，正数为添加天数
    
    adjust -> int"""
    now = datetime.now()
    try:
        now += timedelta(days = int(adjust))
    except ValueError:
        print("[Error]adjust must be <int>, please check input.")
        return None
    formatted_date_time = now.strftime("%Y_%m_%d-%H:%M")
    return formatted_date_time

def input_is_YYYY_MM_DD(input_str) -> bool:
    if len(input_str) != 10:
        return False
    try:
        datetime.strptime(input_str, '%Y_%m_%d')
        return True
    except ValueError:
        return False

def input_is_YYYY_MM_DD_HH_SS(input_str) -> bool:
    if len(input_str) != 16:
        return False
    try:
        datetime.strptime(input_str, '%Y_%m_%d-%H:%M')
        return True
    except ValueError:
        return False

def analyze_interface_input(str_input) -> dict:
    """返回dict{"cmd":str, "parameter":str}"""
    if str_input == "":
        return {"cmd":"", "parameter":""}
    elif str_input[0] == "+":
        try:
            str_input = str_input[1:]
            return {"cmd":"search", "parameter":str_input}
        except IndexError: return {"cmd":"search", "parameter":""}
    elif str_input[0] == "/":
        try:
            str_input = str_input[1:]
        except IndexError: return {"cmd":"", "parameter":""}
    # 一般输入
    str_input = str_input.split(" ", 1)
    try:
        parameter = str_input[1]
    except IndexError: parameter = ""
    
    return {"cmd":str_input[0], "parameter":parameter}
def get_interface_input(name, system_pkg) -> dict | bool:
    while True:
        interface_input = system_pkg["normal_input"](f"{name}")
        input_dict = analyze_interface_input(interface_input)
        if input_dict["cmd"] == "": continue
        elif input_dict["cmd"] == system_pkg["EXIT"]: return False
        
        return input_dict

def show_task_info(timer_task, task_index, system_pkg):
    """显示timer_task信息，task_index为显示参数值"""
    system_pkg["normal_msg"](f"[{task_index}]|<{timer_task.attribute}>|{timer_task.content}")
    system_pkg["body_msg"]([f"start_time:{timer_task.start_time}",
                            f"end_time:{timer_task.end_time}",
                            f"comment:{timer_task.comment}"])

def check_timer_u(timer_task, time: str) -> bool:
    start_time = datetime.strptime(timer_task.start_time, "%Y_%m_%d-%H:%M")
    time = datetime.strptime(time, "%Y_%m_%d")
    return timer_task.end_time == "" and start_time.date() <= time.date()

def check_timer_t(timer_task, time: str) -> bool:
    start_time = datetime.strptime(timer_task.start_time, "%Y_%m_%d-%H:%M")
    time = datetime.strptime(time, "%Y_%m_%d")
    return start_time.date() == time.date()

def check_timer_all(timer_task, time: str) -> bool:
    start_time = datetime.strptime(timer_task.start_time, "%Y_%m_%d-%H:%M")
    time = datetime.strptime(time, "%Y_%m_%d")
    if timer_task.end_time == "":
        return start_time.date() <= time.date()
    else:
        end_time = datetime.strptime(timer_task.end_time, "%Y_%m_%d-%H:%M")
        return start_time.date() <= time.date() <= end_time.date()


def get_not_end_timer_index(tasker) -> list[int]:
    return_index_list = []
    for index, task in enumerate(tasker.task_list):
        try:
            if task.end_time == "":
                return_index_list.append(index)
        except AttributeError: pass
    return return_index_list

def show_unfinished_timer(not_end_timer_index, tasker, system_pkg):
    system_pkg["normal_msg"](f"--------{tasker.tasker_label}中未完成的timer--------")
    table_list = []
    heading = ["指示索引", "索引", "start_time", "end_time", "属性", "内容", "注释"]
    table_list.append(heading)
    instruct_index = 0 - len(not_end_timer_index)
    if not_end_timer_index == []:
        table_list.append([""] * len(table_list[0]))
    else:
        for index in not_end_timer_index:
            task = tasker.task_list[index]
            start_time = task.start_time
            end_time = "未完成" if task.end_time == "" else task.end_time
            attribute = task.attribute
            content = task.content
            comment = task.comment
            table_list.append([str(instruct_index),
                            str(index),
                            str(start_time),
                            str(end_time),
                            str(attribute),
                            str(content),
                            str(comment)])
            instruct_index += 1
    system_pkg["table_msg"](table_list, heading = True)

def is_time_in_duration(input_str, timer_task) -> bool:
    # 将字符串转换为datetime对象
    try:
        input_time = datetime.strptime(input_str, "%Y_%m_%d-%H:%M")
        start_time = datetime.strptime(timer_task.start_time, "%Y_%m_%d-%H:%M")
        end_time = datetime.strptime(timer_task.end_time, "%Y_%m_%d-%H:%M")
    except ValueError: # 格式不符
        return False

    # 如果end_time比start_time早，那么仅判断input_str是否和start_time或end_time相同
    if end_time < start_time:
        return input_time == start_time or input_time == end_time

    # 判断input_str的时间是否在start_time和end_time之间，包括两端点
    return start_time <= input_time <= end_time

def is_str_eq_attribute(input_str, timer_task) -> bool:
    return input_str == timer_task.attribute

def is_str_in_content(input_str, timer_task) -> bool:
    return input_str in timer_task.content

def is_str_in_comment(input_str, timer_task) -> bool:
    return input_str in timer_task.comment

def is_str_in_index(input_str, tasker) -> int | None:
    index = convert_to_int(input_str)
    if index == None: return None
    try:
        tasker.task_list[index]
        return index
    except IndexError:
        return None

def find_timer_in_all(input_str, tasker) -> dict[list]:
    """返回字典{
            "time" -> list[int],
            
            "attribute" -> list[int],
            
            "content" -> list[int],
            
            "comment" -> list[int],
            
            "index" -> int | None}"""
    task_list = tasker.task_list
    time_index = []
    attr_index = []
    content_index = []
    comment_index = []
    
    for index, timer_task in enumerate(task_list):
        if is_time_in_duration(input_str, timer_task): time_index.append(index)
        if is_str_eq_attribute(input_str, timer_task): attr_index.append(index)
        if is_str_in_content(input_str, timer_task): content_index.append(index)
        if is_str_in_comment(input_str, timer_task): comment_index.append(index)
    
    timer_index = is_str_in_index(input_str, tasker)
    
    return {"time":time_index,
            "attribute":attr_index,
            "content":content_index,
            "comment":comment_index,
            "index":timer_index}

def find_timer_in_time(input_str, tasker) -> list[int]:
    time_index = []
    
    for index, timer_task in enumerate(tasker.task_list):
        if is_time_in_duration(input_str, timer_task): time_index.append(index)
    
    return time_index

def calculated_during_time(seconds):
    if seconds < 0:
        return "Error:start, end    "
    elif seconds >= 8640000: # 100 days in seconds
        return "More than 100d      "
    
    days, remainder = divmod(seconds, 86400)
    hours,remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)
    
    result = ""
    result += f"{int(days):>2}d " if days > 0 else "    "
    result += f"{int(hours):>2}h " if hours > 0 else "    "
    result += f"{int(minutes):>2}m" if minutes > 0 else "   "
    
    return result + " " * (16 - len(result))
    
def calculate_during_time(start_time, end_time):
    format = "%Y_%m_%d-%H:%M"
    try:
        start_time = datetime.strptime(start_time, format)
    except ValueError:
        return "Error:start_time     "
    
    if end_time == "":
        return "-----进行中-----"
    try:
        end_time = datetime.strptime(end_time, format)
    except ValueError:
        return "Error:end_time       "
    
    duration = end_time - start_time
    return calculated_during_time(duration.total_seconds())

def set_timer_task_df_attribute(tasker, system_pkg) -> bool | None:
    system_pkg["normal_msg"](f"原timer默认属性：{tasker.timer_task_df_attribute}")
    input_condition, user_input = system_pkg["block_input"]("设置timer默认属性", block_list = system_pkg["BLOCK_LIST"], system_pkg = system_pkg,  block_number = False)

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
    input_condition, user_input = system_pkg["block_input"]("设置timer默认内容前缀", block_list = system_pkg["BLOCK_LIST"], system_pkg = system_pkg,  block_number = False)
    
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
    input_condition, user_input = system_pkg["block_input"]("设置timer默认内容", block_list = system_pkg["BLOCK_LIST"], system_pkg = system_pkg,  block_number = False)
    
    if input_condition == False: return False
    elif user_input == "n":
        tasker.timer_task_df_content = ""
        system_pkg["system_msg"]("已清除timer默认内容")
    elif input_condition == None: return None
    else:
        tasker.timer_task_df_content = user_input
        system_pkg["system_msg"](f"默认timer默认内容更改为{tasker.timer_task_df_content}")
    return None