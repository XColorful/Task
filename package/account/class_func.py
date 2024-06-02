from default_class_func import extra_tasker_func_template
from .function import YYYY_MM_DD, convert_to_int, select_account_task, show_account_detail, edit_account_detail, get_new_password, update_password, show_acc_info
from pyperclip import copy as py_cp

# 封装函数--------+--------+--------+--------+--------+--------+--------+--------+ Begin
def show_acc_info_guide(system_pkg):
    system_pkg["tips_msg"]("account信息参考")
    system_pkg["tips_msg"]("\t[1]|账号类型：所属平台")
    system_pkg["tips_msg"]("\t[2]|标签（可选）：用于搜索该账号，默认与\"账号类型\"相同")
    system_pkg["tips_msg"]("\t[3]|补充信息（可选）：账号描述，登录名称等")

def input_acc_info(task, block_list, system_pkg) -> None | bool:
    """输入task信息
    
    返回None为取消
    
    返回True为成功添加"""
    # 输入账号类型
    return_tuple = system_pkg["strict_input"]("账号类型", block_list, system_pkg, block_number = False)
    if return_tuple[0] == False: return None
    else: task.account_type = return_tuple[1]
    # 输入账号标签
    return_tuple = system_pkg["block_input"]("标签（可选）", block_list, system_pkg, block_number = False)
    if return_tuple[0] == False: return None
    if return_tuple[0] == None: task.label = task.account_type
    else: task.label = return_tuple[1]
    return True

def show_acc_additional_guide(system_pkg):
    system_pkg["normal_msg"]("补充信息类型")
    system_pkg["body_msg"](["description：账号描述", "login_name：登录使用的名称/数据", "verified_phone：绑定手机号", "verified_email：绑定邮箱", "linked_account：绑定的其他账号", "secure_question：安全问题", "other_info：其他类型的补充信息", "password_history（不推荐）：历史密码"])
    system_pkg["tips_msg"]("格式示例：\"类型|||内容1|||内容2（数量不限）\"")
    system_pkg["tips_msg"]("仅输入\"类型\"可显示更多描述")

def show_detail(key, system_pkg):
    """显示详细信息"""
    if key == "description":
        system_pkg["normal_msg"]("description"); system_pkg["body_msg"](["描述：账号描述", "格式示例：\"description|||描述1|||描述2（数量不限）\""])
    elif key == "login_name":
        system_pkg["normal_msg"]("login_name"); system_pkg["body_msg"](["描述：登录使用的名称/数据", "注：若该项非空则使用\"get\"获取该账号时将自动复制第一项到剪贴板", "格式示例：\"login_name|||账号名称1（复制到剪贴板）|||账号名称2（不复制，数量不限）\""])
    elif key == "verified_phone":
        system_pkg["normal_msg"]("verified_phone"); system_pkg["body_msg"](["描述：绑定手机号", "格式示例：\"verified_phone|||手机号1|||手机号2（数量不限）\""])
    elif key == "verified_email":
        system_pkg["normal_msg"]("verified_email"); system_pkg["body_msg"](["描述：绑定邮箱", "格式示例：\"verified_email|||邮箱1|||邮箱2（数量不限）\""])
    elif key == "linked_account":
        system_pkg["normal_msg"]("linked_account"); system_pkg["body_msg"](["描述：绑定的其他账号", "注：使用\"get\"获取账号时会同时搜索linked_account", "注：当格式为\"账号类型：标签\"（中文标点）时，\"get\"将进行标签匹配", "格式示例：\"linked_account|||账号类型1：标签|||账号类型2（数量不限）\""])
    elif key == "secure_question":
        system_pkg["normal_msg"]("secure_question"); system_pkg["body_msg"](["描述：安全问题", "注：使用\"：\"（中文标点）分隔将在\"search\"时分行显示", "格式示例：\"secure_question|||问题1：答案|||问题2：答案（数量不限）\""])
    elif key == "other_info":
        system_pkg["normal_msg"]("other_info"); system_pkg["body_msg"](["描述：其他类型的补充信息", "格式示例：\"other_info|||任意信息|||任意信息（数量不限）\""])
    elif key == "password_history":
        system_pkg["normal_msg"]("password_history"); system_pkg["body_msg"](["描述：历史密码", "注：该项内容可由指令\"update\"自动迁移旧密码", "格式示例：\"password_history|||(YYYY_MM_DD)password1|||(2024_01_01)password2（数量不限）\""])

def show_search_result(task, index, system_pkg, linked_acccout = False):
    """显示搜索结果"""
    index = f"[{index}]" if index != None else ""
    show_alias = f"（{task.label}）" if task.account_type != task.label else ""
    result_head = f"{index}|{task.account_type}{show_alias}"
    system_pkg["normal_msg"](result_head)
    body_list = []
    if linked_acccout == False:
        if task.create_date != "": body_list.append(f"create_date：{task.create_date}")
        if task.last_date != "": body_list.append(f"last_date：{task.last_date}")
        if task.dict["login_name"] != []:
            body_list.append("login_name：")
            for login_name in task.dict["login_name"]:
                body_list.append(f"\t{login_name}")
        if task.dict["description"] != []:
            body_list.append("description：")
            for description in task.dict["description"]:
                body_list.append(f"\t{description}")
    elif linked_acccout == True:
        body_list.append(f"linked_account：")
        for linked_account in task.dict["linked_account"]:
            body_list.append(f"\t{linked_account}") 
    system_pkg["body_msg"](body_list)

def get_password(tasker, index, system_pkg):
    """获取密码到剪贴板"""
    task = tasker.task_list[index]
    password = task.password
    show_alias = f"（{task.label}）" if task.label != task.account_type else ""
    if password != "":
        py_cp(password)
        system_pkg["system_msg"](f"{task.account_type}{show_alias}.password已复制到剪贴板")
        return True
    system_pkg["system_msg"](f"{task.account_type}{show_alias}.password为空")
# 封装函数--------+--------+--------+--------+--------+--------+--------+--------+ End

def get_delete_confirm(system_pkg) -> str | None:
    user_input = system_pkg["normal_input"]("确认删除(y/n)")
    if user_input == system_pkg["EXIT"]: return None
    else: return user_input

def get_update_confirm(system_pkg) -> str | None:
    user_input = system_pkg["normal_input"]("确认更改(y/n)")
    if user_input == system_pkg["EXIT"]: return None
    else: return user_input

class account_tasker_func(extra_tasker_func_template):
    def __init__(self):
        super().__init__() # 继承父类
        self.label = "account_tasker_func"
        self.version = "account"
        self.function_list = ["new", "get", "search", "edit", "delete"]
        self.create_date = YYYY_MM_DD()
    
    def __str__(self):
        return super().__str__()
    
    def get_info(self):
        return super().get_info()
    
    def proceed(self, cmd_list:list, tasker, system_pkg:dict):
        super().proceed(cmd_list, tasker, system_pkg)
    
    def new(self, parameter, tasker, system_pkg) -> None:
        """建立新account
        
        """
        block_list = system_pkg["BLOCK_LIST"]
        # 创建task实例
        ready = False
        for task_template in tasker.task_template:
            task = task_template()
            if task.version == tasker.version:
                ready = True
                break
        if ready == False:
            system_pkg["system_msg"](f"缺少类型（{tasker.version}）匹配的task模板")
            return None
        # 显示account信息参考
        show_acc_info_guide(system_pkg)
        # 输入账号信息
        input_result = input_acc_info(task, block_list, system_pkg)
        if input_result == None: return None
        # task.dict
        # 展示补充格式
        show_acc_additional_guide(system_pkg)
        return_tuple = system_pkg["block_input"]("添加补充信息（可选）", block_list, system_pkg, block_number = False)
        if return_tuple[0] == False: return None
        
        # 输入补充信息
        while return_tuple[0] == True: # 当用户输入不为空或system_pkg["EXIT"]
            # 从输入分隔key, value
            key_value_pair = return_tuple[1].split("|||", 1)
            key = key_value_pair[0]
            value = key_value_pair[1:]
            # 输入的类型不存在
            if key not in task.dict:
                system_pkg["system_msg"](f"类型\"{key}\"不存在")
                return_tuple = system_pkg["block_input"]("添加补充信息", block_list, system_pkg, block_number = False)
                if return_tuple == False: return None
                continue
            
            # 输入的类型存在，值未填
            if (key in task.dict) and (value == []):
                # 显示类型的详细信息
                show_detail(key, system_pkg)
                return_tuple = system_pkg["block_input"]("添加补充信息", block_list, system_pkg, block_number = False)
                if return_tuple[0] == False: return None
                continue

            # 输入的类型存在，值已填
            value_list = value[0].split("|||")
            task.dict[key] = value_list
            return_tuple = system_pkg["block_input"]("添加补充信息", block_list, system_pkg, block_number = False)
            if return_tuple[0] == False: return None
            continue
        
        # 更新创建日期
        task.create_date = YYYY_MM_DD()
        tasker.task_list.append(task)
        # 显示创建成功
        show_alias = f"（{task.label}）" if task.label != task.account_type else ""
        system_pkg["system_msg"](f"账号\"{task.account_type}\"{show_alias}已创建")
        # 立即更新密码（可选）
        user_input = system_pkg["normal_input"]("立即更新密码(y/n)")
        if user_input != "y": return None
        self.update(-1, tasker, system_pkg)
    
    def get(self, parameter:str, tasker, system_pkg, linked_account = True, show = True) -> list: # label, account_type, linked_account
        """参数为"/"开头则强制执行索引搜索，参数为"+"开头则不搜索索引
        
        返回列表
        [
            label -> list,
            
            index -> int | None,
                
            account_type -> list,
                
            linked_account -> list]"""
        if parameter != "": user_input = parameter
        else: user_input = system_pkg["normal_input"]("输入标签或账号类型")
        if user_input == system_pkg["EXIT"]: return None
        if user_input == "": return None
        # 搜索优先级：label > index > account_type > linked_account
        if user_input[0] == "/": # 仅执行索引搜索
            user_input = user_input[1:]; select_search_index = True
        elif user_input[0] == "+": # 不执行索引搜索
            user_input = user_input[1:]; select_search_index = False
        else: select_search_index = None # 执行索引搜索，但不唯一
        label_index = []
        account_type_index = []
        linked_account_index = []
        task_index = None
        # 搜索user_input
        # 索引搜索
        if (select_search_index == True) or (select_search_index == None):
            index_search = convert_to_int(user_input)
            try:
                if user_input[0] == "/": user_input = user_input[1:]
                tasker.task_list[index_search]
                task_index = index_search
            except IndexError: pass
            except TypeError: pass
        if select_search_index != True:
        # 字符串搜索
            for index, task in enumerate(tasker.task_list):
                if task.type != tasker.type: continue # 跳过非account类型
                # 搜索task.label
                if user_input in task.label:
                    label_index.append(index)
                    continue
                # 搜索task.account_type
                elif user_input in task.account_type:
                    account_type_index.append(index)
                    continue
                # 搜索task.dict[linked_account]
                if linked_account == True:
                    for single_account in task.dict["linked_account"]:
                        try:
                            if user_input in single_account.split("：")[1]: # 如果有用"："分隔的第二项（不触发IndexError）
                                linked_account_index.append(index)
                                break
                        except IndexError: continue
                continue
        
        # 显示搜索结果--------+--------+--------+--------+--------+--------+--------+ Begin
        if show == True:
            # 仅显示索引搜索结果
            if select_search_index == True:
                if task_index != None:
                    pass
                pass
            # 显示所有搜索结果
            else:
                show_index = 1
                if label_index != []:
                    system_pkg["head_msg"](f"标签（{len(label_index)}）")
                    for index in label_index:
                        show_search_result(tasker.task_list[index], show_index, system_pkg)
                        show_index += 1
                if select_search_index == None:
                    if task_index != None:
                        system_pkg["head_msg"](f"索引")
                        show_search_result(tasker.task_list[task_index], index = None, system_pkg = system_pkg)
                if account_type_index != []:
                    system_pkg["head_msg"](f"账号类型（{len(account_type_index)}）")
                    for index in account_type_index:
                        show_search_result(tasker.task_list[index], show_index, system_pkg)
                        show_index += 1
                if linked_account_index != []:
                    system_pkg["head_msg"](f"账号关联（{len(linked_account_index)}）")
                    for index in linked_account_index: show_search_result(tasker.task_list[index], show_index, system_pkg, linked_acccout = True)
                    show_index += 1
        # 显示搜索结果--------+--------+--------+--------+--------+--------+--------+ End
        
        # 获取password（索引搜索结果）
        if task_index != None:
            get_password(tasker, task_index, system_pkg)
        # 获取password（非索引搜索结果）
        if select_search_index != True:
            all_index_list = label_index + account_type_index + linked_account_index
            if len(all_index_list) == 1:
                task = tasker.task_list[all_index_list[0]]
                password = task.password
                if password != "":
                    py_cp(password)
                    show_alias = f"（{task.label}）" if task.label != task.account_type else ""
                    system_pkg["system_msg"](f"{task.account_type}{show_alias}.password已复制到剪贴板")
            elif len(all_index_list) > 1:
                system_pkg["tips_msg"]("输入序号以获取密码到剪贴板")
                user_input = system_pkg["normal_input"]("选取account.password")
                if user_input == system_pkg["EXIT"]: return None
                try:
                    input_convert = convert_to_int(user_input)
                    if input_convert <= 0:
                        system_pkg["system_msg"]("索引需为正")
                        return None
                    else:
                        index = all_index_list[input_convert - 1]
                    get_password(tasker, index, system_pkg)
                except TypeError:
                    system_pkg["system_msg"](f"索引\"{user_input}\"错误")
                except IndexError:
                    system_pkg["system_msg"](f"索引\"{user_input}\"不存在")
                
        # 返回get索引
        return [label_index, task_index, account_type_index, linked_account_index]
    
    def search(self, parameter, tasker, system_pkg):
        user_input = select_account_task(parameter, tasker, system_pkg)
        if user_input == None: return None
        else:
            account_index = user_input
            system_pkg["normal_msg"]("--------搜索结果--------")
            show_account_detail(tasker.task_list[account_index], system_pkg)
            system_pkg["normal_msg"]("")
        return None

    def edit(self, parameter, tasker, system_pkg):
        user_input = select_account_task(parameter, tasker, system_pkg)
        if user_input == None: return None
        else:
            account_index = user_input
            system_pkg["normal_msg"](f"--------{tasker.task_list[account_index].label}信息--------")
            edit_account_detail(tasker.task_list[account_index], system_pkg)
            system_pkg["normal_msg"]("")
        return None
    
    def delete(self, parameter, tasker, system_pkg): # label, account_type
        user_input = select_account_task(parameter, tasker, system_pkg)
        if user_input == None: return None
        else:
            account_index = user_input
            system_pkg["normal_msg"]("--------删除预览--------")
            show_account_detail(tasker.task_list[account_index], system_pkg)
            system_pkg["normal_msg"]("")
            if get_delete_confirm(system_pkg) == "y":
                del tasker.task_list[account_index]
                system_pkg["system_msg"]("已删除task")
        return None

class account_manage_func(extra_tasker_func_template):
    def __init__(self):
        super().__init__() # 继承父类
        self.label = "account_manage_func"
        self.version = "account"
        self.function_list = ["update", "list_acc"]
        self.create_date = YYYY_MM_DD()
        
    def update(self, parameter, tasker, system_pkg):
        user_input = select_account_task(parameter, tasker, system_pkg)
        if user_input == None: return None
        else:
            account_index = user_input
            old_password = tasker.task_list[account_index].password
            new_password = get_new_password(old_password, system_pkg)
            
            if new_password != None:
                if get_update_confirm(system_pkg) == "y":
                    update_password(tasker.task_list[account_index], new_password)
        return None

    def list_acc(self, parameter, tasker, system_pkg):
        show_acc_info(tasker.task_list, system_pkg)