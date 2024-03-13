from .function import get_list_width
from .function import count_chinese_char

def system_msg(msg_str):
    """输出系统提示消息，白色
    
    接收一个普通字符串"""
    print(f"\u001b[1;31;37m[System]{msg_str}\u001b[0;0m")

def error_msg(msg_str): # 红色，加粗
    """输出错误提示信息，红色

    接收一个普通字符串"""
    print(f"\u001b[1;31;40m[Error]{msg_str}\u001b[0;0m")

def tips_msg(msg_str): # 绿色
    """输出提示信息，绿色
    
    接收一个普通字符串"""
    print(f"\u001b[0;32;40m[Tips]{msg_str}\u001b[0;0m")

def table_msg(msg_list:list, heading = False):
    """以表格形式输出列表
    
    列表每项组合元素数需相同，以列表第一个元素（列表）为参照"""
    columns_count = len(msg_list[0])
    # 处理表格中每项宽度
    width_list, max_width_list = get_list_width(msg_list)
    for i in range(0, len(max_width_list)):
        append_width = max_width_list[i] % 4
        if append_width != 0:
            max_width_list[i] = max_width_list[i] + 4 - append_width
    # 表格分割栏
    combine_list = []
    for i in range(0, columns_count):
        combine_list.append("-" * max_width_list[i])
    middle_str = "+".join(combine_list)
    separate_line = f"+{middle_str}+"
    # 打印表格起始栏
    print(separate_line)
    # 打印表格第一行
    combine_list = []
    for i in range(0, columns_count):
        blank = msg_list[0][i] + " " * (max_width_list[i] - width_list[0][i])
        combine_list.append(blank)
    middle_str = "|".join(combine_list)
    print(f"|{middle_str}|")
    # 打印标题下分割栏
    if heading == True:
        print(separate_line)
    # 打印列表剩余内容
    list_length = len(msg_list)
    if list_length > 1:
        for i in range(1, list_length):
            combine_list = []
            for k in range(0, columns_count):
                blank = msg_list[i][k] + " " * (max_width_list[k] - width_list[i][k])
                combine_list.append(blank)
            middle_str = "|".join(combine_list)
            print(f"|{middle_str}|")
    # 打印表格结束栏
    print(separate_line)

def head_msg(msg_str): # 带框
    """输出带框的标题
    
    标题框长度为字符串长度，不扩展"""
    chinese_count = count_chinese_char(msg_str)
    middle_str = "-" * (len(msg_str) + chinese_count)
    separate_line = f"+{middle_str}+"
    print(separate_line)
    blank = msg_str
    print(f"|{blank}|")
    print(separate_line)

def body_msg(msg_list:list): # 每行缩进

    """输出每行缩进的消息，左侧加一竖线
    
    接收一个列表，即使只有一个字符串"""
    for i in msg_list:
        print(f"\t|{i}")

def normal_msg(msg_str):
    """输出普通消息
    
    接收一个普通字符串"""
    print(msg_str)