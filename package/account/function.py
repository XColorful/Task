def convert_to_int(s:str):
    """返回字符串是否能转换为int，不修改原字符串
    
    接收一个普通字符串，转换失败则返回None"""
    try:
        return int(s)
    except ValueError:
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

def select_account_task(user_input, tasker, system_pkg) -> int | None:
    """返回值为索引或None"""
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
                            f"password：{account_task.password}"])

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