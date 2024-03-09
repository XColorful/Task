from default_class_func import default_container_func_template
from .function import convert_to_int, convert_to_float, YYYY_MM_DD, YYYY_MM_DD_HH_MM_SS, table_task_template_instance, table_compare_task_list
from os import mkdir
from os.path import exists, join
from glob import glob
from pyperclip import copy as py_cp

class default_container_func(default_container_func_template):
    def __init__(self):
        super().__init__()  # 继承父类
        self.label = "default_container_func"
        self.version = "1.0"
        self.function_list = ["search", "new", "txt", "backup", "edit", "reload"]
        # 供调试时查看信息用，不可见
        self.create_date = YYYY_MM_DD()
    
    def __str__(self):
        return super().__str__()
    
    def get_info(self):
        return super().get_info()

    def proceed(self, command_list:list, container, system_pkg:dict):
        return super().proceed(command_list, container, system_pkg)
    
    def search(self, parameter, container, system_pkg, show_msg = True):
        index_search_result = []
        string_search_result = []
        index_search_index = []
        string_search_index = []
        index_error = False
        task_list_length = len(container.task_list)
        convert_result = convert_to_int(parameter)
        if convert_result != None: # 索引搜索
            try:
                index = convert_result
                task = container.task_list[index]
                if index < 0 : index = task_list_length + index # 索引相反则取为正
                show_string = f"{parameter} -> |{task.date}|{task.attribute}|{task.content}|{task.comment}"
                index_search_index.append(index)
                index_search_result.append(show_string)
            except IndexError:
                index_error = True
        search_count = 1 # 用于展示搜索到的序号
        for task_index in range(0, task_list_length): # 字符串搜索
            task = container.task_list[task_index]
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
    
    def new(self, parameter, container, system_pkg):
        """用空格分隔参数，参数1为索引则选取task模板列表，参数2为"n"开头则创建空模板
        
        """
        task_template_count = 0
        extra_template_count = 0
        for task_template in container.task_template:
            task = task_template()
            if task.type == system_pkg["TYPE_DEFAULT_CONTAINER"]: task_template_count += 1
            else: extra_template_count += 1
        select_task_template_index = 0
        create_empty_task = False
        if extra_template_count != 0: system_pkg["system_pkg"](f"忽略{extra_template_count}项非\"{system_pkg["TYPE_DEFAULT_CONTAINER"]}\"类型task模板")
        if task_template_count == 0: # 无默认类型task模板
            system_pkg["system_msg"]("无可用的默认task模板")
            return None
        elif task_template_count == 1: task_template = container.task_template # 有1个默认类型task模板
        elif task_template_count != 1: # 有多个默认类型task模板
            task_instance_list = []
            for task_template in container.task_template:
                task_instance = task_template()
                task_instance_list.append(task_instance)
            table_task_template_instance(task_instance_list, system_pkg)
            # 选定task模板索引
            user_input = system_pkg["normal_input"]("输入索引")
            if user_input == system_pkg["EXIT"]: return None
            if user_input != "":
                task_template_index = convert_to_int(user_input)
                try:
                    task_template[task_template_index]
                    select_task_template_index = task_template_index
                except IndexError:
                    system_pkg["normal_msg"](f"索引\"{user_input}\"不存在")
                    system_pkg["tips_msg"]("输入<Enter>默认选中索引0")
                    return None
        # 创建空task检查
        empty_check = parameter.split(" ")
        for i in empty_check[1:]: # 检查参数"n"
            try:
                if i[0] == "n": create_empty_task = True
                break
            except: continue
        temp_task = task_template[select_task_template_index]()
        if create_empty_task == True: return None # 判断是否选择创建空task
        
        current_date = YYYY_MM_DD()
        return_tuple = system_pkg["block_input"](f"日期(默认{current_date})", system_pkg["BLOCK_LIST"], system_pkg, block_number = False)
        if return_tuple[0] == False: return None
        if return_tuple[0] == None: date_input = current_date # 默认为当前日期
        else: date_input = return_tuple[1]
        
        return_tuple = system_pkg["block_input"](f"属性(可选)", system_pkg["BLOCK_LIST"], system_pkg, block_number = False)
        if return_tuple[0] == False: return temp_task
        if return_tuple[0] == None: attribute_input = "N/A" # 默认为"N/A"
        else: attribute_input = return_tuple[1]
        
        return_tuple = system_pkg["strict_input"](f"内容", system_pkg["BLOCK_LIST"], system_pkg, block_number = False)
        if return_tuple[0] == False: return None
        else: content_input = return_tuple[1]
        
        return_tuple = system_pkg["block_input"](f"注释(可选)", system_pkg["BLOCK_LIST"], system_pkg, block_number = False)
        if return_tuple[0] == False: return None
        if return_tuple[0] == None: comment_input = ""
        else: comment_input = return_tuple[1]
        
        info_dict = {"create_date":current_date, "date":date_input, "attribute":attribute_input, "content":content_input, "comment":comment_input}
        temp_task.update(info_dict, system_pkg)
        container.task_list.append(temp_task)
        system_pkg["normal_msg"]("已创建task")
        system_pkg["body_msg"]([f"{temp_task.create_date}|{temp_task.date}|{temp_task.attribute}|{temp_task.content}|{temp_task.comment}"])
        return None

    def txt(self, parameter, container, system_pkg):
        """用空格分隔参数，参数为保存路径(?)
        
        这个先不急
        
        """
        pass # 刷新信息
        # 生成txt文件
        pass
    
    def backup(self, parameter, container, system_pkg):
        """暂无实际参数
        
        """
        existed_task_template = {}
        clean_count = 0
        task_list = container.task_list
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
        file_path = join(f"{backup_dir}", f"{container.container_label}_{YYYY_MM_DD_HH_MM_SS()}.txt")
        with open(file_path, "w", encoding = "utf-8") as f:
            function_list = []
            for class_func in container.function_list:
                function_list.append(str(class_func))
            show_function_list = " ".join(function_list)
            # 写入container行
            f.write(f"{container.type}||||{container.version}||||{container.container_label}||||{container.create_date}||||{show_function_list}||||{all_existed_task_template}||||{container.description}\n")
            # 写入task
            for task in task_list:
                backup_str = task.backup()
                if backup_str == "": continue
                f.write(f"\t{backup_str}\n")
        system_pkg["system_msg"](f"已备份至\"{file_path}\"")
        return None

    def edit(self, parameter, container, system_pkg):
        """参数非空时指定搜索对象，为索引或搜索，选取最后一个搜索到的（task_list末端）
        
        """
        index = [] # 存储索引列表
        user_input = parameter # 用于后续判断是否为空输入，操作空task
        if user_input == "":
            system_pkg["tips_msg"]("参数为索引或搜索，选取最后一个搜索到的task（位于列表末端）")
            user_input = system_pkg["normal_input"]("指定编辑对象")
            if user_input == system_pkg["EXIT"]: return None
            if user_input == "": # 搜索空task
                for i in range( len(container.task_list) - 1, -1, -1):
                    if container.task_list[i].create_date == "":
                        index.append(i)
                        break
            else: index = self.search(user_input, container, system_pkg, show_msg = False) # 搜索非空task，返回列表
        else: index = self.search(user_input, container, system_pkg, show_msg = False) # 搜索非空task，返回列表
        # 搜索结果
        if index == []:
            system_pkg["system_msg"]("无指定对象")
            return None
        else: index = index[-1] # 搜索结果选取最后添加的task
        # 输入task编辑内容
        task = container.task_list[int(index)] # 重新取为int
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
    
    def reload(self, parameter, container, system_pkg):
        """暂无实际参数
        
        """
        if container.type != system_pkg["TYPE_DEFAULT_CONTAINER"]:
            system_pkg["system_msg"](f"容器类型\"{container.type}\"不适用于\"{system_pkg["TYPE_DEFAULT_CONTAINER"]}\"类型的方法")
            return None
        backup_dir = ".\\backup_single\\"
        # 读取路径检测
        if not exists(backup_dir): return system_pkg["system_msg"](f"读取路径\"{backup_dir}\"不存在")
        # 显示读取参数
        system_pkg["normal_msg"](f"读取路径\"{backup_dir}\"")
        file_list = glob(join((backup_dir), f"{container.container_label}_*.txt"))
        if file_list == []: return system_pkg["system_msg"](f"无可用的\"{container.container_label}\"备份文件")
        file_list.sort()
        file_path = file_list[-1]
        with open(file_path, "r", encoding = "utf-8") as f:
            txt_list = f.readlines()
            MAX_TXT_LIST_INDEX = len(txt_list)
            check_index = 0
            # container信息读取
            container_check = False
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
                    container_type, container_version = check_list[0:2]
                except ValueError:
                    system_pkg["body_msg"]([f"Line{check_index}:缺少[类型, 版本]"])
                # container.type
                if container_type != container.type:
                    system_pkg["body_msg"]([f"Line{check_index}:容器类型\"{container_type}\"不匹配"])
                    check_index += 1
                    continue
                # container.version
                container_version = convert_to_float(container_version)
                if (container_version == None) or (container_version > (convert_to_float(container.version))):
                    system_pkg["body_msg"]([f"Line{check_index}:容器版本\"{container_version}\"不匹配"])
                    check_index += 1
                    continue
                try:
                    container_container_label, container_create_date, container_function_list, container_task_template, container_description = check_list[2:7]
                except ValueError:
                    system_pkg["body_msg"]([f"Line{check_index}:缺少完整数据[容器标签, 创建日期, 功能列表, task模板, 容器描述]"])
                    check_index += 1
                    continue
                # container.container_label
                if container_container_label != container.container_label:
                    system_pkg["body_msg"]([f"Line{check_index}:容器标签\"{container_container_label}\"不匹配"])
                    check_index += 1
                    continue
                # container.create_date
                if container_create_date != container.create_date:
                    system_pkg["body_msg"]([f"Line{check_index}:容器创建日期\"{container_create_date}\"不匹配"])
                    
                    if system_pkg["normal_input"]("更改原容器创建日期(y/n)") != "y":
                        check_index += 1
                        continue
                    container.create_date = container_create_date

                # container.funciton_list
                function_list = container_function_list.split(" ")
                if len(function_list) % 3 != 0:
                    system_pkg["body_msg"]([f"Line{check_index}:容器功能列表\"{function_list}\"格式错误"])
                    check_index += 1
                    continue
                for index in range(0, len(function_list), 3):
                    function_label, function_version, function_type = function_list[index:index+3]
                    # 对于每一个class_func
                    check = False
                    for class_func in container.function_list:
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
                        system_pkg["body_msg"]([f"Line{check_index}:容器功能列表\"{function_list}\"有不适用功能"])
                # container.task_template
                task_template_list = container_task_template.split(" ")
                if len(task_template_list) % 2 != 0:
                    system_pkg["body_msg"]([f"Line{check_index}:容器task模板\"{container_task_template}\"格式错误"])
                    check_index += 1
                    continue
                for index in range(0, len(task_template_list), 2):
                    task_type, task_version = task_template_list[index:2]
                    # 对于每一个task_template
                    check = False
                    for task_template in container.task_template:
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
                        system_pkg["body_msg"]([f"Line{check_index}:容器task模板\"{task_template_list}\"有不适用模板"])
                # container.description
                if container_description != container.description:
                    
                    if system_pkg["normal_input"]("更改原容器描述(y/n)") != "y":
                        check_index += 1
                        continue
                    container.description = container_description

                container_check = True
                check_index += 1
                break
            # container信息检测
            if container_check == False: return system_pkg["system_msg"](f"识别容器信息失败，请检查备份文件\"{file_path}\"")
            system_pkg["system_msg"](f"读取到容器{container.container_label}")
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
                for task_template in container.task_template:
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
            table_compare_task_list(container.task_list, task_list, system_pkg, display = 8)
            # 确认读取task_list
            user_input = system_pkg["normal_input"]("确认读取(y/n)")
            if user_input != "y": return None
            # 覆写task_list
            container.task_list = task_list
            system_pkg["system_msg"](f"已读取\"{file_path}\"")
            return None