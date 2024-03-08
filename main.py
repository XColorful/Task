from os import chdir
from os.path import dirname, abspath, exists
working_dir = dirname(abspath(__file__))
chdir(working_dir) # 切换工作路径至当前文件目录

try:
    with open(f".\\pkl_dir.txt", "r", encoding = "utf-8") as f:
        main_pkl_dir = f.readline()
        if not exists(main_pkl_dir): raise
except:
    main_pkl_dir = working_dir + "main_container_list.pkl" # 工作目录

import default_pkg.message as df_msg
import default_pkg.io as df_io
import default_pkg.method as df_method
import default_pkg.container as df_container
import default_pkg.task as df_task
import default_pkg.class_func as df_class_func
# 读取默认message库
system_msg = df_msg.system_msg
error_msg = df_msg.error_msg
tips_msg = df_msg.tips_msg
table_msg = df_msg.table_msg
head_msg = df_msg.head_msg
body_msg = df_msg.body_msg
normal_msg = df_msg.normal_msg
# 读取默认I/O库
command_input = df_io.command_input
normal_input = df_io.normal_input
strict_input = df_io.strict_input
block_input = df_io.block_input
# 读取主程序method类，用于执行主程序指令
method_list = []
default_method = df_method.default_method
method_list.append(default_method())
# 读取container类, task类模板
default_container = df_container.default_container
default_task = df_task.default_task
default_container_template_list = [default_container]
default_task_template_list = [default_task]
extra_container_template_list = []
extra_task_template_list = []
# 读取class_func
class_func = []
default_class_func = df_class_func.default_container_func
class_func.append(default_class_func)
# 初始化变量
TYPE_DEFAULT_CONTAINER = "Default_Template"
TYPE_EXTRA_CONTAINER = "Extra_Template"
TYPE_DEFAULT_METHOD = "Default_Template"
TYPE_EXTRA_METHOD = "Extra_Template"
TYPE_DEFAULT_CLASS_FUNC = "default_container_func"
TYPE_EXTRA_CLASS_FUNC = "extra_container_func"
CONDITION_SUCCESS = True # 正常运行
CONDITION_FAIL = False # 程序报错
BLOCK_LIST = ["|||", "\t"]
EXIT = "exit"
# settings管理器
SHOW_TIPS = True
SETTING_AUTO_SAVE = True

# 读取extra内容
# method.py
import extra.school_task.method as ex_school_task_method
school_task_method = ex_school_task_method.school_task_method
method_list.append(school_task_method())
import extra.container_manager.method as ex_container_manager_method
default_container_manager = ex_container_manager_method.default_container_manager
method_list.append(default_container_manager())
# class_func.py
import extra.categorize.class_func as ex_categorize_method
categorize_task = ex_categorize_method.categorize_task
class_func.append(categorize_task)



def system_pkg():
    return {"system_msg":system_msg, "error_msg":error_msg, "tips_msg":tips_msg, "table_msg":table_msg, "head_msg":head_msg, "body_msg":body_msg, "normal_msg":normal_msg,
            "EXIT":EXIT,
            "command_input":command_input, "normal_input":normal_input, "strict_input":strict_input, "block_input":block_input,
            "CONDITION_SUCCESS":CONDITION_SUCCESS, "CONDITION_FAIL":CONDITION_FAIL, "BLOCK_LIST":BLOCK_LIST,
            "TYPE_DEFAULT_CONTAINER":TYPE_DEFAULT_CONTAINER, "TYPE_EXTRA_CONTAINER":TYPE_EXTRA_CONTAINER, "TYPE_DEFAULT_METHOD":TYPE_DEFAULT_METHOD, "TYPE_EXTRA_METHOD":TYPE_EXTRA_METHOD, "TYPE_DEFAULT_CLASS_FUNC":TYPE_DEFAULT_CLASS_FUNC, "TYPE_EXTRA_CLASS_FUNC":TYPE_EXTRA_CLASS_FUNC,
            "default_container_template_list":default_container_template_list, "extra_container_template_list":extra_container_template_list,
            "default_task_template_list":default_task_template_list, "extra_task_template_list":extra_task_template_list,
            "class_func":class_func
            }

# 主程序
from function import convert_to_int, read_from_pkl, save_to_pkl, error_log, YYYY_MM_DD, YYYY_MM_DD_HH_MM_SS, normal_log, table_analyze_result
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
    save_to_pkl(main_container_list, main_pkl_dir)
if main_container_list == []:
    normal_msg("注：主容器列表为空")

# 程序主循环
while True:
    main_command_list = command_input("\u001b[1;37;40m[command]>\u001b[0;0m")
    if main_command_list[0] == system_pkg()["EXIT"]: exit()
    if main_command_list[0] == "":
        if main_command_list[1] != "":
            system_msg("请先输入指令，或尝试去除最先输入的空格重新输入")
        continue
    # 初始化变量
    command_analyze_result_list = []
    executable_index_list = []
    failed_index_list = []
    command_proceed_time = YYYY_MM_DD_HH_MM_SS()
    command_proceed_date = YYYY_MM_DD()
    proceed_condition = None
    exception = False
    # 遍历可执行的method
    for method_index in range(0, len(method_list)):
        analyze_result = method_list[method_index].analyze(main_command_list, main_container_list, system_pkg())
        command_analyze_result_list.append(analyze_result[1])
        if analyze_result[0] == CONDITION_SUCCESS:
            executable_index_list.append(method_index)
        else:
            failed_index_list.append(method_index)
    
    if executable_index_list == []: # 无可执行指令
        system_msg(f"指令\"{main_command_list[0]}\"不存在")
        if failed_index_list != []:
            if normal_input("展示所有可用指令(y/n)").lower() != "y": continue
            table_analyze_result(command_analyze_result_list, failed_index_list, system_pkg())
            continue
        else:
            body_msg(["无可用指令"])
            continue
    else: # 有可执行指令
        try: # 防止程序退出
            if len(executable_index_list) == 1: # 仅有一个可执行指令
                method_index = executable_index_list[0]
                return_tuple = method_list[method_index].proceed(main_command_list, main_container_list, system_pkg())
                proceed_condition = return_tuple[0]
                proceed_return = return_tuple[1]
            else: # 有多个可执行指令
                table_analyze_result(command_analyze_result_list, executable_index_list, system_pkg())
                user_input = normal_input("输入索引")
                if user_input == EXIT: continue
                method_index = convert_to_int(user_input)
                if method_index == None: # 输入非int字符串
                    system_msg(f"\"{user_input}\"不是一个整数")
                    continue
                else: # 输入int字符串
                    if not (method_index in executable_index_list):
                        system_msg(f"\"{method_index}\"不在列出的索引内")
                        continue
                # 确认可用索引
                return_tuple = method_list[method_index].proceed(main_command_list, main_container_list, system_pkg())
                proceed_condition = return_tuple[0]
                proceed_return = return_tuple[1]
        except: # 捕捉报错信息
            exception_message = traceback.format_exc()
            proceed_return = "Exception"
            exception = True
    # 执行指令后
    command_done_time = YYYY_MM_DD_HH_MM_SS()
    proceed_info_list = [method_list[method_index], proceed_condition, proceed_return]
    log_folder_dir = join(working_dir, f"log")
    log_file_name = f"log_{command_proceed_date}.txt"
    if proceed_condition == CONDITION_SUCCESS:
        normal_log([command_proceed_time, command_done_time], main_command_list, proceed_info_list, log_folder_dir, log_file_name) # 写入日志文件
    elif proceed_condition == CONDITION_FAIL:
        error_msg(proceed_return)
        normal_log([command_proceed_time, command_done_time], main_command_list, proceed_info_list, log_folder_dir, log_file_name) # 写入日志文件
    else:
        error_msg("请检查程序是否有返回状态值")
    # 程序报错判断
    if exception == True:
        error_msg("运行出现错误，展示错误信息")
        body_msg(exception_message.split("\n"))
        error_log_file_name = f"exception_{YYYY_MM_DD_HH_MM_SS()}.txt"
        error_log_folder_dir = join(working_dir, "error_log")
        error_log(exception_message, error_log_folder_dir, error_log_file_name) # 写入错误日志
        system_msg(f"错误信息保存至{join(error_log_folder_dir, error_log_file_name)}")
    # 检查自动保存是否开启
    if SETTING_AUTO_SAVE == True:
        main_container_list.sort(key=attrgetter("container_label"))
        save_to_pkl(main_container_list, main_pkl_dir)