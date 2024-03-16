from default_method import default_method_template
from .function import YYYY_MM_DD

class school_task_method(default_method_template):
    def __init__(self):
        super().__init__() # 继承父类
        self.label = "school_task_method"
        self.version = "1.0"
        self.method_list = ["today", "txt1", "backup1", "reload1"]
    
    def method_info(self):
        return super().method_info()
    
    def analyze(self, cmd_list:list, container_list:list, system_pkg:dict): # 分析是否存在可用指令，返回(bool，[标签，版本，类型])
        return super().analyze(cmd_list, container_list, system_pkg)

    def proceed(self, cmd_list:list, container_list:list, system_pkg:dict):
        return super().proceed(cmd_list, container_list, system_pkg)
   
    def today(self, cmd_list:list, container_list:list, system_pkg:dict):
        current_date = YYYY_MM_DD()
        user_input = system_pkg["normal_input"](f"输入时间({current_date})")
        if user_input != "": current_date = user_input
        
        with open(".\\today.txt", "w", encoding = "utf-8") as f:
            # 写container
            for container in container_list:
                write_list = []
                write = False
                write_list.append(f"{container.container_label}:\n")
                # 写task
                for task in container.task_list:
                    if task.date == current_date:
                        write = True
                        comment = task.comment
                        if comment != "":
                            comment = "|" + comment
                        write_list.append(f"\t{task.date}|<{task.attribute}>|{task.content}{comment}\n")
                if write == True:
                    for i in write_list:
                        f.write(i)
        system_pkg["system_msg"]("已生成Task1.2 today.txt")
        return (system_pkg["CONDITION_SUCCESS"], "today")
    
    def txt1(self, cmd_list:list, container_list:list, system_pkg:dict):
        with open(".\\task1.txt", "w", encoding = "utf-8") as f:
            for container in container_list:
                f.write(f"{container.container_label} ({container.create_date} - {container.create_date})\n")
                for task in container.task_list:
                    comment = task.comment
                    if comment != "":
                        comment = "|" + comment
                    f.write(f"\t{task.date}|<{task.attribute}>|{task.content}{comment}\n")
        system_pkg["system_msg"]("已创建Task1.2 txt1.txt")
        return (system_pkg["CONDITION_SUCCESS"], "txt1")
    
    def backup1(self, cmd_list:list, container_list:list, system_pkg:dict):
        system_pkg("system_msg")("注意：此功能为适配早期版本创建，请使用默认模块\"backup\"命令代替")
        if system_pkg("normal_input")("继续执行(y/n)") != "y": return (system_pkg["CONDITION_SUCCESS"], "取消backup1")
        with open(".\\backup1.txt", "w", encoding = "utf-8") as f:
            for container in container_list:
                f.write(f"Task_object|{container.container_label}|{container.create_date}|{container.description}\n")
                for task in container.task_list:
                    f.write(f"Task|{task.date}|{task.attribute}|{task.content}|{task.comment}|{task.create_date}\n")
        system_pkg["system_msg"]("已生成Task1.2 backup1.txt")
        return (system_pkg["CONDITION_SUCCESS"], "backup1")
    
    def reload1(self, cmd_list:list, container_list:list, system_pkg:dict):
        system_pkg("system_msg")("注意：此功能为适配早期版本创建，请使用默认模块\"backup\"命令及\"reload\"代替")
        system_pkg("system_msg")("注意：此方法将不保留task创建日期更变，所有extra类型数据")
        if system_pkg("normal_input")("继续执行(y/n)") != "y": return (system_pkg["CONDITION_SUCCESS"], "取消reload1")
        temp_container_list = []
        
        with open(".\\backup1.txt", "r", encoding = "utf-8") as f:
            temp_container_template = system_pkg["df_container_template_list"][0]
            temp_task_template = system_pkg["df_task_template_list"][0]
            txt_list = f.readlines()
            container_index = -1
            for txt_line in txt_list:
                item_list = txt_line.rstrip("\n").split("|")
                if item_list[0] == "Task_object":
                    container_index += 1
                    temp_container = temp_container_template()
                    temp_container.task_template.append(system_pkg["df_task_template_list"][0])
                    temp_container.container_label, temp_container.create_date, temp_container.description = item_list[1:4]
                    temp_container_list.append(temp_container)
                elif item_list[0] == "Task":
                    temp_task = temp_task_template()
                    info_dict = {"date":item_list[1],
                                 "attribute":item_list[2],
                                 "content":item_list[3],
                                 "comment":item_list[4],
                                 "create_date":item_list[5]}
                    temp_task.update(info_dict)
                    temp_container_list[container_index].task_list.append(temp_task)
            user_input = system_pkg["normal_input"]("Confirm<Enter>:")
            if user_input == "":
                container_list[:] = temp_container_list
                system_pkg["system_msg"]("reload success")
        return (system_pkg["CONDITION_SUCCESS"], "reload1")