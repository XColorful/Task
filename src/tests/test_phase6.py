"""Phase 6 test -- Tasker list + Task table UI components."""

import sys, os, tempfile
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, _src)

# --- Register extension types ---
from core.extension_registry import ExtensionRegistry
from core.input_processor import InputPreprocessor, step_plus_to_search
from extensions.default.default_task import DefaultTask
from extensions.default.default_tasker import DefaultTasker
ExtensionRegistry.register_task_type('default', DefaultTask)
ExtensionRegistry.register_tasker_type('default', DefaultTasker)
InputPreprocessor.clear()
InputPreprocessor.register_step(step_plus_to_search)

# --- App ---
from PySide6.QtWidgets import QApplication
app = QApplication(sys.argv[:1])

# ============================================================
# Test 1: TaskerListWidget
# ============================================================
from ui.tasker.tasker_list_widget import TaskerListWidget
tlw = TaskerListWidget()
taskers = [
    {"id": "a1", "label": "Class", "type": "default", "description": ""},
    {"id": "b2", "label": "Timer", "type": "timer", "description": ""},
]
tlw.refresh(taskers)
assert tlw._list.count() == 2
print("Test 1 OK: TaskerListWidget refresh")

# ============================================================
# Test 2: TaskerEditDialog
# ============================================================
from ui.tasker.tasker_edit_dialog import TaskerEditDialog
dlg = TaskerEditDialog(tasker_data=None, types=["default", "timer"])
dlg._label_edit.setText("NewTasker")
assert dlg.get_data()["label"] == "NewTasker"
print("Test 2 OK: TaskerEditDialog create mode")

# edit mode
dlg2 = TaskerEditDialog(tasker_data={"label": "Old", "description": "desc", "type": "timer"})
assert dlg2.get_data()["type"] == "timer"
assert dlg2._type_combo.isEnabled() is False
print("Test 3 OK: TaskerEditDialog edit mode (type locked)")

# ============================================================
# Test 3: TaskTableModel
# ============================================================
from ui.task.task_table_model import TaskTableModel
model = TaskTableModel()
t1 = DefaultTask(content="first", attribute="test", date="2026_07_11")
t2 = DefaultTask(content="second", attribute="dev")
model.set_tasks([t1, t2])
assert model.rowCount() == 2
assert model.data(model.index(0, 0)) == "0"
assert model.data(model.index(1, 3)) == "second"
print("Test 4 OK: TaskTableModel data access")

# append
t3 = DefaultTask(content="third")
model.append_tasks([t3])
assert model.rowCount() == 3
print("Test 5 OK: TaskTableModel append")

# remove
model.remove_task(0)
assert model.rowCount() == 2
assert model.data(model.index(0, 3)) == "second"
print("Test 6 OK: TaskTableModel remove")

# ============================================================
# Test 4: TaskTableWidget
# ============================================================
from ui.task.task_table_widget import TaskTableWidget
ttw = TaskTableWidget()
ttw.set_tasks([t2, t3])
print("Test 7 OK: TaskTableWidget set_tasks")

# ============================================================
# Test 5: TaskEditPanel
# ============================================================
from ui.task.task_edit_panel import TaskEditPanel
panel = TaskEditPanel()
panel.open_for_create(preset={"attribute": "hw"})
assert panel._attribute.text() == "hw"
panel._content.setText("test content")
panel._submit()
print("Test 8 OK: TaskEditPanel create with preset")

# ============================================================
# Test 6: TaskSearchBar
# ============================================================
from ui.task.task_search_bar import TaskSearchBar
sb = TaskSearchBar()
sb._input.setText("test")
sb.search_requested.emit(sb._input.text())
sb.set_count(5)
print("Test 9 OK: TaskSearchBar search + count")

print()
print("ALL 9 TESTS PASSED")
