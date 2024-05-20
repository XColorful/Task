from default_class_func import default_tasker_func_template
from .function import YYYY_MM_DD
import matplotlib.pyplot as plt
import numpy as np
from pylab import mpl
mpl.rcParams["font.sans-serif"] = ["Microsoft YaHei"]

# 封装函数--------+--------+--------+--------+--------+--------+--------+--------+ Begin
def table_categorize_task_result(labels:list, y:list, system_pkg:dict):
    """labels -> 第1列, y -> 第二列
    
    """
    length = len(labels)
    if length != len(y):
        system_pkg["error_msg"]("传入table_categorize_task_result的两个列表长度不一致")
        return None
    table_list = []
    heading = ["标签（x轴）", "数量（y轴）"]
    table_list.append(heading)
    for i in range(0, length):
        table_list.append([labels[i], str(y[i])])
    system_pkg["table_msg"](table_list, heading = True)
# 封装函数--------+--------+--------+--------+--------+--------+--------+--------+ End


class categorize_task(default_tasker_func_template):
    def __init__(self):
        super().__init__()  # 继承父类
        self.label = "categorize_task"
        self.version = "1.0"
        self.function_list = ["categorize"]
        # 供调试时查看信息用，不可见
        self.create_date = YYYY_MM_DD()
    
    def __str__(self):
        return super().__str__()
    
    def get_info(self):
        return super().get_info()

    def proceed(self, cmd_list:list, tasker, system_pkg:dict):
        return super().proceed(cmd_list, tasker, system_pkg)
    
    def categorize(self, cmd_parameter:str, tasker, system_pkg:dict):
        """可选参数attr, date
        
        """
        user_input = cmd_parameter
        if user_input == "":
            system_pkg["tips_msg"]("可选参数[\"date\", \"attr\"]")
            user_input = system_pkg["normal_input"]("输入分类")
        if user_input == system_pkg["EXIT"]: return None
        
        if user_input == "attr":
            self.attr_count(tasker, system_pkg)
        elif user_input == "date":
            self.date_count(tasker, system_pkg)
        else:
            system_pkg["system_msg"](f"参数\"{user_input}\"不存在")
        return None
    
    def attr_count(self, tasker, system_pkg:dict):
        attr_category = [] # [ ["attr1", 12] , ["attr2", 12], ]
        if tasker.task_list == []:
            system_pkg["system_msg"]("Taskertask_list为空")
            return None
        for task in tasker.task_list:
            task_attr = task.attribute
            if task_attr == "": task_attr = "None"
            find = False
            for index, pair in enumerate(attr_category):
                if task_attr == pair[0]:
                    attr_category[index][1] += 1
                    find = True
                    break
            if find == False:
                attr_category.append([task_attr, 1])
        # 按从大到小排序
        attr_category = sorted(attr_category, key=lambda x: x[1], reverse = True)
        labels = []
        y = []
        iterator = range(len(attr_category))
        max_num_index = max(iterator, key = lambda index: attr_category[index][1])
        attr_explode = [0.1 if i == max_num_index else 0 for i in iterator]
        for pair in attr_category:
            labels.append(pair[0])
            y.append(pair[1])
        attr_y = np.array(y)
        attr_labels = np.array(labels)
        # 表1：pie
        plt.subplot(1, 2, 1)
        plt.pie(attr_y, labels = labels, explode = attr_explode, shadow = True)
        plt.legend(labels)
        plt.title(f"\"{tasker.tasker_label}\"各task占比")
        # 表2：
        plt.subplot(1, 2, 2)
        plt.bar(attr_labels, attr_y)
        plt.grid(axis = "y", linestyle = "--", linewidth = 0.5)
        # 展示
        table_categorize_task_result(labels, y, system_pkg)
        plt.show()
        return None
    
    def date_count(self, tasker, system_pkg:dict):
        date_category = [] # [ ["2023_09", 12], ["2024_03", 15] ]
        if tasker.task_list == []:
            system_pkg["system_msg"]("Taskertask_list为空")
            return None
        for task in tasker.task_list:
            task_date = task.date[:7]
            if task_date == "": task_date = "None"
            find = False
            for index, pair in enumerate(date_category):
                if task_date == pair[0]:
                    date_category[index][1] += 1
                    find = True
                    break
            if find == False:
                date_category.append([task_date, 1])
        # 按月份排序
        date_category = sorted(date_category, key = lambda x: x[0])
        labels = []
        y= []
        iterator = range(len(date_category))
        max_num_index = max(iterator, key = lambda index: date_category[index][1])
        date_explode = [0.1 if i == max_num_index else 0 for i in iterator]
        for pair in date_category:
            labels.append(pair[0])
            y.append(pair[1])
        date_x = np.array(labels)
        date_y = np.array(y)
        # 表1：pie
        plt.subplot(1, 2, 1)
        plt.pie(date_y, labels = labels, autopct='%1.1f%%', explode = date_explode, shadow = True)
        plt.legend(labels)
        title = f"\"{str(tasker.tasker_label)}\"各月task占比"
        plt.title(title)
        # 表2：
        plt.subplot(1, 2, 2)
        plt.bar(date_x, date_y)
        plt.grid(axis = "y", linestyle = "--", linewidth = 0.5)
        # 展示
        table_categorize_task_result(labels, y, system_pkg)
        plt.show()
        return None