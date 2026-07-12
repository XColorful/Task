from os import makedirs
from os.path import isdir, join

def is_valid_input(input_str:str) -> bool:
    """检测首尾是否包含"|"，如有则返回False"""
    try:
        if input_str[0] == "|" or input_str[-1] == "|":
            return False
    except IndexError: return True
    except TypeError: return False
    return True

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

def convert_to_int(s:str):
    """返回字符串是否能转换为int，不修改原字符串
    
    接收一个普通字符串，转换失败则返回None"""
    try:
        return int(s)
    except ValueError:
        return None
    except TypeError:
        return None

def analyze_interface_input(str_input) -> dict:
    """返回dict{"cmd":str, "parameter":str}"""
    if str_input == "":
        return {"cmd":"", "parameter":""}
    elif str_input[0] == "+":
        try:
            str_input = str_input[1:]
            return {"cmd":"search", "parameter":str_input}
        except IndexError: return {"cmd":"search", "parameter":""}
    elif str_input[0] == "/":
        try:
            str_input = str_input[1:]
        except IndexError: return {"cmd":"", "parameter":""}
    # 一般输入
    str_input = str_input.split(" ", 1)
    try:
        parameter = str_input[1]
    except IndexError: parameter = ""
    
    return {"cmd":str_input[0], "parameter":parameter}

def get_interface_input(name, system_pkg) -> dict | bool:
    while True:
        interface_input = system_pkg["normal_input"](f"{name}")
        input_dict = analyze_interface_input(interface_input)
        if input_dict["cmd"] == "": continue
        elif input_dict["cmd"] == system_pkg["EXIT"]: return False
        
        return input_dict

def input_tasker_attr_input_map(tasker, system_pkg) -> bool:
    """输入attr_input_map并配置，返回bool为输入或取消"""
    
    system_pkg["normal_msg"]("配置attr_input_map")
    system_pkg["body_msg"](["说明：此配置用于使用label_tasker_func添加新label类task时，用快捷字对应已预设的关键字",
                            "注意：重复使用同一快捷字会覆盖原先转换关键字"])
    system_pkg["tips_msg"]("输入格式：快捷字|||转换关键字")
    
    
    inputted = False
    while True:
        input_condition, user_input = system_pkg["block_input"]("输入配置内容")
        if (input_condition == False) or (input_condition == None):
            break
        else: # input_conditon == True
            try:
                attr, map = user_input.split("|||", 1)
            except ValueError:
                system_pkg["system_msg"](f"\"{user_input}\"格式不符")
            
            try:
                tasker.attr_input_map["attr"]
                
                system_pkg["system_msg"](f"快捷字\"{attr}\"已经存在（{attr} -> {tasker.attr_input_map["attr"]}）")
                change_confirm = system_pkg["normal_input"]("是否覆盖(y/n)")
                if change_confirm == system_pkg["EXIT"]:
                    break
                elif change_confirm != "y":
                    system_pkg["system_msg"]("取消更改")
            except KeyError: pass
            
            tasker.attr_input_map["attr"] = map
            system_pkg["system_msg"](f"已更改（{attr} -> {map}）")
            inputted = True
    
    if inputted == False:
        return False
    else:
        return True

def input_tasker_convenient_input(tasker, system_pkg) -> bool:
    """更改便捷输入选项，返回bool为输入或取消"""
    
    system_pkg["normal_msg"]("配置便捷输入选项")
    system_pkg["body_msg"](["说明：此配置用于使用label_tasker_func添加新label类task的标签时，用\" \"代替\"|||\"",
                            "注意：打开此选项将不能输入带空格的标签属性"])
    system_pkg["tips_msg"]("输入\"0\"/\"1\"对应\"关闭\"/\"启用\"该选项")
    
    
    inputted = False
    while True:
        convenient_input = "0" if tasker.convenient_input == False else "1"
        input_condition, user_input = system_pkg["block_input"]("配置选项(当前：{convenient_input})")
        if (input_condition == False) or (input_condition == None):
            break
        else: # input_conditon == True
            if user_input == "1":
                inputted = True
                tasker.convenient_input = True
                system_pkg["system_pkg"]("已启用快捷输入")
            elif user_input == "0":
                inputted = True
                tasker.convenient_input = False
                system_pkg["system_pkg"]("已关闭快捷输入")
            else:
                system_pkg["system_msg"](f"\"{user_input}\"格式不符")
                break
    
    if inputted == False:
        return False
    else:
        return True

def get_search_result_save_dir(cwd, system_pkg):
    try:
        dir = system_pkg["settings_dict"]["LABEL:SEARCH_RESULT_SAVE_DIR"]
        
        if isdir(dir):
            return dir
    except KeyError:
        pass
    
    # 尝试找到当前cwd工作目录下.\package\label
    package_label_dir = join(cwd, ".\\package\\label")
    if isdir(package_label_dir):
        # 如果有，则创建.\package\label\label_data\search_result目录，将完整路径赋值给dir
        dir = join(package_label_dir, "saved_data\\search_result")
        makedirs(dir, exist_ok=True)
    else:
        # 如果没有这个目录，则在当前代码文件目录下创建.\label_data\search_result，将完整路径赋值给dir
        dir = join(cwd, ".\\saved_data\\search_result")
        makedirs(dir, exist_ok=True)
    
    # 用isdir检查dir
    if isdir(dir):
        return dir
    else:
        raise FileNotFoundError(f"Directory {dir} does not exist.")
