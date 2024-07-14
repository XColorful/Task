def label_interface(tasker, system_pkg):
    system_pkg["normal_msg"]("test:ex_interface_template")
    system_pkg["body_msg"]([f"tasker.tasker_label:{tasker.tasker_label}"])
    
    system_pkg["system_msg"]("测试前10项task.content")
    for task in tasker.task_list[0:10]:
        system_pkg["normal_msg"](str(task.content))
    system_pkg["system_msg"]("测试后10项task.content")
    for task in tasker.task_list[-10:]:
        system_pkg["normal_msg"](str(task.content))
    return (system_pkg["CONDITION_SUCCESS"], f"{tasker.tasker_label}.interface界面")