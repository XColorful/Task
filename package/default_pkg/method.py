from default_method import default_method_template
from .function import convert_to_int, convert_to_float, table_container_list, table_container_template, YYYY_MM_DD_HH_MM_SS, table_backup_file
from os import mkdir, getcwd
from os.path import exists, join, dirname, abspath
from glob import glob

class default_method(default_method_template):
    def __init__(self):
        super().__init__() # 继承父类
        self.label = "default_method"
        self.version = "1.0"
        self.method_list = ["get", "add", "delete", "edit"]
    
    def method_info(self):
        return super().method_info()
    
    def analyze(self, cmd_list:list, container_list:list, system_pkg:dict): # 分析是否存在可用指令，返回(bool，[标签，版本，类型])
        return super().analyze(cmd_list, container_list, system_pkg)

    def proceed(self, cmd_list:list, container_list:list, system_pkg:dict):
        return super().proceed(cmd_list, container_list, system_pkg)
    
    def get(self, cmd_parameter:str, container_list:list, system_pkg:dict): # 获取container列表，进入container.interface()
        # 检测空container_list
        MAX_INDEX = len(container_list) - 1
        if MAX_INDEX == -1:
            system_pkg["system_msg"]("container_list为空，请先用指令\"add\"创建一个container")
            return (system_pkg["CONDITION_SUCCESS"], "container_list为空")
        # 有参数则跳过首次获取user_input
        user_input = ""
        if cmd_parameter != "":
            user_input = cmd_parameter
        else: # 展示container_list
            table_container_list(range(0, MAX_INDEX +1), container_list, system_pkg)
        # 获取container_list索引值
        get_index = "" # 用于get的索引
        while get_index == "":
            # 获取user_input
            if user_input == "":
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
            # 重置user_input
            user_input = ""
        # 进入container.instance()界面
        return_tuple = container_list[get_index].interface(system_pkg) # 进入container.interface()并提供system_pkg
        return return_tuple
    
    def add(self, cmd_parameter:str, container_list:list, system_pkg:dict): # 添加container
        df_container_template_list = system_pkg["df_container_template_list"]
        ex_container_template_list = system_pkg["ex_container_template_list"]
        container_template_list = df_container_template_list + ex_container_template_list
        if container_template_list == []:
            system_pkg["system_msg"]("没有可用的container模板")
            return (system_pkg["CONDITION_SUCCESS"], "无container模板")
        # 选定container_template
        if cmd_parameter != "": # 用参数预输入
            user_input = cmd_parameter
        else: # 无参数预输入
            # 展示container_template
            container_show_list = table_container_template(container_template_list, system_pkg)
            system_pkg["tips_msg"]("匹配首个符合的模板，输入\"exit\"取消创建")
            user_input = system_pkg["normal_input"]("输入索引或版本")
        if user_input == system_pkg["EXIT"]: return (system_pkg["CONDITION_SUCCESS"], "取消添加container模板")
        convert_result = convert_to_int(user_input)
        # 尝试识别为索引
        container_template_list_index = None
        if convert_result != None:
            MAX_INDEX = len(container_template_list) - 1
            if 0 <= convert_result <= MAX_INDEX:
                container_template_list_index = convert_result
            else:
                system_pkg["system_msg"](f"索引值{user_input}超出范围（0 ~ {MAX_INDEX}）")
                return (system_pkg["CONDITION_SUCCESS"], f"索引值{user_input}超出范围（0 ~ {MAX_INDEX}）")
        # 尝试识别为字符串
        if container_template_list_index == None:
            for index, container_version in enumerate(container_show_list):
                if user_input in container_version:
                    container_template_list_index = index
                    break
        if container_template_list_index == None: return (system_pkg["CONDITION_SUCCESS"], f"无容器添加结果")
        # 创建container实例
        container_instance = container_template_list[container_template_list_index]()
        container_list.append(container_instance)
        # 确认是否立即更新信息
        user_input = system_pkg["normal_input"]("是否立即补充容器信息(y/n)")
        if user_input != "y": return (system_pkg["CONDITION_SUCCESS"], "不补充容器信息")
        container_list[-1].update_info(system_pkg); return (system_pkg["CONDITION_SUCCESS"], "立即补充容器信息")
    
    def delete(self, cmd_parameter:str, container_list:list, system_pkg:dict): # 删除container，尝试创建备份文件
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
            if cmd_parameter != "": # 有参数则跳过首次获取user_input
                user_input = cmd_parameter
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
    
    def edit(self, cmd_parameter:str, container_list:list, system_pkg:dict): # 编辑container信息，单独编辑，使用container内置函数
        # 更改container_label, description, create_date
        return (system_pkg["CONDITION_SUCCESS"], None)


class default_txt_operation(default_method_template):
    def __init__(self):
        super().__init__() # 继承父类
        self.label = "default_txt_operation"
        self.version = "1.0"
        self.method_list = ["backup", "reload"]
    
    def method_info(self):
        return super().method_info()
    
    def analyze(self, cmd_list:list, container_list:list, system_pkg:dict): # 分析是否存在可用指令，返回(bool，[标签，版本，类型])
        return super().analyze(cmd_list, container_list, system_pkg)

    def proceed(self, cmd_list:list, container_list:list, system_pkg:dict):
        return super().proceed(cmd_list, container_list, system_pkg)
    
    def backup(self, cmd_parameter:str, container_list:list, system_pkg:dict): # 备份container，全局备份
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
            # 写入task行
            for task in container.task_list:
                build_list = task.backup_list()
                if build_list == False: # task内部定义的读取异常（不是抛出exception）
                    system_pkg["system_msg"]("获取task备份列表失败")
                    return (system_pkg["CONDITION_SUCCESS"], "获取backup_list失败")
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
    
    def reload(self, cmd_parameter:str, container_list:list, system_pkg:dict): # 从.\\backup\\的txt文件读取container及其task_list，显示备份文件中不可用的模板，统计所有出现的类型及数量
        """参数第一个字符为"u"则自动升级可用版本，参数第一个字符为"n"则取消升级"""
        AUTO_UPDATE_VERSION = False
        try:
            if cmd_parameter[0] == "u":
                AUTO_UPDATE_VERSION = True
            elif cmd_parameter[0] == "n":
                AUTO_UPDATE_VERSION = None
        except IndexError: AUTO_UPDATE_VERSION = False
        
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
        
        # 检测可用的备份txt文件
        backup_dir = ".\\backup_all\\"
        file_list = glob(join((backup_dir), "backup_*.txt"))
        file_list.sort()
        if file_list == []:
            system_pkg["system_msg"]("无可导入的备份文件")
            return (system_pkg["CONDITION_SUCCESS"], "无可导入的备份文件")
        # 显示当前工作路径
        working_dir = getcwd()
        system_pkg["system_msg"](f"当前工作路径{working_dir}")
        # 显示txt文件列表
        display_list = file_list[:]
        display_list[-1] = display_list[-1] + "（默认）"
        table_backup_file(display_list, system_pkg)
        # 选中备份文件
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
        # 读取txt文件
        with open(file_path, "r", encoding = "utf-8") as f:
            txt_list = f.readlines()
        current_container_index = 0
        current_task_index = 0
        temp_container_list = []
        total_garbage_task = 0 # 用于统计无归属container的task
        for index, txt_line in enumerate(txt_list):
            txt_line = txt_line[:-1] # 去除最右的\n
            if txt_line == "/end": break
            elif txt_line == "":
                continue
            # 开始检测
            
            # 创建container--------+--------+--------+--------+--------+--------+--------+ Begin
            if txt_line[0] != "\t":
                current_container_index = index
                current_task_index = index
                build_list = txt_line.split("||||")
                # 长度至少为以下形式，拓展部分在container内部处理
                # [self.type, self.version, self.container_label, self.create_date, function_list, task_template_list, self.description]
                # 尝试创建container
                try:
                    is_default_type = (build_list[0] == system_pkg["TYPE_DEFAULT_CONTAINER"])
                    if is_default_type == True: # container为默认类型
                        read_version = convert_to_float(build_list[1])
                        if read_version == None: # container版本格式不符
                            report_error(txt_list, current_container_index, current_task_index, f"容器版本\"{build_list[0]}\"错误", system_pkg)
                            return (system_pkg["CONDITION_FAIL"], "读取备份文件错误")
                    find_container = False
                    select_container = []
                    # 遍历可用的container模板
                    iterator = system_pkg["df_container_template_list"]
                    # 选择遍历默认模板或extra模板
                    if is_default_type == False: iterator = system_pkg["ex_container_template_list"]
                    # 开始遍历
                    for container_template in iterator:
                        container = container_template()
                        if is_default_type:
                            # container为default类型
                            if read_version <= convert_to_float(container.version):
                                # 建立container
                                build_condition = container.build(build_list, system_pkg)
                                if build_condition == False: # container内部定义的读取失败
                                    system_pkg["system_msg"]("容器建立失败")
                                    return (system_pkg["CONDITION_SUCCESS"], "container.build失败")
                                # 添加到temp_container_list
                                select_container.append([container, container.version])
                                find_container = True
                        else:
                            # container为extra类型
                            if build_list[1] == container.version:
                                # 建立container
                                build_condition = container.build(build_list, system_pkg)
                                if build_condition == False: # container内部定义的读取失败
                                    system_pkg["system_msg"]("容器建立失败")
                                    return (system_pkg["CONDITION_SUCCESS"], "container.build失败")
                                # 添加到temp_container_list
                                find_container = True
                                temp_container_list.append(container)
                                break
                    if find_container == True:
                        # container匹配已有模板
                        
                        # 版本选择--------+--------+--------+--------+--------+--------+ Begin
                        if is_default_type == True: # extra类型不需要在此选择版本
                            select_container.sort(key = lambda x: x[0])
                            if AUTO_UPDATE_VERSION == None: temp_container_list.append(select_container[-1][0])
                            elif AUTO_UPDATE_VERSION == True: temp_container_list.append(select_container[-1][0])
                            elif AUTO_UPDATE_VERSION == False:
                                # 有多个版本选择
                                if len(select_container) != 1:
                                    # 显示不同container版本
                                    compare_selection(select_container, system_pkg, "容器")
                                    user_input = system_pkg["normal_input"]("输入索引")
                                    if user_input == system_pkg["EXIT"]: return ("CONDITION_SUCCESS", "取消读取备份文件")
                                    user_input = convert_to_int(user_input)
                                    if user_input != None:
                                        try:
                                            temp_container_list.append(select_container[user_input][0])
                                            continue # 输入成功，添加container
                                        except IndexError: pass # 输入失败，取消reload
                                    system_pkg["system_msg"](f"索引\"{user_input}\"不存在")
                                    return ("CONDITION_SUCCESS", "输入备份文件容器类型索引错误")
                                # 只有一个版本选择
                                else: temp_container_list.append(select_container[0][0])
                        continue # 若为extra类型则跳过以上判断
                        # 版本选择--------+--------+--------+--------+--------+--------+ End
                        
                    else:
                        # container不匹配已有模板
                        report_error(txt_list, current_container_index, current_task_index, f"容器版本\"{build_list[0]}\"不可用", system_pkg)
                        return (system_pkg["CONDITION_FAIL"], "读取备份文件错误")
                except KeyError:
                    report_error(txt_list, current_container_index, current_task_index, f"容器类型\"{build_list[0]}\"不存在", system_pkg)
                    return (system_pkg["CONDITION_FAIL"], "读取备份文件错误")
            # 创建container--------+--------+--------+--------+--------+--------+--------+ End
            
            # 创建task--------+--------+--------+--------+--------+--------+--------+ Begin
            else: # 行开头为"\t"
                # 如果前面没有读取container
                if len(temp_container_list) == 0:
                    total_garbage_task += 1
                    continue
                current_task_index = index
                txt_line = txt_line[1:]
                build_list = txt_line.split("||||")
                # 长度至少为以下形式，拓展部分在task内部处理
                # [self.type, self.version, self.create_date, self.date, self.attribute, self.content, self.comment]
                try:
                    is_default_type =  build_list[0] == system_pkg["TYPE_DEFAULT_CONTAINER"]
                    if is_default_type == True: # task为默认类
                        read_version = convert_to_float(build_list[1])
                        if read_version == None: # task版本格式不符
                            report_error(txt_list, current_container_index, current_task_index, f"task版本\"{build_list[0]}\"错误", system_pkg)
                            return (system_pkg["CONDITION_FAIL"], "读取备份文件错误")
                    find_task = False
                    select_task = []
                    # 遍历可用的task模板
                    iterator = system_pkg["df_task_template_list"]
                    # 选择遍历默认模板或extra模板
                    if is_default_type == False: iterator = system_pkg["ex_task_template_list"]
                    # 开始遍历
                    for task_template in iterator:
                        task = task_template()
                        if is_default_type:
                            # task为default类型
                            if read_version <= convert_to_float(task.version):
                                # 建立task
                                build_condition = task.build(build_list) # task的build不需要system_pkg
                                if build_condition == False: # task内部定义的读取失败
                                    system_pkg["system_msg"]("task建立失败")
                                    return (system_pkg["CONDITION_SUCCESS"], "task.build失败")
                                # 添加到container
                                select_task.append([task, task.version])
                                find_task = True
                        else:
                            # task为extra类型
                            if build_list[1] == task.version:
                                # 建立task
                                build_condition = task.build(build_list) # task的build不需要system_pkg
                                if build_condition == False: # task内部定义的读取失败
                                    system_pkg["system_msg"]("task建立失败")
                                    return (system_pkg["CONDITION_SUCCESS"], "task.build失败")
                                # 添加到container
                                find_task = True
                                temp_container_list[-1].task_list.append(task)
                                break
                    if find_task == True:
                        # task匹配已有模板
                        
                        # 版本选择--------+--------+--------+--------+--------+--------+ Begin
                        if is_default_type == True: # extra类型不需要在此选择版本
                            select_task.sort(key = lambda x: x[0])
                            if AUTO_UPDATE_VERSION == None: temp_container_list[-1].task_list.append(select_task[-1][0])
                            elif AUTO_UPDATE_VERSION == True: temp_container_list[-1].task_list.append(select_task[-1][0])
                            elif AUTO_UPDATE_VERSION == False:
                                # 有多个版本选择
                                if len(select_task) != 1:
                                    # 显示不同task版本
                                    compare_selection(select_task, system_pkg, "task")
                                    user_input = system_pkg["normal_input"]("输入索引")
                                    if user_input == system_pkg["EXIT"]: return ("CONDITION_SUCCESS", "取消读取备份文件")
                                    user_input = convert_to_int(user_input)
                                    if user_input != None:
                                        try:
                                            temp_container_list[-1].task_list.append(select_task[user_input][0])
                                            continue # 输入成功，添加task
                                        except IndexError: pass # 输入失败，取消reload
                                    system_pkg["system_msg"](f"索引\"{user_input}\"不存在")
                                    return ("CONDITION_SUCCESS", "输入备份文件task类型索引错误")
                                # 只有一个版本选择
                                else:
                                    temp_container_list[-1].task_list.append(select_task[0][0])
                        continue # 若为extra类型则跳过以上判断
                        # 版本选择--------+--------+--------+--------+--------+--------+ End
                        
                    else:
                        # task不匹配已有模板
                        report_error(txt_list, current_container_index, current_task_index, f"容器版本\"{build_list[0]}\"不可用", system_pkg)
                        return (system_pkg["CONDITION_FAIL"], "读取备份文件错误")
                except KeyError:
                    report_error(txt_list, current_container_index, current_task_index, f"容器类型\"{build_list[0]}\"不存在", system_pkg)
                    return (system_pkg["CONDITION_FAIL"], "读取备份文件错误")
            # 创建task--------+--------+--------+--------+--------+--------+--------+ End
            
        total_old_container = len(container_list)
        total_new_container = len(temp_container_list)
        total_old_task = 0
        for i in container_list:
            total_old_task += len(i.task_list)
        total_new_task = 0
        for i in temp_container_list:
            total_new_task += len(i.task_list)
        # 统计container数量变动
        total_container_change = total_new_container - total_old_container
        if total_container_change == 0:
            container_change = f"（相同）"
        elif total_container_change > 0:
            container_change = f"（+{total_container_change}）"
        else:
            container_change = f"（{total_container_change}）"
        # 统计task数量变动
        total_task_change = total_new_task - total_old_task
        if total_task_change == 0:
            task_change = f"（相同）"
        elif total_task_change > 0:
            task_change = f"（+{total_task_change}）"
        else:
            task_change = f"（{total_task_change}）"
        # 显示比较信息
        table_list = [["", "导入前", "导入后"],
                      ["container数", str(total_old_container), f"{str(total_new_container)}{container_change}"],
                      ["task数", str(total_old_task), f"{str(total_new_task)}{task_change}"]]
        system_pkg["table_msg"](table_list, heading = True)
        # 显示将被丢弃的task数量（放置于backup文件的顺序错误，可能是人为导致）
        if total_garbage_task != 0:
            system_pkg["system_msg"](f"注：备份文件中含有{total_garbage_task}项task被丢弃")
        # 空备份文件检测，可能不包含可读取内容
        if total_new_container == 0 or total_new_task == 0:
            system_pkg["system_msg"]("请检查备份文件，防止\"rm -rf\"（此操作将清空所有内容）")
            return (system_pkg["CONDITION_SUCCESS"], "备份文件为空，拒绝reload")
        # 读取确认（覆盖原数据）
        user_input = system_pkg["normal_input"]("确认导入(y/n)")
        if user_input != "y": return (system_pkg["CONDITION_SUCCESS"], "取消导入备份文件")
        container_list[:] = temp_container_list
        system_pkg["system_msg"](f"已导入{file_path}")
        return (system_pkg["CONDITION_SUCCESS"], None)


class default_sys_method(default_method_template):
    def __init__(self):
        super().__init__() # 继承父类
        self.label = "default_sys_method"
        self.version = "1.0"
        self.method_list = ["sys_info"]
    
    def method_info(self):
        return super().method_info()
    
    def analyze(self, cmd_list:list, container_list:list, system_pkg:dict): # 分析是否存在可用指令，返回(bool，[标签，版本，类型])
        return super().analyze(cmd_list, container_list, system_pkg)

    def proceed(self, cmd_list:list, container_list:list, system_pkg:dict):
        return super().proceed(cmd_list, container_list, system_pkg)
    
    def sys_info(self, cmd_parameter:str, container_list:list, system_pkg:dict):
        """获取system_pkg信息"""
        if cmd_parameter != "":
            user_input = cmd_parameter
        else:
            user_input = system_pkg["normal_input"]("输入查询的信息")
        if user_input == system_pkg["EXIT"]: return (system_pkg["CONDITION_SUCCESS"], "取消查询system_pkg")
        try:
            system_pkg["normal_msg"](system_pkg[user_input])
            return (system_pkg["CONDITION_SUCCESS"], f"查询system_pkg\"{user_input}\"")
        except KeyError:
            system_pkg["system_msg"](f"system_pkg中不包含\"{user_input}\"")
            return (system_pkg["CONDITION_SUCCESS"], f"system_pkg\"{user_input}\"查询结果不存在")