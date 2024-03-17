from os import chdir
from os.path import dirname, abspath, exists, join
working_dir = dirname(abspath(__file__))
chdir(working_dir) # 切换工作路径至当前文件目录

# main_func--------+--------+--------+--------+--------+--------+--------+--------+ Begin
from function import convert_to_int, convert_to_float
def adjust_settings(settings_dict:dict, key:str, value:str) -> bool:
    # int, float, bool类型转换
    # bool
    if value == "True": value = True
    elif value == "False": value = False
    elif value == "None": value = None
    if type(value) != bool:
        # float
        value_float = convert_to_float(value)
        if value_float != None: value = value_float
        # int（如果能int就一定先执行过float）
        value_int = convert_to_int(value)
        if value_int == value: value = value_int
    try:
        if type(settings_dict[key]) != type(value): return False
    except KeyError: return None
    settings_dict[key] = value
    return True

from importlib import import_module
def package_loader(package_name, show = True) -> bool:
    """从./package/下读取模块
    
    True -> 成功读取
    
    False -> __init__.py缺少package_dict
    
    None -> 模块不存在"""
    try: pkg = import_module(f'package.{package_name}') # package.{package_name}
    except ModuleNotFoundError:
        if show == True: system_msg(f"模块\"{package_name}\"不存在")
        return None
    try: package_dict = pkg.package_dict
    except AttributeError:
        if show == True: system_msg(f"模块\"{package_name}\"缺少package_dict")
        return False
    global class_func_list
    try: class_func_list += package_dict["class_func"]
    except KeyError: pass
    global df_tasker_template_list
    try: df_tasker_template_list += package_dict["default_tasker"]
    except KeyError: pass
    global ex_tasker_template_list
    try: ex_tasker_template_list += package_dict["extra_tasker"]
    except KeyError: pass
    global io_list
    try: io_list += package_dict["io"]
    except KeyError: pass
    global message_list
    try: message_list += package_dict["message"]
    except KeyError: pass
    global method_list
    try: method_list += package_dict["method"]
    except KeyError: pass
    global df_task_template_list
    try: df_task_template_list += package_dict["default_task"]
    except KeyError: pass
    global ex_task_template_list
    try: ex_task_template_list += package_dict["extra_task"]
    except KeyError: pass
    # 确保已经有system_msg才调整show = True
    if show == True: system_msg(f"已读取\"{package_name}\"")
    return True

def system_pkg() -> dict:
    """返回系统变量，供程序各处访问
    """
    return {"system_msg":system_msg, "error_msg":error_msg, "tips_msg":tips_msg, "table_msg":table_msg, "head_msg":head_msg, "body_msg":body_msg, "normal_msg":normal_msg,
            "EXIT":EXIT,
            "command_input":command_input, "normal_input":normal_input, "strict_input":strict_input, "block_input":block_input,
            "CONDITION_SUCCESS":CONDITION_SUCCESS, "CONDITION_FAIL":CONDITION_FAIL, "BLOCK_LIST":BLOCK_LIST,
            "TYPE_DEFAULT_TASKER":TYPE_DEFAULT_TASKER, "TYPE_EXTRA_TASKER":TYPE_EXTRA_TASKER, "TYPE_DEFAULT_METHOD":TYPE_DEFAULT_METHOD, "TYPE_EXTRA_METHOD":TYPE_EXTRA_METHOD, "TYPE_DEFAULT_CLASS_FUNC":TYPE_DEFAULT_CLASS_FUNC, "TYPE_EXTRA_CLASS_FUNC":TYPE_EXTRA_CLASS_FUNC,
            "df_tasker_template_list":df_tasker_template_list, "ex_tasker_template_list":ex_tasker_template_list,
            "df_task_template_list":df_task_template_list, "ex_task_template_list":ex_task_template_list,
            "class_func_list":class_func_list,
            "settings_dict":settings_dict,
            "github":github, "version":version, "contributor":contributor_list}

def no_tips(msg_str): # 用于settings_dict中"SHOW_TIPS"=False
    return

# main_func--------+--------+--------+--------+--------+--------+--------+--------+ End


# 预处理--------+--------+--------+--------+--------+--------+--------+--------+ Begin
# 初始化变量
from const import *
from val import *
from repo_info import *
system_msg = print
error_log_dir = join(working_dir, "error_log")


# settings管理器，设置初始化
# settings_dict初始化于./val.py
try:
    with open(f".\\settings.txt", "r", encoding = "utf-8") as f:
        settings_list = f.readlines()
        for setting in settings_list:
            setting = setting.rstrip("\n")
            try: set_key, set_value = setting.split("|", 1)
            except: continue
            adjust_settings(settings_dict, set_key, set_value)
except FileNotFoundError: pass


# 模块管理器
# 读取默认模块
load_condition = package_loader("default_pkg", show = False)
if load_condition == False:
    system_msg("模块\"default_pkg\"缺少package_dict")
    system_msg("按任意键退出")
    exit()
elif load_condition == None:
    system_msg("缺少必要模块\"default_pkg\"")
    system_msg("按任意键退出")
    exit()
# 读取package下模块
try:
    with open(f".\\load_package.txt", "r", encoding = "utf-8") as f:
        package_list = f.readlines()
        for package_name in package_list:
            package_name = package_name.rstrip("\n")
            load_condition = package_loader(package_name, show = False)
            if load_condition == True: continue
            elif load_condition == None: system_msg(f"模块\"{package_name}\"不存在")
            elif load_condition == False: system_msg(f"读取模块\"{package_name}\"失败")
except FileNotFoundError: pass


# 设定默认值
# io_list
command_input, normal_input, strict_input, block_input = io_list[0]["command_input"], io_list[0]["normal_input"], io_list[0]["strict_input"], io_list[0]["block_input"]
# message
system_msg, error_msg, tips_msg, table_msg, head_msg, body_msg, normal_msg = message_list[0]["system_msg"], message_list[0]["error_msg"], message_list[0]["tips_msg"], message_list[0]["table_msg"], message_list[0]["head_msg"], message_list[0]["body_msg"], message_list[0]["normal_msg"]
if settings_dict["SHOW_TIPS"] == False:
    tips_msg = no_tips # 将tips_msg改为无内容的空函数（仍接收参数）
    """
    这个以后再改得完善一点，避免直接去除了
    """

# 预处理--------+--------+--------+--------+--------+--------+--------+--------+ End


# 主程序--------+--------+--------+--------+--------+--------+--------+--------+ Start
# 主程序
from function import read_from_pkl, save_pkl, error_log, YYYY_MM_DD_HH_MM_SS, backup_pkl, normal_log, table_analyze_result
import traceback
from operator import attrgetter
# 启动提示
normal_msg(f"<{github}>")
head_msg(f"Task - Version {version}")
body_msg([f"By {", ".join(contributor_list)}"])


# 读取pkl存储路径
try:
    with open(f".\\pkl_dir.txt", "r", encoding = "utf-8") as f:
        main_pkl_dir = f.readline()
        if not exists(main_pkl_dir): raise
except: main_pkl_dir = join(working_dir, "main_tasker_list.pkl") # 工作目录
# 读取主容器pkl文件
from pickle import UnpicklingError
try:
    main_tasker_list = read_from_pkl(main_pkl_dir)
except FileNotFoundError:
    system_msg(f"没有可用的pkl数据文件\"{main_pkl_dir}\"")
    save_pkl(main_tasker_list, main_pkl_dir)
except ModuleNotFoundError as e:
    system_msg(f"缺少模块\"{str(e).split("'")[1]}\"，请检查目录\"./package/\"或尝试运行\"./安装.cmd\"安装所需依赖")
    normal_input("按任意键退出")
    exit()
except AttributeError as e:
    exception_msg = traceback.format_exc()
    system_msg(f"读取模块\"{str(e).split("'")[1]}\"异常，缺少必要属性")
    system_msg("展示错误信息")
    body_msg(exception_msg.split("\n"))
    error_log_filename = f"exception_{YYYY_MM_DD_HH_MM_SS()}.txt"
    error_log(exception_msg, error_log_dir, error_log_filename)
    system_msg(f"错误信息保存至{join(error_log_dir, error_log_filename)}")
    normal_input("按任意键退出")
    exit()
except UnpicklingError:
    exception_msg = traceback.format_exc()
    system_msg("读取文件\"main_pkl_dir\"异常，可能已损坏")
    system_msg("展示错误信息")
    body_msg(exception_msg.split("\n"))
    error_log_filename = f"exception_{YYYY_MM_DD_HH_MM_SS()}.txt"
    error_log(exception_msg, error_log_dir, error_log_filename)
    system_msg(f"错误信息保存至{join(error_log_dir, error_log_filename)}")
    normal_input("按任意键退出")
    exit()
if main_tasker_list == []: normal_msg("注：主容器列表为空")


# 程序主循环
while True:
    # 获取用户输入
    main_cmd_list = command_input("main") # 用" "分隔 -> [cmd:str, cmd_parameter:str]
    if main_cmd_list[0] == system_pkg()["EXIT"]: exit()
    if main_cmd_list[0] == "":
        if main_cmd_list[1] != "":
            system_msg("请先输入指令，或尝试去除最先输入的空格重新输入")
        continue
    # 初始化变量
    cmd_analyse_list = []
    exec_index_list = []
    fail_index_list = []
    cmd_proceed_time = YYYY_MM_DD_HH_MM_SS()
    cmd_proceed_date = cmd_proceed_time[0:10] # "YYYY_MM_DD"
    proceed_condition = None
    exception = False
    # 遍历可执行的method
    try_df_method = True if (main_cmd_list[1] == "" and settings_dict["DEFAULT_METHOD"] != "") else False
    if try_df_method == True:
        df_cmd_list = [settings_dict["DEFAULT_METHOD"], main_cmd_list[0]] # 用" "分隔 -> [cmd:str, cmd_parameter:str] （格式与main_cmd_list相同）
    df_exec_method_index = None
    for method_index in range(0, len(method_list)):
        # 对cmd进行一般搜索
        analyze_result = method_list[method_index].analyze(main_cmd_list, main_tasker_list, system_pkg())
        # 优先级：一般搜索结果 > 默认method
        # 搜索成功
        if analyze_result[0] == CONDITION_SUCCESS:
            cmd_analyse_list.append(analyze_result[1])
            exec_index_list.append(method_index)
            continue
        # 搜索失败
        elif analyze_result[0] == CONDITION_FAIL:
            # 尝试搜索默认method
            if try_df_method == True:
                df_analyze_result = method_list[method_index].analyze(df_cmd_list, main_tasker_list, system_pkg())
                # 搜索成功
                if df_analyze_result[0] == CONDITION_SUCCESS:
                    cmd_analyse_list.append(df_analyze_result[1])
                    exec_index_list.append(method_index)
                    df_exec_method_index = method_index
                    continue
                # 搜索失败
                elif df_analyze_result[0] == CONDITION_FAIL: pass
            # 添加cmd一般搜索结果
            cmd_analyse_list.append(analyze_result[1])
            fail_index_list.append(method_index)
            continue
    # 判断是否有可执行指令
    # 无可执行指令
    if exec_index_list == []:
        system_msg(f"指令\"{main_cmd_list[0]}\"不存在")
        if fail_index_list != []:
            if normal_input("展示所有可用指令(y/n)").lower() != "y": continue
            table_analyze_result(cmd_analyse_list, fail_index_list, system_pkg())
        else: body_msg(["无可用指令"])
        continue
    # 有可执行指令
    try:
        # 仅有一个可执行指令
        if len(exec_index_list) == 1 or (len(exec_index_list) == 2 and try_df_method == True):
            method_index = exec_index_list[0]
            # 尝试执行默认method
            if try_df_method == True and len(exec_index_list) == 1:
                if df_exec_method_index != None:
                    return_tuple = method_list[df_exec_method_index].proceed(df_cmd_list, main_tasker_list, system_pkg())
                else: # 执行非默认设置method
                    return_tuple = method_list[method_index].proceed(main_cmd_list, main_tasker_list, system_pkg())
            # 一般执行method
            else:
                # 使用非默认method
                try: method_index = exec_index_list[1] if exec_index_list[1] != df_exec_method_index else exec_index_list[0]
                except IndexError: method_index = exec_index_list[0]
                return_tuple = method_list[method_index].proceed(main_cmd_list, main_tasker_list, system_pkg())
            proceed_condition, proceed_return = return_tuple[0], return_tuple[1]
        # 有多个可执行指令
        else:
            table_analyze_result(cmd_analyse_list, exec_index_list, system_pkg(), start_index = 1)
            user_input = normal_input("输入索引")
            if user_input == EXIT: continue
            method_index = convert_to_int(user_input)
            # 输入非int字符串
            if method_index == None:
                system_msg(f"\"{user_input}\"不是一个整数")
                continue
            # 输入int字符串
            else:
                if not (method_index in range(1, len(exec_index_list) + 1)):
                    system_msg(f"\"{method_index}\"不在列出的索引内")
                    continue
            # 确认可用索引
            return_tuple = method_list[exec_index_list[method_index - 1]].proceed(main_cmd_list, main_tasker_list, system_pkg())
            proceed_condition, proceed_return = return_tuple[0], return_tuple[1]
    # 捕捉报错信息
    except:
        exception_msg = traceback.format_exc()
        proceed_condition, proceed_return = CONDITION_FAIL, "Exception"
        exception = True
    # 执行指令后
    cmd_donetime = YYYY_MM_DD_HH_MM_SS()
    log_dir = join(working_dir, f"log")
    log_filename = f"log_{cmd_proceed_date}.txt"
    proceed_info_list = [method_list[method_index], proceed_condition, proceed_return]
    if proceed_condition == CONDITION_SUCCESS:
        normal_log([cmd_proceed_time, cmd_donetime], main_cmd_list, proceed_info_list, log_dir, log_filename) # 写入日志文件
    elif proceed_condition == CONDITION_FAIL:
        error_msg(proceed_return)
        normal_log([cmd_proceed_time, cmd_donetime], main_cmd_list, proceed_info_list, log_dir, log_filename) # 写入日志文件
    else:
        error_msg("请检查程序是否有返回状态值")
    # 程序报错判断
    if exception == True:
        error_msg("运行出现错误，展示错误信息")
        body_msg(exception_msg.split("\n"))
        error_log_filename = f"exception_{YYYY_MM_DD_HH_MM_SS()}.txt"
        error_log(exception_msg, error_log_dir, error_log_filename) # 写入错误日志
        system_msg(f"错误信息保存至{join(error_log_dir, error_log_filename)}")
    # 自动保存pkl文件
    if settings_dict["AUTO_SAVE"] == True:
        save_pkl(main_tasker_list, main_pkl_dir)
        tips_msg("--------已保存pkl文件--------")
    # 自动备份pkl文件
    if settings_dict["AUTO_BACKUP"] == True:
        main_tasker_list.sort(key=attrgetter("tasker_label"))
        backup_pkl(main_tasker_list, f"{join(working_dir, "backup_pkl")}", system_pkg(), interval = settings_dict["BACKUP_INTERVAL"], backup_total = settings_dict["BACKUP_TOTAL"])
    # 输出空行
    normal_msg("")

# 主程序--------+--------+--------+--------+--------+--------+--------+--------+ End