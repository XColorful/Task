def convert_to_int(s:str):
    """返回字符串是否能转换为int，不修改原字符串
    
    接收一个普通字符串，转换失败则返回None"""
    try:
        return int(s)
    except ValueError:
        return None

def convert_to_float(s:str):
    """返回字符串是否能转换为float，不修改原字符串
    
    接收一个普通字符串，转换失败则返回None"""
    try:
        return float(s)
    except ValueError:
        return None

def table_container_function_list(iterator, container_list:list, system_pkg:dict):
    """["索引", "创建日期", "标签", "Tasker功能列表"]
    
    """
    table_list = []
    heading = ["索引", "创建日期", "标签", "Tasker功能列表"]
    table_list.append(heading)
    for i in iterator:
        function_list = []
        for j in container_list[i].function_list:
            function_list.append(j.label)
        table_list.append([str(i), 
                        container_list[i].create_date, 
                        container_list[i].container_label, 
                        str(function_list)])
    system_pkg["table_msg"](table_list, heading = True)
    return None

def table_class_func(iterator:list, class_func_list:list, system_pkg:dict):
    """["索引", "标签", "版本", "类型", "func"]
    
    返回使用的class_func, class_func_list Tasker功能列表(二维)"""
    table_list = []
    heading = ["索引", "标签", "版本", "类型", "func"]
    table_list.append(heading)
    class_func_label_list = []
    for i in iterator:
        class_func = class_func_list[i]()
        func_list = class_func.function_list
        table_list.append([str(i),
                          class_func.label,
                          class_func.version,
                          class_func.type,
                          str(func_list)])
        class_func_label_list.append(func_list)
    system_pkg["table_msg"](table_list, heading = True)
    return class_func_label_list

def table_show_container_func(iterator, function_list, system_pkg:dict):
    """["索引", "func标签", "版本", "类型"]
    
    返回所有class_func的标签列表"""
    table_list = []
    heading = ["索引", "func标签", "版本", "类型"]
    table_list.append(heading)
    func_label_list = []
    for index in iterator:
        func = function_list[index]
        table_list.append([str(index),
                          func.label,
                          func.version,
                          func.type])
        func_label_list.append(func.label)
    system_pkg["table_msg"](table_list, heading = True)
    return func_label_list