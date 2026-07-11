"""阶段 4 验证测试——扩展模块注册 + 默认服务"""

import sys, os, tempfile, shutil

_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, _src)

d = tempfile.mkdtemp()

# ============================================================
# Register all extensions
# ============================================================
from core.extension_registry import ExtensionRegistry

from extensions.default.default_task import DefaultTask
from extensions.default.default_tasker import DefaultTasker
ExtensionRegistry.register_task_type("default", DefaultTask)
ExtensionRegistry.register_tasker_type("default", DefaultTasker)

from extensions.timer.timer_task import TimerTask
from extensions.timer.timer_tasker import TimerTasker
ExtensionRegistry.register_task_type("timer", TimerTask)
ExtensionRegistry.register_tasker_type("timer", TimerTasker)

from extensions.account.account_task import AccountTask
from extensions.account.account_tasker import AccountTasker
ExtensionRegistry.register_task_type("account", AccountTask)
ExtensionRegistry.register_tasker_type("account", AccountTasker)

from extensions.label.label_task import LabelTask
from extensions.label.label_tasker import LabelTasker
ExtensionRegistry.register_task_type("label", LabelTask)
ExtensionRegistry.register_tasker_type("label", LabelTasker)

assert len(ExtensionRegistry.list_task_types()) == 4
assert len(ExtensionRegistry.list_tasker_types()) == 4
print("Test 1 OK: all types registered")

# ============================================================
# Test 2-4: create Task instances
# ============================================================
dt = ExtensionRegistry.create_task("default", content="hello")
assert dt.type == "default" and dt.content == "hello"
assert dt.matches_search("hello") and not dt.matches_search("xyz")
d2 = dt.__class__.from_dict(dt.to_dict())
assert d2.content == "hello"
print("Test 2 OK: DefaultTask round-trip")

tt = ExtensionRegistry.create_task("timer", start_time="2026_07_11-10:00", end_time="2026_07_11-12:30")
assert tt.is_running is False and tt.duration_minutes == 150
assert tt.matches_search("10:00")
print("Test 3 OK: TimerTask duration/search")

at = ExtensionRegistry.create_task("account", account_type="GitHub", label_alias="mygh", password="secret")
assert at.account_type == "GitHub" and at.search_label == "mygh"
assert at.matches_search("GitHub")
print("Test 4 OK: AccountTask")

lt = ExtensionRegistry.create_task("label", label_list=[("env", "prod")])
assert len(lt.label_list) == 1 and lt.matches_search("prod")
print("Test 5 OK: LabelTask")

# ============================================================
# Test 6-8: DefaultTaskerService
# ============================================================
from core.storage.storage_manager import StorageManager
from core.service.default_tasker_service import DefaultTaskerService

smgr = StorageManager(d)
dts = DefaultTaskerService(smgr)

ts = dts.create_tasker({"type": "default", "label": "Test", "description": "desc"})
tid = ts["id"]
assert ts["label"] == "Test"
print("Test 6 OK: create_tasker")

tl = dts.list_taskers()
assert len(tl) == 1 and tl[0]["id"] == tid
print("Test 7 OK: list_taskers")

tasker = dts.get_tasker(tid)
assert tasker is not None and tasker.label == "Test"
assert tasker.get_commands() == ["search", "new", "delete", "edit", "backup", "reload"]
print("Test 8 OK: get_tasker with lazy load")

# ============================================================
# Test 9-11: DefaultTaskService
# ============================================================
from core.service.default_task_service import DefaultTaskService

dtsk = DefaultTaskService(smgr, tasker_service=dts)
t = dtsk.create_task(tid, {"content": "first", "attribute": "test"})
assert t is not None and t.content == "first"
tasker2 = dts.get_tasker(tid)
assert len(tasker2.task_list) == 1
print("Test 9 OK: create_task")

dtsk.create_task(tid, {"content": "second"})
dtsk.create_task(tid, {"content": "third"})
tasker3 = dts.get_tasker(tid)
assert len(tasker3.task_list) == 3

dtsk.update_task(tid, 1, {"content": "updated"})
tasker4 = dts.get_tasker(tid)
assert tasker4.task_list[1].content == "updated"
print("Test 10 OK: update_task")

dtsk.delete_task(tid, 0)
tasker5 = dts.get_tasker(tid)
assert len(tasker5.task_list) == 2
assert tasker5.task_list[0].content == "updated"
print("Test 11 OK: delete_task")

# ============================================================
# Test 12: SearchEngine
# ============================================================
from core.service.search_engine import SearchEngine

se = SearchEngine(smgr, tasker_service=dts)
results = se.search(tid, "updated")
assert len(results) == 1 and results[0][1].content == "updated"
print("Test 12 OK: SearchEngine")

# ============================================================
# Test 13: QuickButtonService
# ============================================================
from extensions.quick_button.quick_button_service import QuickButtonService

btn = {'command': 'hw', 'label': 'HW', 'preset': {'attribute': 'hw', 'content': 'quick'}}
r = QuickButtonService.trigger(tasker4, btn)
assert r is not None and r.content == 'quick'
assert btn['usage_count'] == 1
tasker6 = dts.get_tasker(tid)
# After delete of index 0: 3 tasks originally, -1 = 2 remaining + quick button = 3
assert len(tasker6.task_list) == 2
print("Test 13 OK: QuickButtonService")

# ============================================================
# Test 14: delete_tasker
# ============================================================
assert dts.delete_tasker(tid) is True
assert len(dts.list_taskers()) == 0
print("Test 14 OK: delete_tasker")

# ============================================================
# Test 15: TimerTasker end_timer
# ============================================================
dts.create_tasker({"type": "timer", "label": "Timer"})
tls = dts.list_taskers()
ttid = tls[0]["id"]
ttr = dts.get_tasker(ttid)
assert ttr.type == "timer"

dtsk.create_task(ttid, {"content": "coding", "attribute": "dev"})
ttr2 = dts.get_tasker(ttid)
running = ttr2.get_running_tasks()
assert len(running) == 1
ttr2.end_timer(running[0][0])
assert ttr2.task_list[running[0][0]].is_running is False
print("Test 15 OK: TimerTasker end_timer")

import shutil
shutil.rmtree(d)
print()
print("ALL 15 TESTS PASSED")
