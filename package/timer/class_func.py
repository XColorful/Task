from datetime import datetime
from default_class_func import extra_tasker_func_template
from .function import convert_to_int, YYYY_MM_DD, YYYY_MM_DD_HH_MM, show_task_info, get_not_end_timer_index, show_unfinished_timer, find_timer_in_all, set_timer_task_df_attribute, set_timer_task_prefix, set_timer_task_df_content

def check_tasker(tasker, system_pkg) -> None:
    """检查是否有模板"""
    for task_template in tasker.task_template:
        if task_template.version == "timer":
            return True
    system_pkg["system_msg"](f"Tasker（{tasker.tasker_label}）缺少timer类task")
    return False
def make_timer_template(tasker) -> object | None:
    """此函数默认tasker.task_template含有timer类task"""
    for task_template in tasker.task_template:
        if task_template.version == "timer":
            return task_template()
def create_timer_template(tasker, system_pkg) -> object | None:
    if not check_tasker(tasker, system_pkg):
        return None
    timer_task = make_timer_template(tasker)
    return timer_task
def get_tasker_config(tasker) -> dict:
    config_dict = {"timer_task_df_attribute":"",
                   "timer_task_prefix":"",
                   "timer_task_df_content":""}
    try:
        config_dict["timer_task_df_attribute"] = tasker.timer_task_df_attribute
        config_dict["timer_task_prefix"] = tasker.timer_task_prefix
        config_dict["timer_task_df_content"] = tasker.timer_task_df_content
    except AttributeError: pass
    return config_dict

def get_time_input(date_type:str, current_YYYY_MM_DD_HH_SS, system_pkg) -> str | None | bool:
    user_input = system_pkg["normal_input"](f"{date_type}日期({current_YYYY_MM_DD_HH_SS})")
    if user_input == system_pkg["EXIT"]: return False
    elif user_input == "": return None
    else: return user_input
def check_YYYY_MM_DD_HH_SS_format(date_str) -> bool:
    try:
        datetime.strptime(date_str, '%Y_%m_%d-%H:%M')
        return True
    except ValueError:
        return False
def get_YYYY_MM_DD_HH_SS_input(date_type, system_pkg, allow_empty = False) -> str | bool:
    while True:
        current_YYYY_MM_DD_HH_SS = YYYY_MM_DD_HH_MM()
        user_input = get_time_input(date_type, current_YYYY_MM_DD_HH_SS, system_pkg)
        # 检查输入
        if user_input == False: return False # EXIT
        elif user_input == None:
            if allow_empty == False:
                return current_YYYY_MM_DD_HH_SS # ""
            else: return ""
        # 检查日期是否存在
        if check_YYYY_MM_DD_HH_SS_format(user_input):
            return user_input
        else:
            system_pkg["normal_msg"](f"日期格式\"{user_input}\"错误")
            system_pkg["tips_msg"]("格式：YYYY_MM_DD-HH:SS")
            continue
def get_start_time_input(system_pkg):
    return get_YYYY_MM_DD_HH_SS_input("start", system_pkg)
def get_attribute_input(system_pkg) -> str | bool:
    input_condition, user_input = system_pkg["block_input"]("属性(可选)", block_list = system_pkg["BLOCK_LIST"], system_pkg = system_pkg, block_number = False)
    if input_condition == False: return False # EXIT
    elif input_condition == None: return "N/A" # ""
    return user_input
def get_content_strict_input(system_pkg) -> str | bool:
    system_pkg["tips_msg"]("输入\"n\"即可使用默认配置的输入")
    input_condition, user_input = system_pkg["strict_input"]("内容", block_list = system_pkg["BLOCK_LIST"], block_number = False)
    if input_condition == False: return False
    elif input_condition == None: return ""
    return user_input
def get_content_input(system_pkg) -> str | bool:
    system_pkg["tips_msg"]("输入\"n\"即可使用默认配置的输入")
    input_condition, user_input = system_pkg["block_input"]("内容", block_list = system_pkg["BLOCK_LIST"], system_pkg = system_pkg,  block_number = False)
    if input_condition == False: return False
    elif input_condition == None: return ""
    return user_input
def get_comment_input(system_pkg) -> str | bool:
    input_condition, user_input = system_pkg["block_input"]("注释(可选)", block_list = system_pkg["BLOCK_LIST"], system_pkg = system_pkg,  block_number = False)
    if input_condition == False: return False # EXIT
    elif input_condition == None: return "" # ""
    return user_input
def get_end_time_input(system_pkg):
    return get_YYYY_MM_DD_HH_SS_input("end", system_pkg, allow_empty=True)
def input_timer_task_info(tasker_config, system_pkg) -> list[str] | bool:
    input_list = []
    for input_func in [get_start_time_input, # start_time
                       get_attribute_input, # attribute
                       get_content_strict_input, # content
                       get_comment_input, # comment
                       get_end_time_input]: # end_time
        user_input = input_func(system_pkg)
        if user_input == False: return False
        input_list.append(user_input)
    current_date = YYYY_MM_DD()
    input_list.append(current_date) # create_date
    build_list = [system_pkg["TYPE_EXTRA_TASKER"], "timer"] + [""] * 6
    build_list[2] = current_date # create_date
    build_list[3] = input_list[0] # start_time
    build_list[4] = input_list[4] # end_time
    # attribute
    timer_task_df_attribute = tasker_config["timer_task_df_attribute"]
    build_list[5] = input_list[1] if (input_list[1] != "N/A") else timer_task_df_attribute
    # content
    timer_task_prefix = tasker_config["timer_task_prefix"]
    timer_task_df_content = tasker_config["timer_task_df_content"]
    if input_list[2] == "n":
        if timer_task_df_content != "":
            build_list[6] = timer_task_df_content
        else:
            system_pkg["system_msg"]("Tasker未配置默认timer类task内容(保留原输入)")
            build_list[6] = input_list[2]
    else:
        build_list[6] = input_list[2]
    build_list[6] = timer_task_prefix + build_list[6]
    build_list[7] = input_list[3] # comment
    return build_list

def get_unfinished_timer_index(parameter, tasker, system_pkg) -> int | bool:
    not_end_timer_index = get_not_end_timer_index(tasker)
    if not_end_timer_index == []:
        system_pkg["system_msg"]("无未完成的timer类task")
        return None
    
    user_input = parameter
    if user_input == "":
        # 显示未完成的timer类task
        show_unfinished_timer(not_end_timer_index, tasker, system_pkg)
        user_input = system_pkg["normal_input"](f"输入指示索引")
    # EXIT
    if user_input == system_pkg["EXIT"]: return False
    
    convert_condition = convert_to_int(user_input)
    if convert_condition == None:
        system_pkg["system_msg"](f"指示索引\"{user_input}\"格式错误")
        return None
    select_index = convert_condition
    # 判断索引是否符合
    try:
        return not_end_timer_index[select_index]
    except IndexError:
        system_pkg["system_msg"](f"指示索引\"{select_index}\"不符合")
        return False


def show_set_config_guide(system_pkg):
    system_pkg["tips_msg"]("输入<Enter>跳过设置")
    system_pkg["tips_msg"]("输入\"n\"清除原先预设")

def show_tips_for_select_timer_task(system_pkg) -> None:
    system_pkg["tips_msg"]("输入timer类task的{索引，时间，属性，内容，注释}之一")
    system_pkg["tips_msg"]("输入时间应在其持续时间内，格式形如\"YYYY_MM_DD-HH:SS\"")

def get_the_search_result(search_result_dict) -> list[tuple]:
    """输入字典包含"time", "attribute", "content", "comment", "index"键，数据由find_timer_in_all()返回"""
    options = []
    for key in ["time", "attribute", "content", "comment", "index"]:
        if search_result_dict[key] != []:
            options.append( (search_result_dict[key], key) )
    return options

def show_only_search_result(task_list, index:int, category, system_pkg) -> None:
    system_pkg["head_msg"](f"搜索类别：{category}")
    show_task_info(task_list[index], index, system_pkg)
    return None

def show_timer_task_with_increase_index(index_list, start_index, task_list, system_pkg) -> None:
    instruct_index = start_index
    table_list = []
    heading = ["指示索引", "索引", "start_time", "end_time", "属性", "内容", "comment"]
    table_list.append(heading)
    if type(index_list) == int:
        index_list = [index_list]
    for index in index_list:
        timer_task = task_list[index]
        table_list.append([str(instruct_index),
                           str(index),
                           str(timer_task.start_time),
                           str(timer_task.end_time),
                           str(timer_task.attribute),
                           str(timer_task.content),
                           str(timer_task.comment)])
        instruct_index += 1
    system_pkg["table_msg"](table_list, heading = True)
    return None

def show_many_search_result(options, task_list, system_pkg) -> list:
    combine_index_list = []
    display_index = 0
    for (index_list, category) in options:
        if (index_list == None) or (index_list == []): continue
        # index_list == None -> 索引搜索结果为空

        system_pkg["head_msg"](f"搜索类别：{category}")
        show_timer_task_with_increase_index(index_list, display_index, task_list, system_pkg)
        
        if type(index_list) == int:
            index_list = [index_list]
        display_index += len(index_list)
        combine_index_list += index_list # index_list:list[int]
    return combine_index_list

def choose_from_all_index_list(combine_index_list, system_pkg) -> int | None:
    user_input = system_pkg["normal_input"]("输入指示索引")
    if user_input == system_pkg["EXIT"]:
        return None
    convert_result = convert_to_int(user_input)
    
    if convert_result == None:
        system_pkg["system_msg"](f"指示索引\"{user_input}\"格式错误")
        return None
    user_input = convert_result
    try:
        combine_index_list[user_input]
        return combine_index_list[user_input]
    except IndexError:
        system_pkg["system_msg"](f"指示索引{user_input}不在列表范围内")
        return None
    
def select_from_search_result_options(options:list[tuple], task_list, system_pkg) -> int | None:
    combine_index_list = show_many_search_result(options, task_list, system_pkg)
    choose = choose_from_all_index_list(combine_index_list, system_pkg)
    if choose == None: return None
    return choose

def choose_search_result(user_input, search_result_dict:dict, task_list, system_pkg) -> int | None:
    """输入字典包含"time", "attribute", "content", "comment", "index"键，数据由find_timer_in_all()返回"""
    time_index:list[int] = search_result_dict["time"]
    attr_index:list[int] = search_result_dict["attribute"]
    content_index:list[int] = search_result_dict["content"]
    comment_index:list[int] = search_result_dict["comment"]
    timer_index:int | None = search_result_dict["index"]
    
    result_count =  len(time_index) + len(attr_index) + len(content_index) + len(comment_index)
    if timer_index != None: result_count += 1

    if result_count == 0:
        system_pkg["system_msg"](f"未找到\"{user_input}\"")
        return None
    elif result_count == 1:
        options = get_the_search_result(search_result_dict)
        result, category = options[0][0], options[0][1]
        if type(result) == list:
            index = result[0]
        elif type(result) == int:
            index = result
        show_only_search_result(task_list, index, category, system_pkg)
        return index
    elif result_count > 1:
        options = get_the_search_result(search_result_dict)
        choose = select_from_search_result_options(options, task_list, system_pkg)
        if choose == None: return None
        show_task_info(task_list[choose], choose, system_pkg)
        return choose
    
def select_timer_task(user_input, tasker, system_pkg) -> int | None:
    """int -> 索引
    None -> system_pkg["EXIT"]"""
    if user_input == "":
        show_tips_for_select_timer_task(system_pkg)
        user_input = system_pkg["normal_input"]("输入内容选定task")

    if user_input == system_pkg["EXIT"]: return None
    
    search_result_dict = find_timer_in_all(user_input, tasker)
    
    return choose_search_result(user_input, search_result_dict, tasker.task_list, system_pkg)

def edit_timer_task(index, tasker, system_pkg):
    timer_task = tasker.task_list[index]
    
    # task.start_time
    system_pkg["normal_msg"](f"task.start_time：{timer_task.start_time}")
    user_input = get_YYYY_MM_DD_HH_SS_input("start", system_pkg, allow_empty=True)
    if user_input == False: return None
    elif user_input == "": pass
    else:
        system_pkg["system_msg"](f"start_time：{tasker.task_list[index].start_time} -> {user_input}")
        tasker.task_list[index].start_time = user_input
    
    # task.attribute
    system_pkg["normal_msg"](f"task.attribute：{timer_task.attribute}")
    user_input = get_attribute_input(system_pkg)
    if user_input == False: return None
    elif user_input == "N/A": pass
    else:
        system_pkg["system_msg"](f"attribute：{tasker.task_list[index].attribute} -> {user_input}")
        tasker.task_list[index].attribute = user_input
    
    # task.content
    system_pkg["normal_msg"](f"task.content：{timer_task.content}")
    user_input = get_content_input(system_pkg)
    if user_input == False: return None
    elif user_input == "": pass
    elif user_input == "n":
        system_pkg["system_msg"](f"content：{tasker.task_list[index].content} -> {tasker.timer_task_df_content}")
        tasker.task_list[index].content = tasker.timer_task_df_content
    else:
        system_pkg["system_msg"](f"content：{tasker.task_list[index].content} -> {user_input}")
        tasker.task_list[index].content = tasker.timer_task_prefix + user_input
    
    # task.comment
    system_pkg["normal_msg"](f"task.comment：{timer_task.comment}")
    system_pkg["tips_msg"]("输入\"none\"可清除注释")
    user_input = get_comment_input(system_pkg)
    if user_input == False: return None
    elif user_input == "": pass
    elif user_input == "none":
        system_pkg["system_msg"]("已清除注释")
        tasker.task_list[index].comment = ""
    else:
        system_pkg["system_msg"](f"comment：{tasker.task_list[index].comment} -> {user_input}")
        tasker.task_list[index].comment = user_input
    
    # task.end_time
    system_pkg["normal_msg"](f"task.end_time：{timer_task.end_time}")
    user_input = get_end_time_input(system_pkg)
    if user_input == False: return None
    elif user_input == "": pass
    else:
        system_pkg["system_msg"](f"end_time：{tasker.task_list[index].end_time} -> {user_input}")
        tasker.task_list[index].end_time = user_input
    
    return None

def get_delete_confirm(system_pkg) -> bool:
    user_input = system_pkg["normal_input"]("确认删除该task(y/n)")
    if user_input != "y": return False
    return True

def show_select_del_task_info(timer_task, select_index, system_pkg):
    system_pkg["normal_msg"]("")
    system_pkg["normal_msg"]("--------选定的timer_tasker信息--------")
    show_task_info(timer_task, select_index, system_pkg)

class timer_tasker_func(extra_tasker_func_template):
    def __init__(self):
        super().__init__()
        self.label = "timer_tasker_func"
        self.version = "timer"
        self.function_list = ["new", "edit", "config", "delete", "search", "end"]
        self.create_date = YYYY_MM_DD()
    
    def __str__(self):
        return super().__str__()
    
    def get_info(self):
        return super().get_info()
    
    def proceed(self, cmd_list:list, tasker, system_pkg:dict):
        super().proceed(cmd_list, tasker, system_pkg)
    
    def new(self, parameter, tasker, system_pkg) -> None:
        """创建timer类task，暂无可用参数"""
        system_pkg["normal_msg"]("--------new界面--------")
        # 创建timer类task
        timer_task = create_timer_template(tasker, system_pkg)
        if timer_task == None: return None
        
        # 补充task信息
        tasker_config = get_tasker_config(tasker)
        build_list = input_timer_task_info(tasker_config, system_pkg)
        if build_list == False: return None
        timer_task.build(build_list)
        # 显示创建的task
        show_task_info(timer_task, len(tasker.task_list), system_pkg)
        tasker.task_list.append(timer_task)
        return None

    def edit(self, parameter, tasker, system_pkg) -> None:
        system_pkg["normal_msg"]("--------edit界面--------")
        select_index = select_timer_task(parameter, tasker, system_pkg)
        if select_index == None: return None
        edit_timer_task(select_index, tasker, system_pkg)
        return None

    def config(self, parameter, tasker, system_pkg) -> None:
        system_pkg["normal_msg"]("--------config界面--------")
        show_set_config_guide(system_pkg)
        for func in [set_timer_task_df_attribute,
                     set_timer_task_prefix,
                     set_timer_task_df_content]:
            if func(tasker, system_pkg) == False: return None

    def delete(self, parameter, tasker, system_pkg) -> None:
        select_index = select_timer_task(parameter, tasker, system_pkg)
        if select_index == None: return None
        
        show_select_del_task_info(tasker.task_list[select_index], select_index, system_pkg)
        
        if get_delete_confirm(system_pkg):
            del tasker.task_list[select_index]
            system_pkg["system_msg"]("已删除task")
        
    def search(self, parameter, tasker, system_pkg) -> int | None:
        select_index = select_timer_task(parameter, tasker, system_pkg)
        if select_index == None: return None
        else: return select_index

    def end(self, parameter, tasker, system_pkg) -> None:
        """输入参数为指示索引（第几个未完成的timer类task）"""
        system_pkg["normal_msg"]("--------end界面--------")
        unfinished_timer_index = get_unfinished_timer_index(parameter, tasker, system_pkg)
        if unfinished_timer_index == None or (unfinished_timer_index == False and unfinished_timer_index != 0):
            return None
        current_YYYY_MM_DD_HH_MM = YYYY_MM_DD_HH_MM()
        tasker.task_list[unfinished_timer_index].end_time = current_YYYY_MM_DD_HH_MM
        return None


def get_choice(parameter, system_pkg, msg_func) -> str | None:
    try: msg_func(system_pkg)
    except: pass
    
    user_input = parameter
    if user_input == "":
        user_input = system_pkg["normal_input"]("选定参数")
    
    if user_input == system_pkg["EXIT"]: return None
    else: return user_input

def show_distribution_parameter(system_pkg):
    system_pkg["normal_msg"]("distribution可用参数：")
    system_pkg["body_msg"](["[1]all",
                            "\t统计所有timer_task的start_time, end_time分布箱型图",
                            "[2]attr",
                            "\t统计给定属性下timer_task的start_time, end_time分布箱型图",
                            "[3]date",
                            "\t统计各月timer_task的start_time, end_time分布箱型图"])

def show_count_parameter(system_pkg):
    system_pkg["normal_msg"]("count可用参数：")
    system_pkg["body_msg"](["[1]attr",
                            "\t统计给定属性下timer_task总数，柱状图+饼图",
                            "\t统计给定属性下开始的timer_task总数，柱状图+饼图",
                            "\t统计给定属性下进行中的timer_task总数，柱状图+饼图",
                            "\t统计给定属性下结束的timer_task总数，柱状图+饼图",
                            "[2]date",
                            "\t统计各月timer_task总数，柱状图+饼图",
                            "\t统计各月开始的timer_task总数，柱状图+饼图",
                            "\t统计各月进行中的timer_task总数，柱状图+饼图",
                            "\t统计各月结束的timer_task总数，柱状图+饼图"])

def show_trend_parameter(system_pkg):
    system_pkg["normal_msg"]("trend可用参数：")
    system_pkg["body_msg"](["[1]all",
                            "\t统计所有timer_task的start_time, end_time分布图（随月份推移）",
                            "[2]attr",
                            "\t统计给定属性下timer_task的start_time, end_time分布图（随月份推移）"])

def show_duration_parameter(system_pkg):
    system_pkg["normal_msg"]("duration可用参数：")
    system_pkg["body_msg"](["[1]all",
                            "\t所有timer_task持续时间总和",
                            "\t单项最长持续时间（可包含多项，来自不同属性）",
                            "\t总平均持续时间"
                            "[2]attr",
                            "\t统计给定属性下timer_task持续时间总和",
                            "\t单项最长持续时间（可包含多项）"
                            "\t总平均持续时间"
                            "[3]date",
                            "\t统计各月下timer_task持续时间总和",
                            "\t单项最长持续时间（可包含多项，来自不同属性）",
                            "\t每月平均持续时间（表格）"])

class timer_analyze_func(extra_tasker_func_template):
    def __init__(self):
        super().__init__()
        self.label = "timer_analyze_func"
        self.version = "timer"
        self.function_list = ["distribution", "count", "trend", "duration"]
        self.create_date = YYYY_MM_DD()
        
    def __str__(self):
        return super().__str__()
    
    def get_info(self):
        return super().get_info()
    
    def proceed(self, cmd_list:list, tasker, system_pkg:dict):
        super().proceed(cmd_list, tasker, system_pkg)

    def distribution(self, parameter, tasker, system_pkg) -> None: # 箱型图
        """可选参数all, attr, date"""
        
        func_dict = {"all":self.distribution_all,
                     "attr":self.distribution_attr,
                     "date":self.distribution_date}
        
        user_input = get_choice(parameter, system_pkg, show_distribution_parameter)
        if user_input == None: return None
        else:
            try:
                func_dict[user_input](tasker, system_pkg)
            except KeyError:
                system_pkg["system_msg"](f"{user_input}参数错误")
    
    def distribution_all(self, tasker, system_pkg) -> None:
        pass
    
    def distribution_attr(self, tasker, system_pkg) -> None:
        pass
    
    def distribution_date(self, tasker, system_pkg) -> None:
        pass
    
    def count(self, parameter, tasker, system_pkg) -> None: # 柱状图+饼图
        """可选参数attr, date"""

        func_dict = {"attr":self.count_attr,
                     "date":self.count_date}
        
        user_input = get_choice(parameter, system_pkg, show_distribution_parameter)
        if user_input == None: return None
        else:
            try:
                func_dict[user_input](tasker, system_pkg)
            except KeyError:
                system_pkg["system_msg"](f"{user_input}参数错误")
    
    def count_attr(self, parameter, tasker, system_pkg) -> None:
        pass
    
    def count_date(self, parameter, tasker, system_pkg) -> None:
        pass
    
    def trend(self, parameter, tasker, system_pkg) -> None: # 点图
        """可选参数all attr"""
    
        func_dict = {"all":self.trend_all,
                     "attr":self.trend_attr}
        
        user_input = get_choice(parameter, system_pkg, show_trend_parameter)
        if user_input == None: return None
        else:
            try:
                func_dict[user_input](tasker, system_pkg)
            except KeyError:
                system_pkg["system_msg"](f"{user_input}参数错误")
        
    def trend_all(self, parameter, tasker, system_pkg) -> None:
        pass
    
    def trend_attr(self, parameter, tasker, system_pkg) -> None:
        pass
    
    def duration(self, parameter ,tasker , system_pkg) -> None: # 
        """可选参数all, attr, date"""
        
        func_dict = {"all":self.duration_all,
                     "attr":self.duration_attr,
                     "date":self.duration_date}
        
        user_input = get_choice(parameter, system_pkg, show_duration_parameter)
        if user_input == None: return None
        else:
            try:
                func_dict[user_input](tasker, system_pkg)
            except KeyError:
                system_pkg["system_msg"](f"{user_input}参数错误")
        
    def duration_all(self, parameter, tasker, system_pkg) -> None:
        pass
    
    def duration_attr(self, parameter, tasker, system_pkg) -> None:
        pass
    
    def duration_date(self, parameter, tasker, system_pkg) -> None:
        pass