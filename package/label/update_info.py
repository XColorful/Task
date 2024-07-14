from .function import YYYY_MM_DD

def label_update_info(self, system_pkg) -> tuple:
    self.create_date = YYYY_MM_DD()
    return (system_pkg["CONDITION_SUCCESS"], "更新Tasker信息")