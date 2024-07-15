def df_interface_template(tasker, system_pkg):
    system_pkg["normal_msg"]("test:df_interface_template")
    system_pkg["body_msg"]([f"tasker.tasker_label:{tasker.tasker_label}"])
    return (system_pkg["CONDITION_SUCCESS"], f"{tasker.tasker_label}.interface界面")

def ex_interface_template(tasker, system_pkg):
    system_pkg["normal_msg"]("test:ex_interface_template")
    system_pkg["body_msg"]([f"tasker.tasker_label:{tasker.tasker_label}"])
    return (system_pkg["CONDITION_SUCCESS"], f"{tasker.tasker_label}.interface界面")