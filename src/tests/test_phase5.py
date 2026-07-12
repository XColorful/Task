"""Phase 5 test -- verify GUI code runs with offscreen rendering."""

import sys
import os

# Must set env BEFORE importing PySide6
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, _src)

# Register extension types
from core.extension_registry import ExtensionRegistry
from core.input_processor import InputPreprocessor, step_plus_to_search

ExtensionRegistry._task_types.clear()
ExtensionRegistry._tasker_types.clear()
from extensions.default.default_task import DefaultTask
from extensions.default.default_tasker import DefaultTasker
ExtensionRegistry.register_task_type('default', DefaultTask)
ExtensionRegistry.register_tasker_type('default', DefaultTasker)
InputPreprocessor.clear()
InputPreprocessor.register_step(step_plus_to_search)

# Test imports
from ui.component.styled_button import StyledButton
print('Test 1 OK: StyledButton')
from ui.component.toast_notification import ToastNotification
print('Test 2 OK: ToastNotification')
from ui.component.confirm_dialog import ConfirmDialog
print('Test 3 OK: ConfirmDialog')
from ui.main.main_window import MainWindow
print('Test 4 OK: MainWindow')
from ui.main.system_tray import SystemTray
print('Test 5 OK: SystemTray')
from ui.main.main_controller import MainController
print('Test 6 OK: MainController')

# Create QApplication and test window creation
from PySide6.QtWidgets import QApplication
app = QApplication(sys.argv[:1])

window = MainWindow()
assert window.content_area is not None
assert window.output_area is not None
assert window.input_box is not None
print('Test 7 OK: MainWindow layout built')

tray = SystemTray(window)
assert tray.icon() is not None
print('Test 8 OK: SystemTray created')

controller = MainController(window, tray)
assert controller._state == "main"
print('Test 9 OK: MainController initialized')

assert InputPreprocessor.process('+hello') == 'search hello'
print('Test 10 OK: InputPreprocessor')

window.log("test")
window.log_error("test")
print('Test 11 OK: log output')

window.set_commands(["new", "search", "delete"])
print('Test 12 OK: commands panel')

# Test state machine
controller._on_input("+test")
controller._on_input("settings")
controller._on_input("exit")
controller._on_input("exit")
print('Test 13 OK: input dispatch')

print()
print('ALL 13 TESTS PASSED')
