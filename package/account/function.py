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
    from datetime import datetime, timedelta
    now = datetime.now()
    try:
        now += timedelta(days = int(adjust))
    except ValueError:
        print("[Error]adjust must be <int>, please check input.")
        return None
    formatted_date = now.strftime("%Y_%m_%d")
    return formatted_date

def table_class_func(function_list:list, system_pkg:dict):
    """["功能类", "版本", "适用类型", "指令集"]
    
    在输出列表前添加索引，从0开始
    """
    table_list = []
    heading = ["索引", "功能类", "版本", "适用类型", "指令集"]
    table_list.append(heading)
    index = 0
    for class_func in function_list:
        table_list.append([str(index), str(class_func.label), str(class_func.version), str(class_func.type), str(class_func.function_list)])
        index += 1
    system_pkg["table_msg"](table_list, heading = True)
    return None