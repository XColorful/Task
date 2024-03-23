import re
chinese_word = re.compile(u"[\u2E80-\u2FD5\u3190-\u319f\u3400-\u4DBF\u4E00-\u9FCC\uF900-\uFAAD\uFF00-\uFFEF]+")

def convert_to_int(s:str):
    """返回字符串是否能转换为int，不修改原字符串
    
    接收一个普通字符串，转换失败则返回None"""
    try:
        return int(s)
    except ValueError:
        return None

def convert_to_float(s:str):
    """返回字符串是否能转换为float，不修改原字符串
    
    接收一个普通字符串，转换失败则返回None"""
    try:
        return float(s)
    except ValueError:
        return None

def table_tasker_list(iterator, tasker_list:list, system_pkg:dict):
    """["索引", "创建日期", "标签", "版本", "Tasker类型"]
    
    """
    table_list = []
    heading = ["索引", "创建日期", "标签", "版本", "Tasker类型"]
    table_list.append(heading)
    for i in iterator:
        table_list.append([str(i), 
                        tasker_list[i].create_date, 
                        tasker_list[i].tasker_label, 
                        tasker_list[i].version, 
                        tasker_list[i].type])
    system_pkg["table_msg"](table_list, heading = True)
    return None

def table_tasker_template(tasker_template_list, system_pkg:dict) -> None:
    """["索引", "版本", "Tasker类型", "介绍"]
    
    返回tasker_version_list Tasker模板标签列表"""
    table_list = []
    heading = ["索引", "版本", "Tasker类型", "介绍"]
    table_list.append(heading)
    # 获取展示列表，创建标签列表
    for index, tasker_template in enumerate(tasker_template_list):
        table_list.append([str(index),
                           tasker_template.version,
                           tasker_template.type,
                           tasker_template.introduction])
    system_pkg["table_msg"](table_list, heading = True)
    return None

def get_list_width(input_list:list):
    global chinese_word
    width_list = []
    max_width_list = []
    for i in range(0, len(input_list)): # 列表内每一项组合
        width_list.append([])
        for j in range(0, len(input_list[i])): # 组合内每个字符串
            width = len(input_list[i][j])
            chinese_list = re.findall(chinese_word, input_list[i][j])
            for k in chinese_list: # 中文字符宽度 +1
                width += len(k)
            width_list[i].append(width)
            try:
                if width > max_width_list[j]:
                    max_width_list[j] = width
            except IndexError:
                max_width_list.append(width)
    return width_list, max_width_list

def count_chinese_char(input_str:str):
    global chinese_word
    chinese_count = 0
    chinese_list = re.findall(chinese_word, input_str)
    for i in chinese_list:
        chinese_count += len(i)
    return chinese_count

def YYYY_MM_DD(adjust = "0"):
    """输出格式化日期，正数为添加天数
    
    adjust -> int"""
    from datetime import datetime, timedelta
    now = datetime.now()
    try:
        now += timedelta(days = int(adjust))
    except ValueError:
        print("[Error]adjust must be <int>, please check input.")
        return None
    formatted_date = now.strftime("%Y_%m_%d")
    return formatted_date

def YYYY_MM_DD_HH_MM_SS(adjust = "0"):
    """输出格式化日期，正数为添加天数
    
    adjust -> int"""
    from datetime import datetime, timedelta
    now = datetime.now()
    try:
        now += timedelta(days = int(adjust))
    except ValueError:
        print("[Error]adjust must be <int>, please check input.")
        return None
    formatted_date_time = now.strftime("%Y_%m_%d - %H-%M-%S")
    return formatted_date_time

def table_task_template_instance(task_instance_list:list, system_pkg:dict):
    table_list = []
    heading = ["索引", "版本", "task类型"]
    table_list.append(heading)
    index = 0
    for instance in task_instance_list:
        table_list.append([str(index), str(instance.version), str(instance.type)])
        index += 1
    system_pkg["table_msg"](table_list, heading = True)
    return None

def create_index_list(input_list:list, adjust = 0):
    index_list = [i+adjust for i in range(len(input_list))]
    return index_list

def select_valid_index(user_input:str, select_list:list):
    """用空格分隔输入，给出所有符合条件的索引，输入空字符串则创建索引列表
    
    依赖该文件下函数create_index_list"""
    # 空字符串输入
    if user_input == "": return create_index_list(select_list)
    # 非空字符串输入
    user_input_list = user_input.split(" ")
    select_index_list = []
    for index in user_input_list:
        try:
            index = int(index)
            select_list[index]
            select_index_list.append(index)
        except ValueError:
            continue
    return select_index_list

def table_compare_task_list(old_task_list:list, new_task_list:list, system_pkg:dict, display = 8):
    """给出两个默认类型的task_list，进行1.0版本比较
    
    display -> int，显示task_list末尾的若干项task"""
    old_task_list_length = len(old_task_list)
    new_task_list_length = len(new_task_list)
    # 获取需显示的项
    old_list = old_task_list[-display:]
    new_list = new_task_list[-display:]
    old_len = len(old_list)
    new_len = len(new_list)
    if old_len > new_len: MAX_LEN = old_len
    else: MAX_LEN = new_len
    old_list = old_task_list[-MAX_LEN:]
    new_list = new_task_list[-MAX_LEN:]
    table_list = []
    for index in range(-1, -MAX_LEN-1, -1):
        try:
            task = old_list[index]
            display_content = task.content[:8]
            old_column = [str(old_task_list_length + index), f"{task.date}|{task.attribute}|{display_content}"]
        except IndexError:
            old_column = ["", ""]
        try:
            task = new_list[index]
            display_content = task.content[:8]
            new_column = [str(new_task_list_length + index), f"{task.date}|{task.attribute}|{display_content}"]
        except IndexError:
            new_column = ["", ""]
        table_list.append(old_column + new_column)
    heading = ["索引", "老版本", "索引", "新版本"]
    table_list.append(heading)
    table_list.reverse()
    system_pkg["table_msg"](table_list, heading = True)

def table_backup_file(backup_list:list, system_pkg:dict):
    table_list = []
    heading = ["索引", "路径"]
    table_list.append(heading)
    for index, file_path in enumerate(backup_list):
        table_list.append([str(index), file_path])
    system_pkg["table_msg"](table_list, heading = True)