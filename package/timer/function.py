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