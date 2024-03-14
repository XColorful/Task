from os import chdir
from os.path import dirname, abspath, exists
working_dir = dirname(abspath(__file__))
chdir(working_dir) # 切换工作路径至当前文件目录

try:
    with open(f".\\pkl_dir.txt", "r", encoding = "utf-8") as f:
        main_pkl_dir = f.readline()
        if not exists(main_pkl_dir): raise
except: main_pkl_dir = working_dir + "main_container_list.pkl" # 工作目录

# 初始化变量
from const import *
# settings管理器
"""
    日后填坑
"""
SHOW_TIPS = True
SETTING_AUTO_SAVE = True
# 初始化系统变量
class_func_list = []
default_container_template_list = []
extra_container_template_list = []
io_list = []
message_list = []
method_list = []
default_task_template_list = []
extra_task_template_list = []
# 读取package内容
from importlib import import_module
def package_loader(package_name, show = True):
    try: pkg = import_module(f'package.{package_name}') # package.{package_name}
    except ModuleNotFoundError:
        if show == True: system_msg(f"包\"{package_name}\"不存在")
        return None
    try: package_dict = pkg.package_dict
    except AttributeError:
        if show == True: system_msg(f"包\"{package_name}\"缺少package_dict")
        return None
    global class_func_list
    try: class_func_list += package_dict["class_func"]
    except KeyError: pass
    global default_container_template_list
    try: default_container_template_list += package_dict["default_container"]
    except KeyError: pass
    global extra_container_template_list
    try: extra_container_template_list += package_dict["extra_container"]
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
    global default_task_template_list
    try: default_task_template_list += package_dict["default_task"]
    except KeyError: pass
    global extra_task_template_list
    try: extra_task_template_list += package_dict["extra_task"]
    except KeyError: pass
    # 确保已经有system_msg才调整show = True
    if show == True: system_msg(f"已读取\"{package_name}\"")
    return None
# 读取默认包
package_loader("default_pkg", show = False)
# io_list
command_input = io_list[0]["command_input"]
normal_input = io_list[0]["normal_input"]
strict_input = io_list[0]["strict_input"]
block_input = io_list[0]["block_input"]
# message
system_msg = message_list[0]["system_msg"]
error_msg = message_list[0]["error_msg"]
tips_msg = message_list[0]["tips_msg"]
table_msg = message_list[0]["table_msg"]
head_msg = message_list[0]["head_msg"]
body_msg = message_list[0]["body_msg"]
normal_msg = message_list[0]["normal_msg"]
# 读取extra包
"""
    日后填坑：./package.txt，指定添加的package
"""
package_loader("categorize")
package_loader("container_manager")
package_loader("school_task")
package_loader("account")

def system_pkg():
    return {"system_msg":system_msg, "error_msg":error_msg, "tips_msg":tips_msg, "table_msg":table_msg, "head_msg":head_msg, "body_msg":body_msg, "normal_msg":normal_msg,
            "EXIT":EXIT,
            "command_input":command_input, "normal_input":normal_input, "strict_input":strict_input, "block_input":block_input,
            "CONDITION_SUCCESS":CONDITION_SUCCESS, "CONDITION_FAIL":CONDITION_FAIL, "BLOCK_LIST":BLOCK_LIST,
            "TYPE_DEFAULT_CONTAINER":TYPE_DEFAULT_CONTAINER, "TYPE_EXTRA_CONTAINER":TYPE_EXTRA_CONTAINER, "TYPE_DEFAULT_METHOD":TYPE_DEFAULT_METHOD, "TYPE_EXTRA_METHOD":TYPE_EXTRA_METHOD, "TYPE_DEFAULT_CLASS_FUNC":TYPE_DEFAULT_CLASS_FUNC, "TYPE_EXTRA_CLASS_FUNC":TYPE_EXTRA_CLASS_FUNC,
            "default_container_template_list":default_container_template_list, "extra_container_template_list":extra_container_template_list,
            "default_task_template_list":default_task_template_list, "extra_task_template_list":extra_task_template_list,
            "class_func_list":class_func_list
            }

# 主程序
from function import convert_to_int, read_from_pkl, save_pkl, error_log, YYYY_MM_DD, YYYY_MM_DD_HH_MM_SS, backup_pkl, normal_log, table_analyze_result
from os.path import join
import traceback
from operator import attrgetter
head_msg("Task - Version 1.0")
body_msg(["By Xiao Colorful"])
# tips_msg("To -> settings for more help.")

# 读取主容器列表
main_container_list = []
try:
    main_container_list = read_from_pkl(main_pkl_dir)
except:
    system_msg("没有可用的pkl数据文件")
    save_pkl(main_container_list, main_pkl_dir)
if main_container_list == []:
    normal_msg("注：主容器列表为空")

# 程序主循环
while True:
    main_cmd_list = command_input("main")
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
    cmd_proceed_date = YYYY_MM_DD()
    proceed_condition = None
    exception = False
    # 遍历可执行的method
    for method_index in range(0, len(method_list)):
        analyze_result = method_list[method_index].analyze(main_cmd_list, main_container_list, system_pkg())
        cmd_analyse_list.append(analyze_result[1])
        if analyze_result[0] == CONDITION_SUCCESS:
            exec_index_list.append(method_index)
        else:
            fail_index_list.append(method_index)
    # 判断是否有可执行指令
    # 无可执行指令
    if exec_index_list == []:
        system_msg(f"指令\"{main_cmd_list[0]}\"不存在")
        if fail_index_list != []:
            if normal_input("展示所有可用指令(y/n)").lower() != "y": continue
            table_analyze_result(cmd_analyse_list, fail_index_list, system_pkg())
            continue
        else:
            body_msg(["无可用指令"])
            continue
    # 有可执行指令
    else:
        try:
            # 仅有一个可执行指令
            if len(exec_index_list) == 1:
                method_index = exec_index_list[0]
                return_tuple = method_list[method_index].proceed(main_cmd_list, main_container_list, system_pkg())
                proceed_condition = return_tuple[0]
                proceed_return = return_tuple[1]
            # 有多个可执行指令
            else:
                table_analyze_result(cmd_analyse_list, exec_index_list, system_pkg())
                user_input = normal_input("输入索引")
                if user_input == EXIT: continue
                method_index = convert_to_int(user_input)
                # 输入非int字符串
                if method_index == None:
                    system_msg(f"\"{user_input}\"不是一个整数")
                    continue
                # 输入int字符串
                else:
                    if not (method_index in exec_index_list):
                        system_msg(f"\"{method_index}\"不在列出的索引内")
                        continue
                # 确认可用索引
                return_tuple = method_list[method_index].proceed(main_cmd_list, main_container_list, system_pkg())
                proceed_condition = return_tuple[0]
                proceed_return = return_tuple[1]
        # 捕捉报错信息
        except:
            exception_msg = traceback.format_exc()
            proceed_return = "Exception"
            exception = True
    # 执行指令后
    command_done_time = YYYY_MM_DD_HH_MM_SS()
    proceed_info_list = [method_list[method_index], proceed_condition, proceed_return]
    log_dir = join(working_dir, f"log")
    log_filename = f"log_{cmd_proceed_date}.txt"
    if proceed_condition == CONDITION_SUCCESS:
        normal_log([cmd_proceed_time, command_done_time], main_cmd_list, proceed_info_list, log_dir, log_filename) # 写入日志文件
    elif proceed_condition == CONDITION_FAIL:
        error_msg(proceed_return)
        normal_log([cmd_proceed_time, command_done_time], main_cmd_list, proceed_info_list, log_dir, log_filename) # 写入日志文件
    else:
        error_msg("请检查程序是否有返回状态值")
    # 程序报错判断
    if exception == True:
        error_msg("运行出现错误，展示错误信息")
        body_msg(exception_msg.split("\n"))
        error_log_filename = f"exception_{YYYY_MM_DD_HH_MM_SS()}.txt"
        error_log_dir = join(working_dir, "error_log")
        error_log(exception_msg, error_log_dir, error_log_filename) # 写入错误日志
        system_msg(f"错误信息保存至{join(error_log_dir, error_log_filename)}")
    # 常规保存
    save_pkl(main_container_list, main_pkl_dir)
    tips_msg("--------已自动备份pkl文件--------")
    # 检查自动保存是否开启
    if SETTING_AUTO_SAVE == True:
        main_container_list.sort(key=attrgetter("container_label"))
        backup_pkl(main_container_list, f"{join(working_dir, "backup_pkl")}", system_pkg(), interval = 3, save_file = 3)