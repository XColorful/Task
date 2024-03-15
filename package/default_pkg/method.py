from default_method import default_method_template
from .function import convert_to_int, convert_to_float, table_container_list, table_container_template, YYYY_MM_DD_HH_MM_SS, table_backup_file
from os import mkdir
from os.path import exists, join, dirname, abspath
from glob import glob

class default_method(default_method_template):
    def __init__(self):
        super().__init__() # 继承父类
        self.label = "default_method"
        self.version = "1.0"
        self.method_list = ["get", "add", "delete", "search", "edit", "backup", "reload"]
    
    def method_info(self):
        return super().method_info()
    
    def analyze(self, command_list:list, container_list:list, system_pkg:dict): # 分析是否存在可用指令，返回(bool，[标签，版本，类型])
        return super().analyze(command_list, container_list, system_pkg)

    def proceed(self, command_list:list, container_list:list, system_pkg:dict):
        return super().proceed(command_list, container_list, system_pkg)
    
    def get(self, command_parameter:str, container_list:list, system_pkg:dict): # 获取container列表，进入container.interface()
        get_index = "" # 用于get的索引
        MAX_INDEX = len(container_list) - 1
        if MAX_INDEX == -1:
            system_pkg["system_msg"]("container_list为空，请先用指令\"add\"创建一个container")
            return (system_pkg["CONDITION_SUCCESS"], "container_list为空")
        # 展示container_list
        table_container_list(range(0, MAX_INDEX +1), container_list, system_pkg)
        # 获取container_list索引值
        while get_index == "":
            # 获取user_input
            if command_parameter != "": # 有参数则跳过首次获取user_input
                user_input = command_parameter
            else:
                system_pkg["tips_msg"]("匹配首个符合的标签，输入\"exit\"退出")
                user_input = system_pkg["normal_input"]("输入索引或标签")
            if user_input == system_pkg["EXIT"]: return (system_pkg["CONDITION_SUCCESS"], "exit")
            
            if user_input != "": # 用户输入不为空字符串
                # 索引判断
                convert_result = convert_to_int(user_input)
                if convert_result != None:
                    if 0 <= convert_result <= MAX_INDEX:
                        get_index = convert_result
                        break
                # 标签判断
                index_list = []
                for container_index in range(0, MAX_INDEX + 1): # 对于每一个container
                    container_label = container_list[container_index].container_label
                    if user_input in container_label:
                        index_list.append(container_index)
                        if user_input == container_label:
                            index_list = [container_index]
                            break # 完全匹配则退出

                if len(index_list) == 1: # 用户输入有一项匹配，自动获取索引
                    get_index = index_list[0]
                    break
                elif len(index_list) == 0: # 用户输入非空字符串，但没有匹配
                    system_pkg["system_msg"](f"没有找到\"{user_input}\"")
                else: # 用户输入有多项匹配，仅显示筛选的container
                    table_container_list(index_list, container_list, system_pkg)
        # 进入container.instance()界面
        return_tuple = container_list[get_index].interface(system_pkg) # 进入container.interface()并提供system_pkg
        return return_tuple
    
    def add(self, command_parameter:str, container_list:list, system_pkg:dict): # 添加container
        df_container_template_list = system_pkg["df_container_template_list"]
        ex_container_template_list = system_pkg["ex_container_template_list"]
        container_template_list = df_container_template_list + ex_container_template_list
        if container_template_list == []:
            system_pkg["system_msg"]("没有可用的container模板")
            return (system_pkg["CONDITION_SUCCESS"], "无container模板")
        # 选定container_template
        if command_parameter != "": # 用参数预输入
            user_input = command_parameter
        else: # 无参数预输入
            # 展示container_template
            container_label_list = table_container_template(container_template_list, system_pkg)
            system_pkg["tips_msg"]("匹配首个符合的标签，输入\"exit\"取消创建")
            user_input = system_pkg["normal_input"]("输入索引或标签")
        if user_input == system_pkg["EXIT"]: return (system_pkg["CONDITION_SUCCESS"], "取消添加container模板")
        convert_result = convert_to_int(user_input)
        if convert_result != None: # 用户输入为int
            MAX_INDEX = len(container_template_list) - 1
            if 0 <= convert_result <= MAX_INDEX:
                container_template_list_index = convert_result
            else:
                system_pkg["system_msg"](f"索引值{user_input}超出范围(0 ~ {MAX_INDEX})")
                return (system_pkg["CONDITION_SUCCESS"], f"索引值{user_input}超出范围(0 ~ {MAX_INDEX})")
        else: # 用户输入不为int
            try:
                for index in range(0, len(container_label_list)):
                    if user_input in container_label_list[index]:
                        container_template_list_index = index
                        break
            except ValueError:
                system_pkg["system_msg"](f"容器标签{user_input}不匹配")
                return (system_pkg["CONDITION_SUCCESS"], f"容器标签{user_input}不匹配")
        # 创建container实例
        container_instance = container_template_list[container_template_list_index]()
        container_list.append(container_instance)
        # 确认是否立即更新信息
        user_input = system_pkg["normal_input"]("是否立即补充容器信息(y/n)")
        if user_input != "y": return (system_pkg["CONDITION_SUCCESS"], "不补充容器信息")
        container_list[-1].update_info(system_pkg); return (system_pkg["CONDITION_SUCCESS"], "立即补充容器信息")
    
    def delete(self, command_parameter:str, container_list:list, system_pkg:dict): # 删除container，尝试创建备份文件
        get_index = "" # 用于get的索引
        MAX_INDEX = len(container_list) - 1
        if MAX_INDEX == -1:
            system_pkg["system_msg"]("container_list为空，请先用指令\"add\"创建一个container")
            return (system_pkg["CONDITION_SUCCESS"], "container_list为空")
        # 展示container_list
        table_container_list(range(0, MAX_INDEX +1), container_list, system_pkg)
        # 获取container_list索引值
        while get_index == "":
            # 获取user_input
            if command_parameter != "": # 有参数则跳过首次获取user_input
                user_input = command_parameter
            else:
                system_pkg["tips_msg"]("匹配首个符合的标签，输入\"exit\"退出")
                user_input = system_pkg["normal_input"]("输入索引或标签")
            if user_input == "exit": return (system_pkg["CONDITION_SUCCESS"], "exit")
            
            if user_input != "": # 用户输入不为空字符串
                # 索引判断
                convert_result = convert_to_int(user_input)
                if convert_result != None:
                    if 0 <= convert_result <= MAX_INDEX:
                        get_index = convert_result
                        break
                # 标签判断
                index_list = []
                for container_index in range(0, MAX_INDEX + 1): # 对于每一个container
                    container_label = container_list[container_index].container_label
                    if user_input in container_label:
                        index_list.append(container_index)
                        if user_input == container_label:
                            index_list = [container_index]
                            break # 完全匹配则退出

                if len(index_list) == 1: # 用户输入有一项匹配，自动获取索引
                    get_index = index_list[0]
                    break
                elif len(index_list) == 0: # 用户输入非空字符串，但没有匹配
                    system_pkg["system_msg"](f"没有找到\"{user_input}\"")
                else: # 用户输入有多项匹配，仅显示筛选的container
                    table_container_list(index_list, container_list, system_pkg)
        # 进入container.instance()界面
        select_container_label = container_list[get_index].container_label
        table_container_list([get_index], container_list, system_pkg)
        user_input = system_pkg["normal_input"](f"确认删除{select_container_label}(y/n)")
        if user_input == "y": 
            del container_list[get_index]
            system_pkg["system_msg"](f"已删除\"{select_container_label}\"")
        return (system_pkg["CONDITION_SUCCESS"], f"删除container{select_container_label}")
    
    def search(self, command_parameter:str, container_list:list, system_pkg:dict): # 调用container可用的search()
        return (system_pkg["CONDITION_SUCCESS"], None)
    
    def edit(self, command_parameter:str, container_list:list, system_pkg:dict): # 编辑container信息，单独编辑，使用container内置函数
        # 更改container_label, description, create_date
        return (system_pkg["CONDITION_SUCCESS"], None)
    
    def backup(self, command_parameter:str, container_list:list, system_pkg:dict): # 备份container，全局备份
        backup_dir = ".\\backup_all\\"
        if not exists(backup_dir): mkdir(backup_dir)
        file_path = join(f"{backup_dir}", f"backup_{YYYY_MM_DD_HH_MM_SS()}.txt")
        working_dir = dirname(abspath(__file__))
        container_count = 0
        task_count = 0
        f = open(file_path, "w", encoding = "utf-8")
        for container in container_list:
            build_list = container.backup_list()
            # [self.type, self.version, self.container_label, self.create_date, function_list, self.task_template, self.description]
            # function_list format: [func.label, func.version, func.type]
            function_list = []
            for i in build_list[4]:
                function_list.append(" ".join([i[0], i[1], i[2]]))
            function_list = " ". join(function_list)
            # task_template format: [task.type, task.version]
            task_template = []
            for i in build_list[5]:
                task_template.append(" ".join([i[0], i[1]]))
            task_template = " ".join(task_template)
            # container行
            build_list[4], build_list[5] = function_list, task_template
            build_list = "||||".join(build_list)
            # 写入container行
            f.write(f"{build_list}\n")
            container_count += 1
            for task in container.task_list:
                build_list = task.backup_list()
                build_list = "||||".join(build_list)
                f.write(f"\t{build_list}\n")
                task_count += 1
        # 结束备份内容
        f.write(f"/end\n")
        backup_info = [f"共计{container_count}个容器，{task_count}个task",
                       f"当前工作目录{working_dir}",
                       f"完整路径{working_dir}{file_path[1:]}",
                       f"方法{self.label}，版本{self.version}，使用指令{"backup"}"]
        # 写入备份信息
        for i in backup_info: f.write(f"{i}\n")
        f.close()
        system_pkg["system_msg"](f"已备份至\"{file_path}\"")
        system_pkg["body_msg"](backup_info)
        return (system_pkg["CONDITION_SUCCESS"], f"生成备份文件{working_dir}{file_path[1:]}")
    
    def reload(self, command_parameter:str, container_list:list, system_pkg:dict): # 从.\\backup\\的txt文件读取container及其task_list，显示备份文件中不可用的模板，统计所有出现的类型及数量
        """参数第一个字符为"u"则自动升级可用版本，参数第一个字符为"n"则取消升级"""
        AUTO_UPDATE = False
        try:
            if command_parameter[0] == "u":
                AUTO_UPDATE = True
            elif command_parameter[0] == "n":
                AUTO_UPDATE = None
        except IndexError: AUTO_UPDATE = False
        
        def report_error(txt_list:list, container_index:int, task_index:int, error_message:str, system_pkg:dict):
            container_index += 1
            task_index += 1
            system_pkg["error_msg"](error_message)
            system_pkg["system_msg"](f"输出备份文件（{container_index} - {task_index}）")
            body_list = []
            body_list.append("--------容器行--------")
            body_list.append(f"line[{container_index}] -> |{txt_list[container_index][:-1]}")
            if task_index > container_index:
                body_list.append("--------task行--------")
                for index in range(container_index + 1, task_index + 1):
                    body_list.append(f"line[{index}] -> |{txt_list[index][:-1]}")
            system_pkg["body_msg"](body_list)
        
        def compare_selection(container_list:list, system_pkg:dict, selection_type:str):
            table_list = []
            heading = ["索引", f"{selection_type}类型", "版本"]
            table_list.append(heading)
            for index, pair_list in enumerate(container_list):
                container_type, container_version = pair_list
                table_list.append([str(index), container_type.type, container_version])
            system_pkg["table_msg"](table_list, heading = True)
        backup_dir = ".\\backup_all\\"
        file_list = glob(join((backup_dir), "backup_*.txt"))
        file_list.sort()
        if file_list == []:
            system_pkg["system_msg"]("无可导入的备份文件")
            return (system_pkg["CONDITION_SUCCESS"], "无可导入的备份文件")
        working_dir = dirname(abspath(__file__))
        system_pkg["system_msg"](f"当前工作路径{working_dir}")
        display_list = file_list[:]
        display_list[-1] = display_list[-1] + "（默认）"
        table_backup_file(display_list, system_pkg)
        system_pkg["tips_msg"]("<Enter>选中默认（最新）")
        user_input = system_pkg["normal_input"]("输入索引")
        if user_input == system_pkg["EXIT"]: return (system_pkg["CONDITION_SUCCESS"], "取消导入备份文件")
        user_input = convert_to_int(user_input)
        if user_input == None: user_input = -1
        try:
            file_path = file_list[user_input]
        except IndexError:
            system_pkg["system_msg"](f"索引\"{user_input}\"错误")
            return (system_pkg["CONDITION_SUCCESS"], "取消导入备份文件（输入索引错误）")
        f = open(file_path, "r", encoding = "utf-8")
        txt_list = f.readlines()
        current_container_index = 0
        current_task_index = 0
        temp_container_list = []
        garbage_task_count = 0 # 用于统计无归属container的task
        for index, txt_line in enumerate(txt_list):
            txt_line = txt_line[:-1] # 去除最右的\n
            if txt_line == "/end": break
            elif txt_line == "":
                continue
            if txt_line[0] != "\t": # 创建container
                current_container_index = index
                current_task_index = index
                build_list = txt_line.split("||||")
                # 长度至少为以下形式，拓展部分在container内部处理
                # [self.type, self.version, self.container_label, self.create_date, function_list, task_template_list, self.description]
                try:
                    is_default_type =  build_list[0] == system_pkg["TYPE_DEFAULT_CONTAINER"]
                    if is_default_type == True:
                        read_version = convert_to_float(build_list[1])
                        if read_version == None:
                            report_error(txt_list, current_container_index, current_task_index, f"容器版本\"{build_list[0]}\"错误", system_pkg)
                            return (system_pkg["CONDITION_FAIL"], "读取备份文件错误")
                    
                    find_container = False
                    select_container = []
                    # 遍历可用的container模板
                    iterator = system_pkg["df_container_template_list"]
                    if is_default_type == False: iterator = system_pkg["ex_container_template_list"]
                    for container_template in iterator:
                        container = container_template()
                        if is_default_type: # container为default类型
                            if read_version <= convert_to_float(container.version):
                                container.build(build_list, system_pkg)
                                select_container.append([container, container.version])
                                find_container = True
                        else: # container为extra类型
                            if build_list[1] == container.version:
                                container.build(build_list, system_pkg)
                                find_container = True
                                temp_container_list.append(container)
                                break
                    if find_container == True:
                        if is_default_type == True:
                            select_container.sort(key = lambda x: x[0])
                            if AUTO_UPDATE == None: temp_container_list.append(select_container[-1][0])
                            elif AUTO_UPDATE == True: temp_container_list.append(select_container[-1][0])
                            elif AUTO_UPDATE == False:
                                if len(select_container) != 1: # 若有多项可选
                                    compare_selection(select_container, system_pkg, "容器")
                                    user_input = system_pkg["normal_input"]("输入索引")
                                    if user_input == system_pkg["EXIT"]: return ("CONDITION_SUCCESS", "取消读取备份文件")
                                    user_input = convert_to_int(user_input)
                                    if user_input != None:
                                        try:
                                            temp_container_list.append(select_container[user_input][0])
                                            continue # 输入成功
                                        except IndexError:
                                            pass
                                    system_pkg["system_msg"](f"索引\"{user_input}\"不存在")
                                    return ("CONDITION_SUCCESS", "输入备份文件容器类型索引错误")
                                else: # 若只有一项可选
                                    temp_container_list.append(select_container[0][0])
                        continue # 若为extra类型则跳过以上判断
                    else:
                        report_error(txt_list, current_container_index, current_task_index, f"容器版本\"{build_list[0]}\"不可用", system_pkg)
                        return (system_pkg["CONDITION_FAIL"], "读取备份文件错误")
                except KeyError:
                    report_error(txt_list, current_container_index, current_task_index, f"容器类型\"{build_list[0]}\"不存在", system_pkg)
                    return (system_pkg["CONDITION_FAIL"], "读取备份文件错误")
            
            else: # 行开头为"\t" -> task
                if len(temp_container_list) == 0:
                    garbage_task_count += 1
                    continue
                current_task_index = index
                txt_line = txt_line[1:]
                build_list = txt_line.split("||||")
                # 长度至少为以下形式，拓展部分在task内部处理
                # [self.type, self.version, self.create_date, self.date, self.attribute, self.content, self.comment]
                try:
                    is_default_type =  build_list[0] == system_pkg["TYPE_DEFAULT_CONTAINER"]
                    if is_default_type == True:
                        read_version = convert_to_float(build_list[1])
                        if read_version == None:
                            report_error(txt_list, current_container_index, current_task_index, f"task版本\"{build_list[0]}\"错误", system_pkg)
                            return (system_pkg["CONDITION_FAIL"], "读取备份文件错误")
                    
                    find_task = False
                    select_task = []
                    # 遍历可用的task模板
                    iterator = system_pkg["df_task_template_list"]
                    if is_default_type == False: iterator = system_pkg["ex_task_template_list"]
                    for task_template in iterator:
                        task = task_template()
                        if is_default_type: # task为default类型
                            if read_version <= convert_to_float(task.version):
                                task.build(build_list) # task的build不需要system_pkg
                                select_task.append([task, task.version])
                                find_task = True
                        else: # task为extra类型
                            if build_list[1] == task.version:
                                task.build(build_list) # task的build不需要system_pkg
                                find_task = True
                                temp_container_list[-1].task_list.append(task)
                                break
                    if find_task == True:
                        if is_default_type == True:
                            select_task.sort(key = lambda x: x[0])
                            if AUTO_UPDATE == None: temp_container_list[-1].task_list.append(select_task[-1][0])
                            elif AUTO_UPDATE == True: temp_container_list[-1].task_list.append(select_task[-1][0])
                            elif AUTO_UPDATE == False:
                                if len(select_task) != 1: # 若有多项可选
                                    compare_selection(select_task, system_pkg, "task")
                                    user_input = system_pkg["normal_input"]("输入索引")
                                    if user_input == system_pkg["EXIT"]: return ("CONDITION_SUCCESS", "取消读取备份文件")
                                    user_input = convert_to_int(user_input)
                                    if user_input != None:
                                        try:
                                            temp_container_list[-1].task_list.append(select_task[user_input][0])
                                            continue # 输入成功
                                        except IndexError:
                                            pass
                                    system_pkg["system_msg"](f"索引\"{user_input}\"不存在")
                                    return ("CONDITION_SUCCESS", "输入备份文件task类型索引错误")
                                else: # 若只有一项可选
                                    temp_container_list[-1].task_list.append(select_task[0][0])
                        continue # 若为extra类型则跳过以上判断
                    else:
                        report_error(txt_list, current_container_index, current_task_index, f"容器版本\"{build_list[0]}\"不可用", system_pkg)
                        return (system_pkg["CONDITION_FAIL"], "读取备份文件错误")
                except KeyError:
                    report_error(txt_list, current_container_index, current_task_index, f"容器类型\"{build_list[0]}\"不存在", system_pkg)
                    return (system_pkg["CONDITION_FAIL"], "读取备份文件错误")
        # 输出比较信息
        # garbage_task_count
        # 总container数
        # 总task数
        old_container_count = len(container_list)
        new_container_count = len(temp_container_list)
        old_total_task = 0
        for i in container_list:
            old_total_task += len(i.task_list)
        new_total_task = 0
        for i in temp_container_list:
            new_total_task += len(i.task_list)
        # 容器数量变动
        container_count_change = new_container_count - old_container_count
        if container_count_change == 0: container_count_change = f"（相同）"
        elif container_count_change > 0: container_count_change = f"（+{container_count_change}）"
        else: container_count_change = f"（{container_count_change}）"
        # task数量变动
        total_task_change = new_total_task - old_total_task
        if total_task_change == 0: total_task_change = f"（相同）"
        elif total_task_change > 0: total_task_change = f"（+{total_task_change}）"
        else: total_task_change = f"（{total_task_change}）"
        table_list = [["", "导入前", "导入后"],
                      ["container数", str(old_container_count), f"{str(new_container_count)}{container_count_change}"],
                      ["task数", str(old_total_task), f"{str(new_total_task)}{total_task_change}"]]
        system_pkg["table_msg"](table_list, heading = True)
        if container_count_change == 0 or total_task_change == 0:
            system_pkg["system_msg"]("请检查备份文件，拒绝rm -rf")
            return (system_pkg["CONDITION_SUCCESS"], "备份文件异常")
        user_input = system_pkg["normal_input"]("确认导入(y/n)")
        if user_input != "y": return (system_pkg["CONDITION_SUCCESS"], "取消导入备份文件")
        container_list[:] = temp_container_list
        system_pkg["system_msg"](f"已导入{file_path}")
        return (system_pkg["CONDITION_SUCCESS"], None)