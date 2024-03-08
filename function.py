from os import mkdir
from os.path import exists, join
import pickle

def convert_to_int(s:str):
    """返回字符串是否能转换为int，不修改原字符串
    
    接收一个普通字符串，转换失败则返回None"""
    try:
        return int(s)
    except ValueError:
        return None

def add_index_in_list(input_list:list, start_index = 0, heading = False):
    """为列表里每项添加索引字符串，要求每项均为列表
    
    [["a", "b"], ["c", "d"]] -> [["0", "a", "b"], ["1", "c", "d"]]
    
    start_index -> int
    
    heading -> bool
    
    若heading为True则首项添加空字符串"""
    index_for_list = start_index
    list_start_index = 0
    if heading == True:
        input_list[0].insert(0, "")
        list_start_index += 1
    for index_for_input_list in range(list_start_index, len(input_list)):
        index_str = str(index_for_list)
        input_list[index_for_input_list].insert(0, index_str)
        index_for_list += 1

def create_str_index_list(input_list:list, start_index = 0, heading = False):
    """基于列表元素数量返回相同数量的索引字符串列表
    
    输入任意长度的列表
    
    start_index -> int
    
    heading -> bool
    
    若heading为True则跳过第一项"""
    index = start_index
    if input_list == []:
        return []
    list_start_index = 0
    if heading == True:
        list_start_index += 1
    str_index_list = []
    for i in range(list_start_index, len(input_list)):
        str_index_list.append(str(index))
        index += 1
    return str_index_list

def read_from_pkl(dir:str):
    pkl_file = open(dir, "rb")
    return_object = pickle.load(pkl_file)
    pkl_file.close()
    return return_object

def save_to_pkl(input_object, dir:str):
    pkl_file = open(dir, "wb")
    pickle.dump(input_object, pkl_file, 5)
    pkl_file.close()

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

def error_log(exception_message:str, folder_dir:str, file_name:str):
    if not exists(folder_dir): mkdir(folder_dir) # 创建目录
    file_dir = join(folder_dir, file_name)
    with open(file_dir, "w", encoding = "utf-8") as f:
        f.write(exception_message)

def normal_log(time_list:list, command_list:list, proceed_info_list:list, folder_dir:str, file_name:str):
    if not exists(folder_dir): mkdir(folder_dir) # 创建目录
    file_dir = join(folder_dir, file_name)
    with open(file_dir, "a", encoding = "utf-8") as f:
        f.write(f"({time_list[0]}, {time_list[1]})\n") # (起始时间, 结束时间)
        method_info = proceed_info_list[0].method_info()
        method_list = proceed_info_list[0].method_list
        f.write(f"\tlabel:{method_info[0]}; version:{method_info[1]}; type:{method_info[2]}; method_list:{str(method_list)}\n")
        f.write(f"\tcommand_list:{str(command_list)}\n")
        f.write(f"\tproceed_condition:{proceed_info_list[1]}; proceed_return:{proceed_info_list[2]}\n")
    return None

def table_analyze_result(method_list:list, method_index_list:list, system_pkg:dict, start_index = 1):
    """[标签，版本，适用类型，指令集]
    
    """
    table_list = [] # 用于table_msg的临时变量
    heading = ["标签", "版本", "适用类型", "指令集"]
    table_list.append(heading)
    for index in method_index_list:
        table_list.append(method_list[index])
    add_index_in_list(table_list, start_index, heading = True) # 添加序号
    system_pkg["table_msg"](table_list, heading = True)
    return None