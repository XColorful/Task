from datetime import datetime, timedelta

def convert_to_int(s:str):
    """返回字符串是否能转换为int，不修改原字符串
    
    接收一个普通字符串，转换失败则返回None"""
    try:
        return int(s)
    except ValueError:
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
            
            "content" -> intlist[int],
            
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
    if duration.total_seconds() < 0:
        return "Error:start, end    "
    if duration.total_seconds() >= 8640000:  # 100 days in seconds
        return "More than 100d      "
    
    days, remainder = divmod(duration.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)
    
    result = ""
    result += f"{int(days):>2}d " if days > 0 else "    "
    result += f"{int(hours):>2}h " if hours > 0 else "    "
    result += f"{int(minutes):>2}m" if minutes > 0 else "   "
    
    return result + " " * (16 - len(result))