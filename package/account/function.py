from random import choices, sample
from pyperclip import copy as py_cp

def convert_to_int(s:str):
    """返回字符串是否能转换为int，不修改原字符串
    
    接收一个普通字符串，转换失败则返回None"""
    try:
        return int(s)
    except ValueError:
        return None
    except TypeError:
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

def get_select_index_dict(user_input, tasker) -> dict:
    """搜索account_type, label, description, linked_account, other_info"""
    index_dict = {"account_type":[],
                  "label":[],
                  "description":[],
                  "linked_account":[],
                  "other_info":[]}
    for index, account_task in enumerate(tasker.task_list):
        if account_task.version != "account": continue
        
        if user_input in account_task.account_type: index_dict["account_type"].append(index)
        if user_input in account_task.label: index_dict["label"].append(index)
        for description in account_task.dict["description"]:
            if user_input in description:
                index_dict["description"].append(index)
                break
        for linked_account in account_task.dict["linked_account"]:
            if user_input in linked_account:
                index_dict["linked_account"].append(index)
                break
        for other_info in account_task.dict["other_info"]:
            if user_input in other_info:
                index_dict["other_info"].append(index)
                break
    return index_dict

def count_select_index_dict(index_dict) -> int:
    """输入字典由get_select_index_dict生成"""
    return \
        len(index_dict["account_type"]) + \
        len(index_dict["label"]) + \
        len(index_dict["description"]) + \
        len(index_dict["linked_account"]) + \
        len(index_dict["other_info"])

def get_the_only_index(index_dict) -> int:
    """输入字典由get_select_index_dict生成"""
    for key in ["account_type", "label", "description", "linked_account", "other_info"]:
        if index_dict[key] != []:
            return index_dict[key][0]
    raise

def get_all_index(index_dict) -> list[int]:
    """输入字典由get_select_index_dict生成"""
    all_index_list = []
    for key in ["account_type", "label", "description", "linked_account", "other_info"]:
        all_index_list += index_dict[key]
    return all_index_list

def show_account_with_index(account_task, show_index, system_pkg):
    account_label = f"（{account_task.label}）" if account_task.label != "" else ""
    
    account_description = []
    if account_task.dict["description"] != []:
        account_description = ["description："]
        for description in account_task.dict["description"]:
            account_description.append(f"\t{description}")
    
    account_linked_account = []
    if account_task.dict["linked_account"] != []:
        account_linked_account = ["linked_account："]
        for linked_account in account_task.dict["linked_account"]:
            account_linked_account.append(f"\t{linked_account}")
    
    account_other_info = []
    if account_task.dict["other_info"] != []:
        account_other_info = ["other_info："]
        for other_info in account_task.dict["other_info"]:
            account_other_info.append(f"\t{other_info}")
    
    system_pkg["normal_msg"](f"[{show_index}]|{account_task.account_type}{account_label}")
    body_list = [f"create_date：{account_task.create_date}"]
    body_list += account_description
    body_list += account_linked_account
    body_list += account_other_info
    
    system_pkg["body_msg"](body_list)

def show_candidate_with_index(index_dict, tasker, system_pkg):
    """输入字典由get_select_index_dict生成"""
    show_index = 0
    for key in ["account_type", "label", "description", "linked_account", "other_info"]:
        if index_dict[key] != []:
            system_pkg["head_msg"](f"{key}搜索结果：{len(index_dict[key])}")
            
            for account_index in index_dict[key]:
                show_account_with_index(tasker.task_list[account_index], show_index, system_pkg)
                show_index += 1

def select_from_index_list(index_list, system_pkg) -> int | None:
    user_input = system_pkg["normal_input"]("输入索引")
    if user_input == system_pkg["EXIT"]: return None
    
    convert_result = convert_to_int(user_input)
    if convert_result == None:
        system_pkg["system_msg"](f"索引\"{user_input}\"格式错误")
        return None
    else:
        try:
            return index_list[convert_result]
        except IndexError:
            system_pkg["system_msg"](f"索引{user_input}不在范围内")
            return None
    
def choose_from_index_dict(index_dict, tasker, system_pkg) -> int | None:
    all_index_list = get_all_index(index_dict)
    show_candidate_with_index(index_dict, tasker, system_pkg)
    
    select_index = select_from_index_list(all_index_list, system_pkg)
    if select_index == None: return None
    else: return select_index

def is_valid_index_in_tasker(index:int, tasker) -> bool:
    if type(index) != int:
        return False
    try:
        tasker.task_list[index]
        return True
    except IndexError:
        return False

def select_account_task(user_input: str | int, tasker, system_pkg) -> int | None:
    """返回值为索引或None"""
    if is_valid_index_in_tasker(user_input, tasker):
        return user_input
    else:
        if user_input == "":
            user_input = system_pkg["normal_input"]("输入内容选定task")
        if user_input == system_pkg["EXIT"]: return None
        
        index_dict = get_select_index_dict(user_input, tasker)

        total_index = count_select_index_dict(index_dict)
    
    if total_index == 0: return None
    elif total_index == 1:
        return get_the_only_index(index_dict)
    else:
        return choose_from_index_dict(index_dict, tasker, system_pkg)

def show_account_detail(account_task, system_pkg) -> None:
    # 单项信息
    account_label = f"（{account_task.label}）" if (account_task.label != "" and \
                                                    account_task.label != account_task.account_type) \
                                                else ""
    system_pkg["head_msg"](f"{account_task.account_type}{account_label}")
    system_pkg["body_msg"]([f"create_date：{account_task.create_date}",
                            f"last_date：{account_task.last_date}",
                            f"password：{account_task.password[:4] + "*" * (len(account_task.password) - 4)}"])

    # description
    if account_task.dict["description"] != []:
        system_pkg["normal_msg"]("description：")
        account_description = []
        for description in account_task.dict["description"]:
            account_description.append(description)
        system_pkg["body_msg"](account_description)
    
    # login_name
    if account_task.dict["login_name"] != []:
        show_index = 1
        system_pkg["normal_msg"]("login_name：")
        account_login_name = []
        for login_name in account_task.dict["login_name"]:
            account_login_name.append(f"[{show_index}]|{login_name}")
            show_index += 1
        system_pkg["body_msg"](account_login_name)
    
    # verified_phone
    if account_task.dict["verified_phone"] != []:
        show_index = 1
        system_pkg["normal_msg"]("verified_phone：")
        account_verified_phone = []
        for verified_phone in account_task.dict["verified_phone"]:
            account_verified_phone.append(f"[{show_index}]|{verified_phone}")
            show_index += 1
        system_pkg["body_msg"](account_verified_phone)

    # verified_email
    if account_task.dict["verified_email"] != []:
        show_index = 1
        system_pkg["normal_msg"]("verified_email：")
        account_verified_email = []
        for verified_email in account_task.dict["verified_email"]:
            account_verified_email.append(f"[{show_index}]|{verified_email}")
            show_index += 1
        system_pkg["body_msg"](account_verified_email)
    
    # linked_account
    if account_task.dict["linked_account"] != []:
        show_index = 1
        system_pkg["normal_msg"]("linked_account：")
        account_linked_account = []
        for linked_account in account_task.dict["linked_account"]:
            account_linked_account.append(f"[{show_index}]|{linked_account}")
            show_index += 1
        system_pkg["body_msg"](account_linked_account)
    
    # secure_question
    if account_task.dict["secure_question"] != []:
        show_index = 1
        system_pkg["normal_msg"]("secure_question：")
        account_secure_question = []
        for secure_question in account_task.dict["secure_question"]:
            account_secure_question.append(f"[{show_index}]|{secure_question}")
            show_index += 1
        system_pkg["body_msg"](account_secure_question)
    
    # other_info
    if account_task.dict["other_info"] != []:
        show_index = 1
        system_pkg["normal_msg"]("other_info：")
        account_other_info = []
        for other_info in account_task.dict["other_info"]:
            account_other_info.append(f"[{show_index}]|{other_info}")
            show_index += 1
        system_pkg["body_msg"](account_other_info)
    
    # password_history
    if account_task.dict["password_history"] != []:
        show_index = 1
        system_pkg["normal_msg"]("password_history：")
        account_password_history = []
        for password_history in account_task.dict["password_history"]:
            account_password_history.append(f"[{show_index}]|{password_history}")
            show_index += 1
        system_pkg["body_msg"](account_password_history)

    return None


def is_valied_input(user_input, system_pkg) -> bool:
    """判断是否头尾包含"|"，系统BLOCK_LIST"""
    if user_input == "": return False
    else:
        if user_input[0] == "|": return False
        if user_input[-1] == "|": return False
    for block_str in system_pkg["BLOCK_LIST"]:
        if block_str in user_input: return False
    return True

def get_account_attr_input(attr_name:str, system_pkg) -> str | bool:
    """获取account类task属性的输入，为字符串
    
    返回str -> 正确输入
    
    返回False -> 取消输入/失败
    
    返回None -> 输入为空"""
    block_list = system_pkg["BLOCK_LIST"]
    input_condition, user_input = system_pkg["block_input"](f"输入{attr_name}", block_list = block_list, block_number = False)
    if input_condition == False: return False
    elif input_condition == None: return False
    else:
        if not is_valied_input(user_input, system_pkg):
            system_pkg["system_msg"](f"\"{user_input}\"不符合输入，尝试去除\"|\"")
            return False
        return user_input

def get_account_dict_input(attr_name, system_pkg) -> list[str] | bool:
    """获取account类task属性的输入，为list[str]
    
    返回list[str] -> 正确输入
    
    返回False -> 取消输入/失败
    
    返回None -> 输入为空"""
    system_pkg["tips_msg"]("用\"|||\"分隔每一项")
    block_list = system_pkg["BLOCK_LIST"]
    input_condition, user_input = system_pkg["block_input"](f"输入{attr_name}", block_list = block_list, block_number = False)
    if input_condition == False: return False
    elif input_condition == None: return False
    else:
        user_input = user_input.split("|||")
        for i in user_input:
            if not is_valied_input(i, system_pkg):
                system_pkg["system_msg"](f"项\"{i}\"不符合输入，尝试去除\"|\"")
                return False
        return user_input

def input_account_type(system_pkg) -> str | None:
    user_input = get_account_attr_input("account_type", system_pkg)
    if user_input == False: return None
    elif user_input == None: return None
    else: return user_input

def change_account_type(account_task, system_pkg) -> None:
    py_cp(account_task.account_type)
    system_pkg["normal_msg"](f"\"账号类型\"已复制到剪贴板")
    
    user_input = input_account_type(system_pkg)
    if (user_input == False) or (user_input == None): return None
    else:
        account_task.account_type = user_input
        return None

def input_label(system_pkg) -> str | None:
    user_input = get_account_attr_input("label", system_pkg)
    if user_input == False: return None
    elif user_input == None: return None
    else: return user_input

def change_label(account_task, system_pkg) -> None:
    py_cp(account_task.label)
    system_pkg["normal_msg"](f"\"标签\"已复制到剪贴板")
    
    user_input = input_label(system_pkg)
    if (user_input == False) or (user_input == None): return None
    else:
        account_task.label = user_input
        return None

def input_password(system_pkg) -> str | None:
    user_input = get_account_attr_input("password", system_pkg)
    if user_input == False: return None
    elif user_input == None: return None
    else: return user_input

def change_password(account_task, system_pkg) -> None:
    py_cp(account_task.password)
    system_pkg["normal_msg"](f"\"password\"已复制到剪贴板")
    
    user_input = input_password(system_pkg)
    if (user_input == False) or (user_input == None): return None
    else:
        account_task.password = user_input
        return None

def input_description(system_pkg) -> list[str] | None:
    user_input = get_account_dict_input("description", system_pkg)
    if user_input == False: return None
    elif user_input == None: return None
    else: return user_input

def copy_item_str(dict_key, account_task, system_pkg):
    copy_str = ""
    try:
        copy_str += account_task.dict[dict_key][0]
        for item in account_task.dict[dict_key][1:]:
            copy_str += f"|||{item}"
    except IndexError: pass
    except KeyError:
        system_pkg["error_msg"](f"值{dict_key}错误，请检查代码")
        return None
    
    py_cp(copy_str)
    system_pkg["normal_msg"](f"\"{dict_key}\"已复制到剪贴板")

def change_description(account_task, system_pkg) -> None:
    copy_item_str("description", account_task, system_pkg)
    
    user_input = input_description(system_pkg)
    if (user_input == False) or (user_input == None): return None
    else:
        account_task.dict["description"] = user_input
        return None

def input_login_name(system_pkg) -> list[str] | None:
    user_input = get_account_dict_input("login_name", system_pkg)
    if user_input == False: return None
    elif user_input == None: return None
    else: return user_input

def change_login_name(account_task, system_pkg) -> None:
    copy_item_str("login_name", account_task, system_pkg)
    
    user_input = input_login_name(system_pkg)
    if (user_input == False) or (user_input == None): return None
    else:
        account_task.dict["login_name"] = user_input
        return None

def input_verified_phone(system_pkg) -> list[str] | None:
    user_input = get_account_dict_input("verified_phone", system_pkg)
    if user_input == False: return None
    elif user_input == None: return None
    else: return user_input

def change_verified_phone(account_task, system_pkg) -> None:
    copy_item_str("verified_phone", account_task, system_pkg)
    
    user_input = input_verified_phone(system_pkg)
    if (user_input == False) or (user_input == None): return None
    else:
        account_task.dict["verified_phone"] = user_input
        return None

def input_verified_email(system_pkg) -> list[str] | None:
    user_input = get_account_dict_input("verified_email", system_pkg)
    if user_input == False: return None
    elif user_input == None: return None
    else: return user_input

def change_verified_email(account_task, system_pkg) -> None:
    copy_item_str("verified_email", account_task, system_pkg)
    
    user_input = input_verified_email(system_pkg)
    if (user_input == False) or (user_input == None): return None
    else:
        account_task.dict["verified_email"] = user_input
        return None

def input_linked_account(system_pkg) -> list[str] | None:
    user_input = get_account_dict_input("linked_account", system_pkg)
    if user_input == False: return None
    elif user_input == None: return None
    else: return user_input

def change_linked_account(account_task, system_pkg) -> None:
    copy_item_str("linked_account", account_task, system_pkg)
    
    user_input = input_linked_account(system_pkg)
    if (user_input == False) or (user_input == None): return None
    else:
        account_task.dict["linked_account"] = user_input
        return None

def input_secure_question(system_pkg) -> list[str] | None:
    user_input = get_account_dict_input("secure_question", system_pkg)
    if user_input == False: return None
    elif user_input == None: return None
    else: return user_input

def change_secure_question(account_task, system_pkg) -> None:
    copy_item_str("secure_question", account_task, system_pkg)
    
    user_input = input_secure_question(system_pkg)
    if (user_input == False) or (user_input == None): return None
    else:
        account_task.dict["secure_question"] = user_input
        return None

def input_other_info(system_pkg) -> list[str] | None:
    user_input = get_account_dict_input("other_info", system_pkg)
    if user_input == False: return None
    elif user_input == None: return None
    else: return user_input

def change_other_info(account_task, system_pkg) -> None:
    copy_item_str("other_info", account_task, system_pkg)
    
    user_input = input_other_info(system_pkg)
    if (user_input == False) or (user_input == None): return None
    else:
        account_task.dict["other_info"] = user_input
        return None

def input_password_history(system_pkg) -> list[str] | None:
    user_input = get_account_dict_input("password_history", system_pkg)
    if user_input == False: return None
    elif user_input == None: return None
    else: return user_input

def change_password_history(account_task, system_pkg) -> None:
    copy_item_str("password_history", account_task, system_pkg)
    
    user_input = input_password_history(system_pkg)
    if (user_input == False) or (user_input == None): return None
    else:
        account_task.dict["password_history"] = user_input
        return None

attr_func_list = [("账号类型", change_account_type),
    ("标签", change_label),
    ("password", change_password),
    ("description", change_description),
    ("login_name", change_login_name),
    ("verified_phone", change_verified_phone),
    ("verified_email", change_verified_email),
    ("linked_account", change_linked_account),
    ("secure_question", change_secure_question),
    ("other_info", change_other_info),
    ("password_history", change_password_history)]

def select_account_attr(system_pkg) -> tuple | None | bool:
    """返回attr_func_list:list[tuple]中的项"""
    
    user_input = system_pkg["normal_input"]("选择属性")
    
    if user_input == system_pkg["EXIT"]: return False
    
    try:
        index = convert_to_int(user_input)
        if index != None:
            return attr_func_list[index]
    except IndexError: pass
    
    for attr_func in attr_func_list:
        if user_input in attr_func[0]:
            return attr_func
    
    return None
    
def show_account_attr(system_pkg):
    table_list = []
    heading = ["索引", "属性名"]
    table_list.append(heading)
    for index, attr_func in enumerate(attr_func_list):
        table_list.append([str(index),
                           attr_func[0]])
    system_pkg["table_msg"](table_list, heading = True)

def edit_account_detail(account_task, system_pkg) -> None:
    show_account_attr(system_pkg)
    while True:
        system_pkg["tips_msg"]("输入索引或属性名")
        attr_func_tuple = select_account_attr(system_pkg)
        
        if attr_func_tuple == False:
            return None
        elif attr_func_tuple == None:
            continue
        else:
            attr_func_tuple[1](account_task, system_pkg)

uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
lowercase = "abcdefghijklmnopqrstuvwxyz"
symbols = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
numbers = "0123456789"
default_password_length = 12
full_char_list = [uppercase, lowercase, symbols, numbers]

def detect_char_list(password):
    char_list = []
    if password == "": return char_list
    
    has_uppercase = False
    has_lowercase = False
    has_symbols = False
    has_numbers = False
    
    for char in password:
        
        if has_uppercase != True:
            if char in uppercase:
                char_list.append(uppercase)
                has_uppercase = True
                continue
        
        if has_lowercase != True:
            if char in lowercase:
                char_list.append(lowercase)
                has_lowercase = True
                continue
        
        if has_symbols != True:
            if char in symbols:
                char_list.append(symbols)
                has_symbols = True
                continue
        
        if has_numbers != True:
            if char in numbers:
                char_list.append(numbers)
                has_numbers = True
                continue
        
        if has_uppercase and has_lowercase and has_symbols and has_numbers:
            break
            
    return char_list

def get_password_length(old_password, system_pkg):
    """返回旧密码长度/从设置读取默认密码长度，保证不为0"""
    if old_password != "":
        return len(old_password)
    else:
        try:
            length = system_pkg["settings_dict"]["ACCOUNT:DEFAULT_PASSWORD_LENGTH"]
            if (type(length) == int) and (length > 0):
                return length
        except KeyError: pass
    return default_password_length


def generate_with_char_ratio(length, char_list):
    total_length = sum([len(s) for s in char_list])
    ratio = [max(1, int(len(s) / total_length * length)) for s in char_list]
    
    new_string = ""
    left_length = length
    for i, s in enumerate(char_list):
        num_chars = ratio[i]
        new_string += "".join(choices(s, k=num_chars))
        left_length -= num_chars
    
    if left_length > 0:
        all_chars = "".join(char_list)
        new_string += "".join(choices(all_chars, k=left_length))
    
    new_string = "".join(sample(new_string, len(new_string)))
    
    return new_string

def generate_password(length = default_password_length, char_list = full_char_list):
    if char_list == []:
        char_list = full_char_list
    
    new_password = generate_with_char_ratio(length, char_list)
    return new_password

def get_new_password(old_password, system_pkg) -> str | None:
    character_list = detect_char_list(old_password)
    if character_list == []:
        character_list = full_char_list
    
    password_length = get_password_length(old_password, system_pkg)
    random_password = generate_password(password_length, character_list)
    py_cp(random_password)
    system_pkg["system_msg"](f"新生成随机密码{random_password[:4] + "*" * (len(random_password) - 4)}已复制到剪贴板")
    
    input_condition, user_input = system_pkg["block_input"]("输入新密码", block_list = system_pkg["BLOCK_LIST"], block_number = False)
    if input_condition == False: return None
    elif input_condition == None: user_input = random_password
    
    if not is_valied_input(user_input, system_pkg):
        system_pkg["system_msg"](f"\"{user_input}\"不符合输入，尝试去除\"|\"")
        return None
    
    return user_input
    

def append_password_history(account_task):
    """将当前密码，日期添加到password_history"""
    old_password = account_task.password
    if old_password == "": return None
    
    old_password_date = account_task.last_date
    if old_password_date == "":
        old_password_date = YYYY_MM_DD()
    
    if len(old_password_date) != 10:
        old_password_date[:10] + " " * (10 - len(old_password_date))
    account_task.dict["password_history"].append(f"({old_password_date}){old_password}")
    
def update_password(account_task, new_password):
    append_password_history(account_task)
    
    current_YYYY_MM_DD = YYYY_MM_DD()
    account_task.last_date = current_YYYY_MM_DD
    account_task.password = new_password