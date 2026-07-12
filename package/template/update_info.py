from .function import YYYY_MM_DD

def df_update_info(self, system_pkg) -> tuple:
    self.create_date = YYYY_MM_DD()
    return (system_pkg["CONDITION_SUCCESS"], "更新Tasker信息")

def ex_update_info(self, system_pkg) -> tuple:
    self.create_date = YYYY_MM_DD()
    return (system_pkg["CONDITION_SUCCESS"], "更新Tasker信息")