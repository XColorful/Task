"""Phase 7 test -- quick button bar widget and editor."""

import sys, os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, _src)

# --- App ---
from PySide6.QtWidgets import QApplication
app = QApplication(sys.argv[:1])

# ============================================================
# Test 1: QuickButtonBarWidget
# ============================================================
from extensions.quick_button.quick_button_bar_widget import QuickButtonBarWidget
bar = QuickButtonBarWidget()

buttons = [
    {"command": "hw", "label": "Homework", "preset": {"attribute": "homework"}, "tasker_label": "Class"},
    {"command": "code", "label": "Coding", "preset": {"attribute": "dev"}, "tasker_label": "Timer"},
]
bar.refresh(buttons, show_tasker_label=True)
# verify children exist
assert bar._layout.count() > 0
print("Test 1 OK: QuickButtonBarWidget refreshed")

# ============================================================
# Test 2: QuickButtonBarWidget without tasker labels
# ============================================================
bar2 = QuickButtonBarWidget()
bar2.refresh(buttons, show_tasker_label=False)
assert bar2._layout.count() > 0
print("Test 2 OK: QuickButtonBarWidget without labels")

# ============================================================
# Test 3: QuickButtonEditor (create)
# ============================================================
from extensions.quick_button.quick_button_editor import QuickButtonEditor
editor = QuickButtonEditor(button_def=None)
editor._command.setText("hw")
editor._label.setText("Homework")
editor._attr.setText("homework")
editor._content.setText("")
editor._use_default_date.setChecked(True)

data = editor.get_data()
assert data["command"] == "hw"
assert data["label"] == "Homework"
assert data["preset"]["attribute"] == "homework"
assert data["preset"]["use_default_date"] is True
print("Test 3 OK: QuickButtonEditor create")

# ============================================================
# Test 4: QuickButtonEditor (edit)
# ============================================================
existing = {
    "command": "old_cmd", "label": "Old Label",
    "preset": {"attribute": "old", "content": "x", "comment": "y", "use_default_date": False}
}
editor2 = QuickButtonEditor(button_def=existing)
assert editor2._command.text() == "old_cmd"
assert editor2._label.text() == "Old Label"
assert editor2._attr.text() == "old"
assert editor2._use_default_date.isChecked() is False
data2 = editor2.get_data()
assert data2["command"] == "old_cmd"
print("Test 4 OK: QuickButtonEditor edit")

# ============================================================
# Test 5: QuickButtonService integration
# ============================================================
from core.extension_registry import ExtensionRegistry
from core.input_processor import InputPreprocessor, step_plus_to_search
ExtensionRegistry._task_types.clear(); ExtensionRegistry._tasker_types.clear()
from extensions.default.default_task import DefaultTask
from extensions.default.default_tasker import DefaultTasker
ExtensionRegistry.register_task_type('default', DefaultTask)
ExtensionRegistry.register_tasker_type('default', DefaultTasker)
InputPreprocessor.clear()
InputPreprocessor.register_step(step_plus_to_search)

from extensions.quick_button.quick_button_service import QuickButtonService
btn = {"command": "test", "label": "Test", "preset": {"attribute": "test", "content": "hello"}}
tasker = DefaultTasker(tasker_id="t1", label="T")
result = QuickButtonService.trigger(tasker, btn)
assert result is not None and result.content == "hello"
assert btn.get("usage_count") == 1
print("Test 5 OK: QuickButtonService trigger + count")

# ============================================================
# Test 6: QuickButton sort
# ============================================================
btns = [
    {"command": "a", "preset": {}, "usage_count": 1},
    {"command": "b", "preset": {}, "usage_count": 5},
    {"command": "c", "preset": {}},
]
sorted_btns = QuickButtonService.sort_by_usage(btns)
assert sorted_btns[0]["command"] == "b"
assert sorted_btns[1]["command"] == "a"
assert sorted_btns[2]["command"] == "c"
print("Test 6 OK: QuickButtonService sort_by_usage")

print()
print("ALL 6 TESTS PASSED")
