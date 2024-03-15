from os import mkdir, makedirs, remove
from os.path import exists, join, getsize, basename
import pickle

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

def save_pkl(input_object, dir:str):
    pkl_file = open(dir, "wb")
    pickle.dump(input_object, pkl_file, 5)
    pkl_file.close()

from datetime import datetime, timedelta
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

def YYYY_MM_DD_HH_MM_SS(adjust = "0"):
    """输出格式化日期，正数为添加天数
    
    adjust -> int"""
    now = datetime.now()
    try:
        now += timedelta(days = int(adjust))
    except ValueError:
        print("[Error]adjust must be <int>, please check input.")
        return None
    formatted_date_time = now.strftime("%Y_%m_%d - %H-%M-%S")
    return formatted_date_time

def error_log(exception_message:str, folder_dir:str, filename:str):
    if not exists(folder_dir): mkdir(folder_dir) # 创建目录
    file_dir = join(folder_dir, filename)
    with open(file_dir, "w", encoding = "utf-8") as f:
        f.write(exception_message)

def normal_log(time_list:list, command_list:list, proceed_info_list:list, folder_dir:str, filename:str):
    if not exists(folder_dir): mkdir(folder_dir) # 创建目录
    file_dir = join(folder_dir, filename)
    with open(file_dir, "a", encoding = "utf-8") as f:
        f.write(f"({time_list[0]}, {time_list[1]})\n") # (起始时间, 结束时间)
        method_info = proceed_info_list[0].method_info()
        method_list = proceed_info_list[0].method_list
        f.write(f"\tlabel:{method_info[0]}; version:{method_info[1]}; type:{method_info[2]}; method_list:{str(method_list)}\n")
        f.write(f"\tcommand_list:{str(command_list)}\n")
        f.write(f"\tproceed_condition:{proceed_info_list[1]}; proceed_return:{proceed_info_list[2]}\n")
    return None

def file_size_str(file_path):
    size_in_bytes = getsize(file_path)
    size_in_kib = size_in_bytes / 1024 # Convert to KiB
    if size_in_kib < 1024: return f"{size_in_kib:.2f} KiB"
    else: return f"{size_in_kib/1024:.2f} MiB"

import glob
def backup_pkl(data, dir:str, system_pkg:dict, interval : int = 3, backup_total : int = 3):
    """管理main_container_list.pkl备份文件
    
    interval：保存日期间隔
    backup_total：维持的备份文件总数"""
    # 参数检查
    date_interval = 3 if interval < 0 else interval
    backup_total = 3 if backup_total <= 0 else backup_total
    # 读取符合格式的文件名
    pkl_file_list = []
    if not exists(dir): makedirs(dir)
    else: pkl_file_list = glob.glob(join(dir, 'backup_*_*_* - *-*-*.pkl'))
    pkl_file_list.sort()
    # 比较时间差是否超过interval
    current_time = YYYY_MM_DD_HH_MM_SS()
    file_name = f'backup_{YYYY_MM_DD_HH_MM_SS()}.pkl'
    current_date = datetime.strptime(current_time, "%Y_%m_%d - %H-%M-%S")
    # 如果存在备份文件
    display_last_backup_time = ""
    if pkl_file_list:
        file_basename = basename(pkl_file_list[-1])
        last_backup_time = datetime.strptime(file_basename[7:28], "%Y_%m_%d - %H-%M-%S")
        # 如果没超过，直接返回
        if (current_date - last_backup_time).days < date_interval: return None
        else: display_last_backup_time = f"（上次备份：{last_backup_time.strftime("%Y_%m_%d - %H-%M-%S")}）"
    # 写入备份pkl文件
    backup_dir = join(dir, file_name)
    with open(backup_dir, 'wb') as f: pickle.dump(data, f)
    # pkl数量超过backup_total，则删除最老的一个
    backup_count = len(pkl_file_list) + 1
    if backup_count > backup_total:
        remove(pkl_file_list[0])
        backup_count -= 1
    system_pkg["system_msg"](f"自动备份pkl文件至\"{backup_dir}\"")
    system_pkg["body_msg"]([f"文件大小：{file_size_str(backup_dir)}", f"备份间隔：{date_interval}天{display_last_backup_time}", f"备份总数：{backup_count}/{backup_total}"])

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