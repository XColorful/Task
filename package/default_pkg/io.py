def is_valid_input(input_str:str) -> bool:
    """检测首尾是否包含"|"，如有则返回False"""
    try:
        if input_str[0] == "|" or input_str[-1] == "|":
            return False
    except IndexError: return True
    except TypeError: return False
    return True

def command_input(msg_str = ""):
    """用空格分割输入的指令
    
    最大分割 1 次，返回包含 2 个元素的列表"""
    user_input = input(f"\u001b[1;37;40m[command]{msg_str}>\u001b[0;0m")
    user_input_list = user_input.split(" ", 1)
    if len(user_input_list) < 2:
        user_input_list.append("")
    return user_input_list

def normal_input(msg_str = ""):
    """普通输入
    
    可补充显示的字符串"""
    return input(f"[Input]{msg_str}>")

def strict_input(msg_str = "", block_list = [], system_pkg = {"tips_msg":print}, block_number = True):
    """限制输入，不为空字符串，首项不为空格，首项不为数字，返回元组( True/False ，字符串)
    
    可补充输入提示"""
    try:
        quit_string = system_pkg["EXIT"]
    except KeyError:
        quit_string = "exit"
    
    while True:
        block = False
        user_input = input(f"[Input]{msg_str}>")
        if user_input == quit_string:
            return (False, "取消严格输入")
        if user_input == "":
            continue
        if user_input[0] == " ":
            system_pkg["tips_msg"](f"不能以空格开头")
            continue
        if block_number == True:
            if user_input[0].isdecimal():
                system_pkg["tips_msg"](f"不能以数字开头")
                continue
        for block_char in block_list:
            if block_char in user_input:
                system_pkg["tips_msg"](f"不能包含\"{block_char}\"")
                block = True
                break
        if not is_valid_input(user_input):
            system_pkg["tips_msg"](f"尝试去除首尾的\"|\"")
            block = True
        if block == True: continue
        return (True, user_input)
        
def block_input(msg_str = "", block_list = [], system_pkg = {"tips_msg":print}, block_number = True):
    """对非空输入内容进行限制，首项不为空格，首项不为数字，返回元组( True/False/None ，字符串)
    
    可补充输入提示"""
    try:
        quit_string = system_pkg["EXIT"]
    except KeyError:
        quit_string = "exit"
    
    while True:
        block = False
        user_input = input(f"[Input]{msg_str}>")
        if user_input == quit_string:
            return (False, "取消严格输入")
        if user_input == "":
            return (None, "取消严格输入")
        if user_input[0] == " ":
            system_pkg["tips_msg"](f"不能以空格开头")
            continue
        if block_number == True:
            if user_input[0].isdecimal():
                system_pkg["tips_msg"](f"不能以数字开头")
                continue
        for block_char in block_list:
            if block_char in user_input:
                system_pkg["tips_msg"](f"不能包含\"{block_char}\"")
                block = True
                break
        if not is_valid_input(user_input):
            system_pkg["tips_msg"](f"尝试去除首尾的\"|\"")
            block = True
        if block == True: continue
        return (True, user_input)