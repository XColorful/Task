from default_class_func import extra_tasker_func_template
from .function import YYYY_MM_DD, YYYY_MM_DD_HH_MM_SS, convert_to_int, input_tasker_attr_input_map, input_tasker_convenient_input, get_search_result_save_dir
from .const import CREATE_ATTR, CONTENT_ATTR
from os import getcwd
from os.path import join
def normal_user_input(user_input, system_pkg) -> str | None:
    if user_input == "":
        user_input = system_pkg["normal_input"]("输入搜索内容")
    
    if user_input == system_pkg["EXIT"]:
        return None
    else:
        return user_input

def get_paired_attr_result(user_input, tasker) -> tuple:
    """返回数据格式：
    
    tuple(pair_attr_list, paired_attr_count)
    
    paired_attr_list = [ (task_index:int, [attr1:int|str, attr2:int|str, attr3:str, ...] ) ]
    
    paired_attr_count = {"attr1":int, "attr2":int, ...}, attr1:int|str"""
    def add_to_dict(key, dict):
        try:
            dict[key] += 1
        except KeyError:
            dict[key] = 1
    
    task_list = tasker.task_list
    
    paired_attr_list = []
    paired_attr_count = {}
    
    for index, task in enumerate(task_list):
        if task.version != tasker.version: continue
        
        
        pair = False
        queue_attr_list = []
        
        if user_input in task.create_date:
            queue_attr_list.append(CREATE_ATTR)
            add_to_dict(CREATE_ATTR, paired_attr_count)
            pair = True
        if user_input in task.content:
            queue_attr_list.append(CONTENT_ATTR)
            add_to_dict(CONTENT_ATTR, paired_attr_count)
            pair = True
        for (attr, label) in task.label_list:
            if (user_input in attr) or (user_input in label):
                queue_attr_list.append(str(attr))
                add_to_dict(attr, paired_attr_count)
                pair = True
        
        if pair == True:
            paired_attr_list.append( (index, queue_attr_list) )
    
    return (paired_attr_list, paired_attr_count)

def select_attr_filter(paired_attr_count, system_pkg) -> dict | None:
    """filtered_dict格式与get_paired_attr_result -> paired_attr_count相同
    
    paired_attr_count = {"attr1":int, "attr2":int, ...}, attr1:int|str"""
    def make_original_dict(paired_attr_count, create_attr_count, content_attr_count):
        if create_attr_count > 0:
            paired_attr_count[CREATE_ATTR] = create_attr_count
        if content_attr_count > 0:
            paired_attr_count[CONTENT_ATTR] = content_attr_count
        return paired_attr_count
    def add_two_special_attr(items_list, create_attr_count, content_attr_count):
        """补充提前删去的两attr"""
        if content_attr_count > 0:
            items_list.insert(0, (CONTENT_ATTR, content_attr_count) )
        if create_attr_count > 0:
            items_list.insert(0, (CREATE_ATTR, create_attr_count) )
    
    if len(paired_attr_count) < 2:
        return paired_attr_count
    
    create_attr_count = 0
    content_attr_count = 0
    try:
        create_attr_count = paired_attr_count[CREATE_ATTR]
        del paired_attr_count[CREATE_ATTR]
    except KeyError: pass
    try:
        content_attr_count = paired_attr_count[CONTENT_ATTR]
        del paired_attr_count[CONTENT_ATTR]
    except KeyError: pass
    items_list = list(paired_attr_count.items())
    
    index = 0
    table_list = []
    heading = ["索引", "属性", "数量"]
    table_list.append(heading)
    
    
    # 特殊属性优先
    if create_attr_count > 0:
        table_list.append( [str(index), "|create_date|", str(create_attr_count)] )
        index += 1
    if content_attr_count > 0:
        table_list.append( [str(index), "|content|", str(content_attr_count)] )
        index += 1
    
    # 其他标签
    for paired_attr, attr_count in items_list:
        table_list.append( [str(index), str(paired_attr), str(attr_count)])
        index += 1
    system_pkg["table_msg"](table_list, heading = True)
    system_pkg["tips_msg"]("输入类型（用空格分隔，依次处理）")
    system_pkg["tips_msg"]("[1]\"all\"/\"索引\" -> 选中属性，包含选中属性的结果将展示")
    system_pkg["tips_msg"]("[2]\"减号\" + \"all\"/\"索引\" -> 若结果展示，则不展示该属性")
    if (create_attr_count > 0) or (content_attr_count > 0):
        system_pkg["tips_msg"]("注：<create_date>默认隐藏，<content>默认勾选")

    # 补充content和create_date属性
    add_two_special_attr(items_list, create_attr_count, content_attr_count)
    
    # 选定内容
    user_input = system_pkg["normal_input"]("选定索引")
    if user_input == system_pkg["EXIT"]: return None
    
    index_input_list = user_input.split(" ")
    filter_dict = {}
    for index in index_input_list:
        # 反选检测
        invert = False
        try:
            if index[0] == "-":
                invert = True
                index = index[1:]
        except IndexError: pass
        
        # 连续空格
        if index == "":
            continue
        # 全选
        elif index == "all":
            if invert == False:
                filter_dict = make_original_dict(paired_attr_count, create_attr_count, content_attr_count)
            else:
                filter_dict = all_to_negative_dict(make_original_dict(paired_attr_count, create_attr_count, content_attr_count))
            continue
        # 索引
        else:
            convert_result = convert_to_int(index)
            # 转换失败
            if convert_result == None:
                system_pkg["system_msg"](f"已跳过格式不符的输入(\"{index}\")")
                continue
            index = convert_result
            key = items_list[index][0]
            if invert == True: # 反选
                filter_dict[key] = -1
            else: # 添加
                filter_dict[key] = items_list[index][1]
    
    return filter_dict

def all_to_negative_dict(input_dict) -> dict:
    """输入字典value均为int，生成新字典，值均为-1"""
    negative_dict = {}
    for key in input_dict:
        negative_dict[key] = -1
    return negative_dict

def postive_to_zero_dict(input_dict) -> dict:
    """输入字典value均为int，生成新字典，正数改为0，负数不影响"""
    zero_dict = {}
    for key, value in list(input_dict.items()):
        if value > 0:
            zero_dict[key] = 0
        else:
            zero_dict[key] = value
    return zero_dict

def should_display_search_result(task, attr_filter_dict) -> bool:
    try:
        if attr_filter_dict[CONTENT_ATTR] > 0: # attr包含self.content
            return True
    except KeyError:
        # task.content默认勾选
        return True
    try:
        if attr_filter_dict[CREATE_ATTR] > 0: # attr包含self.create_date
            return True
    except KeyError:
        # task.create_date默认隐藏
        pass

    has_attr = False
    for label_pair in task.label_list:
        attr = label_pair[0]
        try:
            if attr_filter_dict[attr] > 0: # -1为过滤
                has_attr = True
                break
        except KeyError: # 未保留或过滤该属性
            continue
    return has_attr

def make_search_display_content(task, search_index, attr_filter_count, attr_filter_dict:dict) -> tuple:
    """get_paired_attr_result() -> paired_attr_list[1] -> attr_filter_count = [attr1:int|str, attr2:int|str, attr3:str, ...]"""
    
    
    # attr = 0 为需过滤的属性
    main_line = f"[{search_index}]"
    body_list = []
    
    if should_display_search_result(task, attr_filter_dict):
        # task.content默认勾选
        try:
            if attr_filter_dict[CONTENT_ATTR] <= 0:
                main_line += "（已过滤该属性）"
            else:
                main_line += f"{task.content}"
        except KeyError:
            main_line += f"{task.content}"
        # task.create_date默认隐藏
        try:
            if attr_filter_dict[CREATE_ATTR] > 0:
                main_line += f"（create_date：{task.create_date}）"
        except KeyError: pass
        # task.label_list
        for label_pair in task.label_list:
            attr = label_pair[0]
            label = label_pair[1]
            try:
                if attr_filter_dict[attr] <= 0:
                    body_list.append("（已过滤该属性）")
                else:
                    attr_filter_count[attr] += 1 # attr_filter_count从0开始
                    body_list.append(f"({attr_filter_count[attr]}/{attr_filter_dict[attr]})<{attr}>|{label}")
            except KeyError:
                # 未保留或过滤的属性
                body_list.append(f"<{attr}>|{label}")
    else:
        main_line += "（未包含选中属性）"
    
    return main_line, body_list

def save_search_result_to_txt(tasker, paired_attr_list, attr_filter_dict, system_pkg):
    def write_search_result(f, task, attr_filter_dict):
        main_line = ""
        try:
            if attr_filter_dict[CONTENT_ATTR] < 0:
                main_line += "（已过滤）"
            else:
                main_line += f"{task.content}"
        except KeyError:
            main_line += f"{task.content}"
        try:
            if attr_filter_dict[CREATE_ATTR] > 0:
                main_line += f"({task.create_date})"
            else: pass
        except KeyError: pass
        f.write(f"{main_line}\n")
        
        for label_pair in task.label_list:
            attr = label_pair[0]
            label = label_pair[1]
            try:
                if attr_filter_dict[label] < 0:
                    f.write("\t（已过滤）\n")
                else:
                    f.write(f"\t<{attr}>|{label}\n")
            except KeyError:
                f.write(f"\t<{attr}>|{label}\n")
    
    def write_attr_filter_dict(f, attr_filter_dict):
        f.write(f"attr_filter_dict：\n")
        try:
            attr_filter_dict["|content|"] = attr_filter_dict[CONTENT_ATTR]
            del attr_filter_dict[CONTENT_ATTR]
        except KeyError: pass
        try:
            attr_filter_dict["|create_date|"] = attr_filter_dict[CREATE_ATTR]
            del attr_filter_dict[CREATE_ATTR]
        except KeyError: pass
        
        items_list = list(attr_filter_dict)
        items_list.sort()
        for key, value in items_list:
            f.write(f"{key}|{value}\n")
        
    def write_system_info(f, cwd, dir):
        f.write(f"当前工作目录：{cwd}\n")
        f.write(f"保存路径{dir}\n")
        f.write(f"方法label_tasker_func，版本label，使用指令search\n")
    
    task_list = tasker.task_list

    cwd = getcwd()
    dir = get_search_result_save_dir(cwd, system_pkg)
    with open(join(dir, f"search_result_{YYYY_MM_DD_HH_MM_SS()}.txt"), "w", encoding="utf-8") as f:
        for task_index, attr_list in paired_attr_list:
            task = task_list[task_index]
            write_search_result(f, task, attr_filter_dict)
        f.write("||||end\n")
        write_attr_filter_dict(f, attr_filter_dict)
        f.write("||||end\n")
        write_system_info(f, cwd, dir)
    
def display_filterd_result(tasker, paired_attr_list, attr_filter_dict, system_pkg):
    """get_paired_attr_result() -> paired_attr_list
    
    = [ (task_index:int, [attr1:int|str, attr2:int|str, attr3:str, ...] ) ]
    
    select_attr_filter() -> attr_filter_dict
    
    = {"attr1":int, "attr2":int, ...}, attr1:int|str"""
    
    search_index = 1 # 用于显示搜索结果的序号
    task_list = tasker.task_list
    
    if len(paired_attr_list) == 0:
        system_pkg["system_msg"]("无搜索结果")
        return None
    system_pkg["head_msg"](f"搜索结果（{len(paired_attr_list)}个）")
    
    attr_filter_count = postive_to_zero_dict(attr_filter_dict) # 用于统计已经展示多少个attr，负数值不影响
    for task_index, attr_list in paired_attr_list:
        main_line, body_list = make_search_display_content(task_list[task_index], search_index, attr_filter_count, attr_filter_dict)
        system_pkg["normal_msg"](main_line)
        system_pkg["body_msg"](body_list)
        search_index += 1
    return None


class label_tasker_func(extra_tasker_func_template):
    def __init__(self):
        super().__init__()
        self.label = "label_tasker_func"
        self.version = "label"
        self.function_list = ["new", "delete", "edit", "search", "config"]
        self.create_date = YYYY_MM_DD()
    
    def __str__(self):
        return super().__str__()
    
    def get_info(self):
        return super().get_info()
    
    def proceed(self, cmd_list:list, tasker, system_pkg:dict):
        super().proceed(cmd_list, tasker, system_pkg)
    
    def new(self, parameter, tasker, system_pkg) -> None:
        system_pkg["system_pkg"]("待完成")
        return None
    
    def delete(self, parameter, tasker, system_pkg) -> None:
        system_pkg["system_pkg"]("待完成")
        return None
    
    def edit(self, parameter, tasker, system_pkg) -> None:
        system_pkg["system_pkg"]("待完成")
        return None
    
    def search(self, parameter, tasker, system_pkg) -> None:
        user_input = normal_user_input(parameter, system_pkg)
        if user_input == None: return None
        
        paired_attr_list, paired_attr_count = get_paired_attr_result(user_input, tasker)
        
        attr_filter_dict = select_attr_filter(paired_attr_count, system_pkg)
        if attr_filter_dict == None:
            return None
        
        display_filterd_result(tasker, paired_attr_list, attr_filter_dict, system_pkg)
        save_search_result_to_txt(tasker, paired_attr_list, attr_filter_dict, system_pkg)
        return None
    
    def config(self, parameter, tasker, system_pkg) -> None:
        
        input_tasker_attr_input_map(tasker, system_pkg)
        
        input_tasker_convenient_input(tasker, system_pkg)
        
        return None


class label_analyze_func(extra_tasker_func_template):
    def __init__(self):
        super().__init__()
        self.label = "label_tasker_func"
        self.version = "label"
        self.function_list = ["details", "list_label"]
        self.create_date = YYYY_MM_DD()
    
    def __str__(self):
        return super().__str__()
    
    def get_info(self):
        return super().get_info()
    
    def proceed(self, cmd_list:list, tasker, system_pkg:dict):
        super().proceed(cmd_list, tasker, system_pkg)
    
    def details(self, parameter, tasker, system_pkg) -> None:
        """统计相关数据"""
        system_pkg["system_pkg"]("待完成")
        return None
    
    def list_label(self, parameter, tasker, system_pkg) -> None:
        """输入标签，查找，分析相关信息"""
        system_pkg["system_pkg"]("待完成")
        return None