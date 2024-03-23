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