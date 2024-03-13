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

def table_categorize_task_result(labels:list, y:list, system_pkg:dict):
    """labels -> 第1列, y -> 第二列
    
    """
    length = len(labels)
    if length != len(y):
        system_pkg["error_msg"]("传入table_categorize_task_result的两个列表长度不一致")
        return None
    table_list = []
    heading = ["标签（x轴）", "数量（y轴）"]
    table_list.append(heading)
    for i in range(0, length):
        table_list.append([labels[i], str(y[i])])
    system_pkg["table_msg"](table_list, heading = True)