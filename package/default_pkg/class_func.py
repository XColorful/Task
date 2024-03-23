from default_class_func import default_tasker_func_template
from .function import convert_to_int, convert_to_float, YYYY_MM_DD, YYYY_MM_DD_HH_MM_SS
from os import mkdir
from os.path import exists, join
from glob import glob
from pyperclip import copy as py_cp

# 封装函数--------+--------+--------+--------+--------+--------+--------+--------+ Begin
def table_task_template(task_template_list:list, index_list, system_pkg:dict):
    table_list = []
    heading = ["索引", "版本", "task类型"]
    table_list.append(heading)
    index = 0
    for template_index in index_list:
        template = task_template_list[template_index]
        table_list.append([str(index), str(template.version), str(template.type)])
        index += 1
    system_pkg["table_msg"](table_list, heading = True)
    return None

def select_task_template(tasker, system_pkg) -> None | object:
    """选择tasker的task模板
    
    返回None为未选择成功
    
    返回object为task实例"""
    df_template_index_list = []
    ex_template_index_list = []
    for index, task_template in enumerate(tasker.task_template):
        if task_template.type == system_pkg["TYPE_DEFAULT_TASKER"]:
            df_template_index_list.append(index)
        else:
            ex_template_index_list.append(index)
    template_index = 0
    df_template_count = len(df_template_index_list)
    ex_template_count = len(ex_template_index_list)
    if ex_template_count != 0:
        system_pkg["system_pkg"](f"忽略{ex_template_count}项非\"{system_pkg["TYPE_DEFAULT_TASKER"]}\"类型task模板")
    if df_template_count == 0: # 无默认类型task模板
        system_pkg["system_msg"]("无可用的默认task模板")
        return None
    elif df_template_count == 1: # 有1个默认类型task模板
        temeplate_index = df_template_index_list[0]
        return tasker.task_template[temeplate_index]()
    elif df_template_count != 1: # 有多个默认类型task模板
        table_task_template(tasker.task_template, df_template_index_list, system_pkg)
        # 选定task模板索引
        user_input = system_pkg["normal_input"]("输入索引")
        if user_input == system_pkg["EXIT"]: return None
        if user_input != "":
            temeplate_index = convert_to_int(user_input)
            if not temeplate_index in df_template_index_list:
                system_pkg["normal_msg"](f"索引\"{template_index}\"不存在")
                system_pkg["tips_msg"]("输入<Enter>默认选中索引0")
                return None
            else:
                return tasker.task_template[temeplate_index]()

def add_empty_task(tasker, temp_task, system_pkg):
    """为tasker添加空task"""
    current_date = YYYY_MM_DD()
    info_dict = {"create_date":current_date, "date":current_date, "attribute":"", "content":"", "comment":""}
    temp_task.update(info_dict, system_pkg)
    tasker.task_list.append(temp_task)
    system_pkg["system_msg"]("已创建空Task")

def input_task_info(system_pkg) -> dict | None:
    """输入task信息
    
    返回None为取消补充
    
    返回dict用于task.update(info_dict, system_pkg)"""
    current_date = YYYY_MM_DD()
    return_tuple = system_pkg["block_input"](f"日期(默认{current_date})", system_pkg["BLOCK_LIST"], system_pkg, block_number = False)
    if return_tuple[0] == False: return None
    if return_tuple[0] == None: date_input = current_date # 默认为当前日期
    else: date_input = return_tuple[1]
    
    return_tuple = system_pkg["block_input"](f"属性(可选)", system_pkg["BLOCK_LIST"], system_pkg, block_number = False)
    if return_tuple[0] == False: return None
    if return_tuple[0] == None: attribute_input = "N/A" # 默认为"N/A"
    else: attribute_input = return_tuple[1]
    
    return_tuple = system_pkg["strict_input"](f"内容", system_pkg["BLOCK_LIST"], system_pkg, block_number = False)
    if return_tuple[0] == False: return None
    else: content_input = return_tuple[1]
    
    return_tuple = system_pkg["block_input"](f"注释(可选)", system_pkg["BLOCK_LIST"], system_pkg, block_number = False)
    if return_tuple[0] == False: return None
    if return_tuple[0] == None: comment_input = ""
    else: comment_input = return_tuple[1]
    
    return {"create_date":current_date, "date":date_input, "attribute":attribute_input, "content":content_input, "comment":comment_input}

def table_compare_task_list(old_task_list:list, new_task_list:list, system_pkg:dict, display = 8):
    """给出两个默认类型的task_list，进行1.0版本比较
    
    display -> int，显示task_list末尾的若干项task"""
    old_task_list_length = len(old_task_list)
    new_task_list_length = len(new_task_list)
    # 获取需显示的项
    old_list = old_task_list[-display:]
    new_list = new_task_list[-display:]
    old_len = len(old_list)
    new_len = len(new_list)
    if old_len > new_len: MAX_LEN = old_len
    else: MAX_LEN = new_len
    old_list = old_task_list[-MAX_LEN:]
    new_list = new_task_list[-MAX_LEN:]
    table_list = []
    for index in range(-1, -MAX_LEN-1, -1):
        try:
            task = old_list[index]
            display_content = task.content[:8]
            old_column = [str(old_task_list_length + index), f"{task.date}|{task.attribute}|{display_content}"]
        except IndexError:
            old_column = ["", ""]
        try:
            task = new_list[index]
            display_content = task.content[:8]
            new_column = [str(new_task_list_length + index), f"{task.date}|{task.attribute}|{display_content}"]
        except IndexError:
            new_column = ["", ""]
        table_list.append(old_column + new_column)
    heading = ["索引", "老版本", "索引", "新版本"]
    table_list.append(heading)
    table_list.reverse()
    system_pkg["table_msg"](table_list, heading = True)
# 封装函数--------+--------+--------+--------+--------+--------+--------+--------+ End


class default_tasker_func(default_tasker_func_template):
    def __init__(self):
        super().__init__() # 继承父类
        self.label = "default_tasker_func"
        self.version = "1.0"
        self.function_list = ["search", "new", "delete", "backup", "edit", "reload"]
        # 供调试时查看信息用，不可见
        self.create_date = YYYY_MM_DD()
    
    def __str__(self):
        return super().__str__()
    
    def get_info(self):
        return super().get_info()

    def proceed(self, command_list:list, tasker, system_pkg:dict):
        return super().proceed(command_list, tasker, system_pkg)
    
    def search(self, parameter, tasker, system_pkg, show_msg = True):
        index_search_result = []
        string_search_result = []
        index_search_index = []
        string_search_index = []
        index_error = False
        task_list_length = len(tasker.task_list)
        convert_result = convert_to_int(parameter)
        if convert_result != None: # 索引搜索
            try:
                index = convert_result
                task = tasker.task_list[index]
                if index < 0 : index = task_list_length + index # 索引相反则取为正
                show_string = f"{parameter} -> |{task.date}|{task.attribute}|{task.content}|{task.comment}"
                index_search_index.append(index)
                index_search_result.append(show_string)
            except IndexError:
                index_error = True
        search_count = 1 # 用于展示搜索到的序号
        for task_index in range(0, task_list_length): # 字符串搜索
            task = tasker.task_list[task_index]
            task_info_list = [task.content, task.date, task.attribute, task.comment]
            for i in task_info_list:
                if str(parameter) in i: # 输入参数重新取为str
                    show_string = f"{parameter}[{search_count}] -> |{task.date}|{task.attribute}|{task.content}|{task.comment}"
                    search_count += 1
                    string_search_index.append(task_index)
                    string_search_result.append(show_string)
                    break # 结束对单个task的内容匹配
        if show_msg == True:
            if string_search_result != []:
                system_pkg["head_msg"](f"内容搜索结果：{len(string_search_result)}/{task_list_length}")
                system_pkg["body_msg"](string_search_result)
            if index_error == True:
                system_pkg["system_msg"](f"索引\"{parameter}\"不存在")
            elif index_search_result != []:
                system_pkg["head_msg"](f"索引搜索结果：{len(index_search_result)}/{task_list_length}")
                system_pkg["body_msg"](index_search_result)
        # 返回搜索结果索引列表
        if index_search_result != []: return_index = string_search_index + index_search_index # 索引搜索结果放在[-1]位置
        else: return_index = string_search_index
        return return_index
    
    def new(self, parameter, tasker, system_pkg) -> None:
        """用空格分隔参数，参数1为索引则选取task模板列表，参数2为"n"开头则创建空模板
        
        """
        temp_task = select_task_template(tasker, system_pkg)
        if temp_task == None: return None
        # 创建空task检查
        empty_check = parameter.split(" ")
        create_empty_task = False
        for i in empty_check[0:]: # 检查参数"n"
            try:
                if i[0] == "n": create_empty_task = True
                break
            except IndexError: continue
        
        if create_empty_task == True:
            add_empty_task(tasker, temp_task, system_pkg)
            return None # 判断是否选择创建空task
        
        info_dict = input_task_info(system_pkg) # 输入task信息
        if info_dict == None: return None
        temp_task.update(info_dict, system_pkg)
        tasker.task_list.append(temp_task)
        system_pkg["normal_msg"]("已创建task")
        system_pkg["body_msg"]([f"{temp_task.create_date}|{temp_task.date}|{temp_task.attribute}|{temp_task.content}|{temp_task.comment}"])
        return None

    def delete(self, parameter, tasker, system_pkg):
        """参数非空时指定搜索对象，为索引或搜索，选取最后一个搜索到的（task_list末端）
        
        """
        index = [] # 存储索引列表
        user_input = parameter # 用于后续判断是否为空输入，操作空task
        if user_input == "":
            system_pkg["tips_msg"]("参数为索引或搜索，选取最后一个搜索到的task（位于列表末端）")
            user_input = system_pkg["normal_input"]("指定编辑对象")
            if user_input == system_pkg["EXIT"]: return None
            if user_input == "": # 搜索空task
                for i in range( len(tasker.task_list) - 1, -1, -1):
                    if tasker.task_list[i].create_date == "":
                        index.append(i)
                        break
            else: index = self.search(user_input, tasker, system_pkg, show_msg = False) # 搜索非空task，返回列表
        else: index = self.search(user_input, tasker, system_pkg, show_msg = False) # 搜索非空task，返回列表
        # 搜索结果
        if index == []:
            system_pkg["system_msg"]("无指定对象")
            return None
        else: index = index[-1] # 搜索结果选取最后添加的task
        # 显示task内容
        task = tasker.task_list[int(index)] # 重新取为int
        system_pkg["normal_msg"](f"{index}|{task.date}|{task.attribute}|{task.content}|{task.comment}")
        user_input = system_pkg["normal_input"](f"确认删除\"{task.content}\"(y/n)")
        if user_input != "y": return None
        del tasker.task_list[index]
        system_pkg["system_msg"]("已删除task")
    
    def backup(self, parameter, tasker, system_pkg):
        """备份单个tasker，删除空项
        
        parameter以"e"开头，尝试备份extra类型"""
        if tasker.type != system_pkg["TYPE_DEFAULT_TASKER"]:
            if parameter[0:] != "e":
                system_pkg["system_msg"]("该功能默认不备份extra类型Tasker")
                system_pkg["tips_msg"]("参数为\"e\"开头则尝试备份")
                return None
        existed_task_template = {}
        clean_count = 0
        task_list = tasker.task_list
        for task_index in range(len(task_list) - 1, -1, -1): # 倒序，用于后续删除index不产生错误
            try:
                # 删除空项
                task = task_list[task_index]
                if task.create_date == "":
                    del task_list[task_index]
                    clean_count += 1
                    continue
                # 版本检测
                if not task.version in existed_task_template[f"{task.type}"]: # task.type在字典key的列表里，但版本不同
                    existed_task_template[f"{task.type}"] = [task.version]
            except KeyError: # task.type不在字典里
                existed_task_template[f"{task.type}"] = [task.version]
        # 所有出现的版本
        all_existed_task_template = ""
        for task_template in existed_task_template.keys():
            for template_version in existed_task_template[task_template]:
                all_existed_task_template += f"{task_template} {template_version} "
        all_existed_task_template = all_existed_task_template.rstrip(" ")
        # 创建备份文件夹路径
        backup_dir = ".\\backup_single\\"
        if not exists(backup_dir): mkdir(backup_dir)
        file_path = join(f"{backup_dir}", f"{tasker.tasker_label}_{YYYY_MM_DD_HH_MM_SS()}.txt")
        with open(file_path, "w", encoding = "utf-8") as f:
            function_list = []
            for class_func in tasker.function_list:
                function_list.append(str(class_func))
            show_function_list = " ".join(function_list)
            # 写入tasker行
            f.write(f"{tasker.type}||||{tasker.version}||||{tasker.tasker_label}||||{tasker.create_date}||||{show_function_list}||||{all_existed_task_template}||||{tasker.description}\n")
            # 写入task
            try:
                for task in task_list:
                    backup_str = task.backup()
                    if backup_str == "": continue
                    f.write(f"\t{backup_str}\n")
            except AttributeError:
                system_pkg["system_msg"]("写入中断，task不包含backup()方法")
                return None
        system_pkg["system_msg"](f"已备份至\"{file_path}\"")
        return None

    def edit(self, parameter, tasker, system_pkg):
        """参数非空时指定搜索对象，为索引或搜索，选取最后一个搜索到的（task_list末端）
        
        """
        index = [] # 存储索引列表
        user_input = parameter # 用于后续判断是否为空输入，操作空task
        if user_input == "":
            system_pkg["tips_msg"]("参数为索引或搜索，选取最后一个搜索到的task（位于列表末端）")
            user_input = system_pkg["normal_input"]("指定编辑对象")
            if user_input == system_pkg["EXIT"]: return None
            if user_input == "": # 搜索空task
                for i in range( len(tasker.task_list) - 1, -1, -1):
                    if tasker.task_list[i].create_date == "":
                        index.append(i)
                        break
            else: index = self.search(user_input, tasker, system_pkg, show_msg = False) # 搜索非空task，返回列表
        else: index = self.search(user_input, tasker, system_pkg, show_msg = False) # 搜索非空task，返回列表
        # 搜索结果
        if index == []:
            system_pkg["system_msg"]("无指定对象")
            return None
        else: index = index[-1] # 搜索结果选取最后添加的task
        # 输入task编辑内容
        task = tasker.task_list[int(index)] # 重新取为int
        system_pkg["normal_msg"](f"{index}|{task.date}|{task.attribute}|{task.content}|{task.comment}")
        
        py_cp(task.date)
        system_pkg["normal_msg"](f"task.date copied to clipboard")
        return_tuple = system_pkg["block_input"](f"{task.date}", system_pkg["BLOCK_LIST"], system_pkg, block_number = False)
        if return_tuple[0] == False: return None
        if return_tuple[0] == None: date_input = ""
        else: date_input = return_tuple[1]
        
        py_cp(task.attribute)
        system_pkg["normal_msg"](f"task.attribute copied to clipboard")
        return_tuple = system_pkg["block_input"](f"{task.attribute}", system_pkg["BLOCK_LIST"], system_pkg, block_number = False)
        if return_tuple[0] == False: return None
        if return_tuple[0] == None: attribute_input = ""
        else: attribute_input = return_tuple[1]
        
        py_cp(task.content)
        system_pkg["normal_msg"](f"task.content copied to clipboard")
        return_tuple = system_pkg["block_input"](f"{task.content}", system_pkg["BLOCK_LIST"], system_pkg, block_number = False)
        if return_tuple[0] == False: return None
        if return_tuple[0] == None: content_input = ""
        else: content_input = return_tuple[1]
        
        py_cp(task.comment)
        system_pkg["normal_msg"](f"task.comment copied to clipboard")
        return_tuple = system_pkg["block_input"](f"{task.comment}", system_pkg["BLOCK_LIST"], system_pkg, block_number = False)
        if return_tuple[0] == False: return None
        if return_tuple[0] == None: comment_input = ""
        else: comment_input = return_tuple[1]
        
        # 编辑task
        if date_input != "":
            system_pkg["normal_msg"](f"task.date：{task.date}")
            system_pkg["body_msg"]([f"更改为：{date_input}"])
            task.date = date_input
        if attribute_input != "":
            system_pkg["normal_msg"](f"task.attribute：{task.attribute}")
            system_pkg["body_msg"]([f"更改为：{attribute_input}"])
            task.attribute = attribute_input
        if content_input != "":
            system_pkg["normal_msg"](f"task.content：{task.content}")
            system_pkg["body_msg"]([f"更改为：{content_input}"])
            task.content = content_input
        if comment_input != "":
            system_pkg["normal_msg"](f"task.comment：{task.comment}")
            system_pkg["body_msg"]([f"更改为：{comment_input}"])
            task.comment = comment_input
        if user_input == "": # 为空task更新创建日期
            if date_input and attribute_input and content_input: task.create_date = YYYY_MM_DD()
        return None
    
    def reload(self, parameter, tasker, system_pkg):
        """暂无实际参数
        
        """
        if tasker.type != system_pkg["TYPE_DEFAULT_TASKER"]:
            system_pkg["system_msg"](f"Tasker类型\"{tasker.type}\"不适用于\"{system_pkg["TYPE_DEFAULT_TASKER"]}\"类型的方法")
            return None
        backup_dir = ".\\backup_single\\"
        # 读取路径检测
        if not exists(backup_dir): return system_pkg["system_msg"](f"读取路径\"{backup_dir}\"不存在")
        # 显示读取参数
        system_pkg["normal_msg"](f"读取路径\"{backup_dir}\"")
        file_list = glob(join((backup_dir), f"{tasker.tasker_label}_*.txt"))
        if file_list == []: return system_pkg["system_msg"](f"无可用的\"{tasker.tasker_label}\"备份文件")
        file_list.sort()
        file_path = file_list[-1]
        with open(file_path, "r", encoding = "utf-8") as f:
            txt_list = f.readlines()
            MAX_TXT_LIST_INDEX = len(txt_list)
            check_index = 0
            # tasker信息读取
            tasker_check = False
            for index in range(check_index, MAX_TXT_LIST_INDEX):
                check_line = txt_list[index]
                if check_line == "": # 排除空行
                    system_pkg["body_msg"]([f"Line{check_index}:空行"])
                    check_index += 1
                    continue
                check_list = check_line.split("||||")
                if len(check_list) != 7:
                    check_index += 1
                    continue
                try:
                    tasker_type, tasker_version = check_list[0:2]
                except ValueError:
                    system_pkg["body_msg"]([f"Line{check_index}:缺少[类型, 版本]"])
                # tasker.type
                if tasker_type != tasker.type:
                    system_pkg["body_msg"]([f"Line{check_index}:Tasker类型\"{tasker_type}\"不匹配"])
                    check_index += 1
                    continue
                # tasker.version
                tasker_version = convert_to_float(tasker_version)
                if (tasker_version == None) or (tasker_version > (convert_to_float(tasker.version))):
                    system_pkg["body_msg"]([f"Line{check_index}:Tasker版本\"{tasker_version}\"不匹配"])
                    check_index += 1
                    continue
                try:
                    tasker_tasker_label, tasker_create_date, tasker_function_list, tasker_task_template, tasker_description = check_list[2:7]
                except ValueError:
                    system_pkg["body_msg"]([f"Line{check_index}:缺少完整数据[Tasker标签, 创建日期, 功能列表, task模板, Tasker描述]"])
                    check_index += 1
                    continue
                # tasker.tasker_label
                if tasker_tasker_label != tasker.tasker_label:
                    system_pkg["body_msg"]([f"Line{check_index}:Tasker标签\"{tasker_tasker_label}\"不匹配"])
                    check_index += 1
                    continue
                # tasker.create_date
                if tasker_create_date != tasker.create_date:
                    system_pkg["body_msg"]([f"Line{check_index}:Tasker创建日期\"{tasker_create_date}\"不匹配"])
                    
                    if system_pkg["normal_input"]("更改原Tasker创建日期(y/n)") != "y":
                        check_index += 1
                        continue
                    tasker.create_date = tasker_create_date

                # tasker.funciton_list
                function_list = tasker_function_list.split(" ")
                if len(function_list) % 3 != 0:
                    system_pkg["body_msg"]([f"Line{check_index}:Tasker功能列表\"{function_list}\"格式错误"])
                    check_index += 1
                    continue
                for index in range(0, len(function_list), 3):
                    function_label, function_version, function_type = function_list[index:index+3]
                    # 对于每一个class_func
                    check = False
                    for class_func in tasker.function_list:
                        if function_label != class_func.label:
                            check_index += 1
                            continue
                        function_version = convert_to_float(function_version)
                        if (function_version == None) or (function_version > convert_to_float(class_func.version)):
                            check_index += 1
                            continue
                        if function_type != class_func.type:
                            check_index += 1
                            continue
                        check = True
                        break
                    if check == False:
                        system_pkg["body_msg"]([f"Line{check_index}:Tasker功能列表\"{function_list}\"有不适用功能"])
                # tasker.task_template
                task_template_list = tasker_task_template.split(" ")
                if len(task_template_list) % 2 != 0:
                    system_pkg["body_msg"]([f"Line{check_index}:Taskertask模板\"{tasker_task_template}\"格式错误"])
                    check_index += 1
                    continue
                for index in range(0, len(task_template_list), 2):
                    task_type, task_version = task_template_list[index:2]
                    # 对于每一个task_template
                    check = False
                    for task_template in tasker.task_template:
                        task_instance = task_template()
                        if task_type != task_instance.type:
                            check_index += 1
                            continue
                        task_version = convert_to_float(task_version)
                        # task_version == None则可能为extra类型（不允许类型为可被float()的字符串）
                        if (task_version == None) or (task_version > convert_to_float(task_instance.version)):
                            check_index += 1
                            continue
                        check = True
                        break
                    if check == False:
                        system_pkg["body_msg"]([f"Line{check_index}:Tasker\"{task_template_list}\"有不适用的task模板"])
                # tasker.description
                if tasker_description != tasker.description:
                    
                    if system_pkg["normal_input"]("更改原Tasker描述(y/n)") != "y":
                        check_index += 1
                        continue
                    tasker.description = tasker_description

                tasker_check = True
                check_index += 1
                break
            # tasker信息检测
            if tasker_check == False: return system_pkg["system_msg"](f"识别Tasker信息失败，请检查备份文件\"{file_path}\"")
            system_pkg["system_msg"](f"读取到Tasker{tasker.tasker_label}")
            # task读取
            task_list = []
            for index in range(check_index, MAX_TXT_LIST_INDEX):
                check_line = txt_list[index].rstrip("\n")
                if check_line == "": # 排除空行
                    system_pkg["body_msg"]([f"Line{check_line}:空行"])
                    check_index += 1
                    continue
                if check_line[0] != "\t": # 非"\t"开头则结束
                    break
                check_line = check_line[1:] # 去除开头的"\t"
                check_list = check_line.split("||||")
                if len(check_list) != 7:
                    system_pkg["body_msg"]([f"Line{check_index}:task类型\"{check_line}\"不匹配"])
                    check_index += 1
                    continue
                task_type, task_version, task_create_date, task_date, task_attribute, task_content, task_comment = check_list
                # 创建空task模板
                temp_task = None
                for task_template in tasker.task_template:
                    task_instance = task_template()
                    if task_type != task_instance.type: continue
                    task_version = convert_to_float(task_version)
                    if (task_version == None) or (task_version > convert_to_float(task_instance.version)): continue
                    temp_task = task_instance
                if temp_task == None:
                    system_pkg["body_msg"]([f"Line{check_index}:\"{check_line}\"无匹配的task模板"])
                    check_index += 1
                    continue
                # 填充task信息
                temp_task.update({"create_date":task_create_date, "date":task_date, "attribute":task_attribute, "content":task_content, "comment":task_comment}, system_pkg)
                task_list.append(temp_task)
            # 空task_list检测
            if task_list == []:
                system_pkg["system_msg"]("无读取的task，不进行覆写操作")
                return None
            # task_list信息比较
            table_compare_task_list(tasker.task_list, task_list, system_pkg, display = 8)
            # 确认读取task_list
            user_input = system_pkg["normal_input"]("确认读取(y/n)")
            if user_input != "y": return None
            # 覆写task_list
            tasker.task_list = task_list
            system_pkg["system_msg"](f"已读取\"{file_path}\"")
            return None