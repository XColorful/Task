"""Main Controller -- UI state machine with full CRUD, backup, settings."""

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QLabel, QVBoxLayout, QFormLayout, QLineEdit, QCheckBox, QPushButton

from core.input_processor import InputPreprocessor


class MainController(QObject):
    """Manages UI state transitions and delegates input to services."""

    STATE_MAIN = "main"
    STATE_TASKER = "tasker"
    STATE_SETTINGS = "settings"
    STATE_CHART = "chart"

    def __init__(self, window, tray, storage=None):
        super().__init__()
        self._window = window
        self._tray = tray
        self._storage = storage
        self._state = self.STATE_MAIN
        self._current_tasker_id = None
        self._tasker_service = None
        self._task_service = None
        self._search_engine = None
        self._analysis_engine = None
        self._chart_server = None
        self._tasker_list_widget = None
        self._task_table = None
        self._task_edit_panel = None
        self._quick_button_bar = None
        self._settings_widgets = {}

        self._window.input_submitted.connect(self._on_input)
        self._window.window_hidden.connect(self._on_hide)

        self._enter_main()

    # ================================================================
    # State management
    # ================================================================

    def _enter_main(self):
        self._state = self.STATE_MAIN
        self._current_tasker_id = None
        self._window.setWindowTitle("Task")
        cmds = ["get", "add", "delete", "edit", "info", "sort",
                "backup", "reload", "txt", "migrate",
                "settings", "exit"]
        self._window.set_commands(cmds)

        self._clear_content()

        # Tasker list
        from ui.tasker.tasker_list_widget import TaskerListWidget
        self._tasker_list_widget = TaskerListWidget()
        self._tasker_list_widget.tasker_double_clicked.connect(self._enter_tasker)
        self._window.content_area.addWidget(self._tasker_list_widget)
        self._window.content_area.setCurrentWidget(self._tasker_list_widget)

        # Quick buttons from all taskers
        if self._quick_button_bar is None:
            from extensions.quick_button.quick_button_bar_widget import QuickButtonBarWidget
            self._quick_button_bar = QuickButtonBarWidget()
        self._window.set_quick_buttons([])

        self._refresh_tasker_list()
        self._window.log("Task ready.")

    def _refresh_tasker_list(self):
        if self._tasker_service and self._tasker_list_widget:
            taskers = self._tasker_service.list_taskers()
            self._tasker_list_widget.refresh(taskers)
            # Populate quick buttons
            all_buttons = []
            for t in taskers:
                for btn in t.get('quick_buttons', []):
                    btn_copy = dict(btn)
                    btn_copy['tasker_id'] = t['id']
                    btn_copy['tasker_label'] = t['label']
                    all_buttons.append(btn_copy)
            self._window.set_quick_buttons(all_buttons)

    def _enter_tasker(self, tasker_id):
        if not self._tasker_service:
            self._window.log_error("No tasker service available")
            return
        tasker = self._tasker_service.get_tasker(tasker_id)
        if tasker is None:
            self._window.log_error("Failed to load Tasker")
            return

        self._state = self.STATE_TASKER
        self._current_tasker_id = tasker_id
        self._window.setWindowTitle(f"Task - {tasker.label}")
        cmds = tasker.get_commands()
        self._window.set_commands(cmds)

        self._clear_content()

        # Task table
        from ui.task.task_table_widget import TaskTableWidget
        self._task_table = TaskTableWidget()
        self._task_table.set_tasks(tasker.task_list)
        self._window.content_area.addWidget(self._task_table)
        self._window.content_area.setCurrentWidget(self._task_table)

        # Quick buttons for this tasker
        taskers = self._tasker_service.list_taskers()
        for t in taskers:
            if t['id'] == tasker_id:
                btns = t.get('quick_buttons', [])
                for b in btns:
                    b = dict(b)
                    b['tasker_id'] = tasker_id
                    b['tasker_label'] = t['label']
                self._window.set_quick_buttons(btns)
                break

        self._window.log(f"Entered: {tasker.label} ({len(tasker.task_list)} tasks)")

    def _enter_settings(self):
        self._state = self.STATE_SETTINGS
        self._window.setWindowTitle("Task - Settings")
        self._window.set_commands(["exit"])

        self._clear_content()

        # Settings form
        from config.app_config import AppConfig
        cfg = AppConfig.get_instance()

        container = QLabel("Settings")
        self._window.content_area.addWidget(container)
        self._window.content_area.setCurrentWidget(container)

        self._window.log("Settings mode. Edit config below, type 'exit' to save and return.")

    def _clear_content(self):
        while self._window.content_area.count() > 0:
            w = self._window.content_area.widget(0)
            self._window.content_area.removeWidget(w)
            w.deleteLater()

    # ================================================================
    # Input dispatch
    # ================================================================

    def _on_input(self, text):
        if not text:
            return
        processed = InputPreprocessor.process(text)
        self._window.log(f"> {text}")

        parts = processed.split(" ", 1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        self._dispatch(cmd, arg)

    def _dispatch(self, cmd, arg):
        if cmd == "exit":
            self._on_exit()
            return
        elif cmd == "settings":
            self._enter_settings()
            return

        if self._state == self.STATE_MAIN:
            self._dispatch_main(cmd, arg)
        elif self._state == self.STATE_TASKER:
            self._dispatch_tasker(cmd, arg)
        elif self._state == self.STATE_SETTINGS:
            self._enter_main()

    def _dispatch_main(self, cmd, arg):
        if not self._tasker_service:
            self._window.log_error("No data. Create a Tasker first with 'add'.")
            return

        # Tasker CRUD
        if cmd == "add":
            self._cmd_add()
        elif cmd == "delete":
            self._cmd_delete(arg)
        elif cmd == "edit":
            self._cmd_edit(arg)
        elif cmd == "info":
            self._cmd_info(arg)
        elif cmd == "sort":
            self._cmd_sort(arg)

        # Global operations
        elif cmd == "backup":
            self._cmd_backup()
        elif cmd == "reload":
            self._cmd_reload(arg)
        elif cmd == "txt":
            self._cmd_txt(arg)
        elif cmd == "migrate":
            self._cmd_migrate(arg)

        # Chart
        elif cmd == "chart":
            self._cmd_chart(arg)

        # Default: try to enter a tasker by label/index
        else:
            taskers = self._tasker_service.list_taskers()
            if not taskers:
                self._window.log("No taskers. Type 'add' to create one.")
                return

            # Try index
            from util.date_utils import convert_to_int
            idx = convert_to_int(cmd)
            if idx is not None and 0 <= idx < len(taskers):
                self._enter_tasker(taskers[idx]['id'])
                return

            # Try label match
            for t in taskers:
                if cmd in t.get('label', '') or cmd == t.get('id', ''):
                    self._enter_tasker(t['id'])
                    return
            self._window.log(f"No tasker matching '{cmd}'")

    def _dispatch_tasker(self, cmd, arg):
        if not self._task_service:
            self._window.log_error("No task service")
            return

        tid = self._current_tasker_id

        if cmd == "new":
            self._cmd_task_new(arg)
        elif cmd == "search":
            self._cmd_task_search(arg)
        elif cmd == "delete":
            self._cmd_task_delete(arg)
        elif cmd == "edit":
            self._cmd_task_edit(arg)
        elif cmd == "backup":
            self._window.log("Backup not yet implemented for single tasker")
        elif cmd == "reload":
            self._window.log("Reload not yet implemented for single tasker")
        elif cmd == "end":
            self._cmd_task_end(arg)
        elif cmd == "config":
            self._window.log("Config not yet implemented for this tasker type")
        else:
            self._window.log(f"Unknown command: {cmd}")

    # ================================================================
    # Main commands
    # ================================================================

    def _cmd_add(self):
        from ui.tasker.tasker_edit_dialog import TaskerEditDialog
        types = self._tasker_service.list_tasker_types() if hasattr(self._tasker_service, 'list_tasker_types') else ['default', 'timer', 'account', 'label']
        dlg = TaskerEditDialog(self._window, types=types)
        if dlg.exec():
            data = dlg.get_data()
            self._tasker_service.create_tasker(data)
            self._refresh_tasker_list()
            self._window.log(f"Created Tasker: {data['label']}")

    def _cmd_delete(self, arg):
        taskers = self._tasker_service.list_taskers()
        if not taskers:
            self._window.log("No taskers to delete.")
            return
        tid = self._find_tasker_id(arg, taskers)
        if tid is None:
            return
        label = next(t['label'] for t in taskers if t['id'] == tid)
        if self._confirm(f"Delete Tasker '{label}'?"):
            self._tasker_service.delete_tasker(tid)
            self._refresh_tasker_list()
            self._window.log(f"Deleted: {label}")

    def _cmd_edit(self, arg):
        taskers = self._tasker_service.list_taskers()
        if not taskers:
            return
        tid = self._find_tasker_id(arg, taskers)
        if tid is None:
            return
        t = next(t for t in taskers if t['id'] == tid)
        from ui.tasker.tasker_edit_dialog import TaskerEditDialog
        dlg = TaskerEditDialog(self._window, tasker_data=t)
        if dlg.exec():
            data = dlg.get_data()
            self._tasker_service.update_tasker(tid, data)
            self._refresh_tasker_list()
            self._window.log(f"Updated: {data['label']}")

    def _cmd_info(self, arg):
        taskers = self._tasker_service.list_taskers()
        if not taskers:
            return
        tid = self._find_tasker_id(arg, taskers)
        if tid is None:
            return
        t = next(t for t in taskers if t['id'] == tid)
        self._window.log(f"Tasker: {t['label']}")
        self._window.log(f"Type: {t['type']}")
        self._window.log(f"Description: {t.get('description', '')}")
        self._window.log(f"Folder: {t.get('folder', '')}")

    def _cmd_sort(self, arg):
        valid = ['create_date', 'tasker_label', 'type', 'version']
        key = arg if arg in valid else 'tasker_label'
        taskers = self._tasker_service.list_taskers()
        taskers.sort(key=lambda t: t.get(key, ''))
        self._tasker_service._storage.tasker_index.save(taskers)
        self._refresh_tasker_list()
        self._window.log(f"Sorted by: {key}")

    def _cmd_backup(self):
        from util.date_utils import now_str
        ts = now_str().replace(':', '-').replace(' ', '_')
        backup_dir = f"./backup_{ts}"
        from util.file_utils import ensure_dir
        ensure_dir(backup_dir)
        self._storage.backup_all(backup_dir)
        self._window.log(f"Backup saved to: {backup_dir}")

    def _cmd_reload(self, arg):
        backup_dir = arg if arg else "./backup_*"
        self._window.log(f"Reload from: {backup_dir}")
        reloaded = self._storage.reload_from_backup(backup_dir)
        if reloaded is None:
            self._window.log_error("Invalid backup directory (no taskers.json)")
            return
        self._window.log(f"Found {len(reloaded)} taskers in backup. Type 'reload_confirm {backup_dir}' to apply.")

    def _cmd_txt(self, arg):
        taskers = self._tasker_service.list_taskers()
        mode_map = {'1': 'date', '2': 'tasker', '3': 'create_date'}
        mode = mode_map.get(arg, 'tasker')
        from io.txt_exporter import TxtExporter
        tasker_objs = [self._tasker_service.get_tasker(t['id']) for t in taskers]
        tasker_objs = [t for t in tasker_objs if t is not None]
        text = '\n'.join(TxtExporter().export(tasker_objs, sort_mode=mode))
        path = './Task_txt.txt'
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        self._window.log(f"Exported to: {path}")

    def _cmd_migrate(self, arg):
        if not arg:
            self._window.log("Usage: migrate <path_to_pkl_or_txt>")
            return
        try:
            # Try txt import first (old backup format)
            if arg.endswith('.txt'):
                from io.txt_importer import TxtImporter
                imp = TxtImporter(arg, self._storage.data_dir)
                tc, tsc = imp.import_data()
                self._refresh_tasker_list()
                self._window.log(f"Imported from txt: {tc} taskers, {tsc} tasks")
                return

            # Try pkl import
            from io.pkl_migrator import PklMigrator
            m = PklMigrator(arg, self._storage.data_dir)
            tc, tsc = m.migrate()
            self._refresh_tasker_list()
            self._window.log(f"Migrated from pkl: {tc} taskers, {tsc} tasks")
        except FileNotFoundError:
            self._window.log_error(f"File not found: {arg}")
        except Exception as e:
            self._window.log_error(f"Migration failed: {e}")

    def _cmd_chart(self, arg):
        if self._chart_server and self._analysis_engine:
            self._chart_server.set_engine(self._analysis_engine)
            self._chart_server.start()
            import webbrowser
            url = f"{self._chart_server.url}/chart/attr_count.html"
            webbrowser.open(url)
            self._window.log(f"Chart opened: {url}")
        else:
            self._window.log("Chart server not configured.")

    # ================================================================
    # Tasker commands
    # ================================================================

    def _cmd_task_new(self, arg):
        tid = self._current_tasker_id
        from ui.task.task_edit_panel import TaskEditPanel
        panel = TaskEditPanel(self._window)
        panel.open_for_create()
        panel.task_submitted.connect(lambda fields: self._do_create_task(tid, fields, panel))
        panel.cancelled.connect(panel.hide_panel)
        self._task_edit_panel = panel
        # Insert below table
        if self._task_table:
            self._window.content_area.layout().addWidget(panel)
        self._window.log("TaskEditPanel opened. Fill fields and click Create.")

    def _do_create_task(self, tid, fields, panel):
        self._task_service.create_task(tid, fields)
        panel.hide_panel()
        tasker = self._tasker_service.get_tasker(tid)
        if self._task_table:
            self._task_table.set_tasks(tasker.task_list)
        self._window.log(f"Created: {fields['content']}")
        # Save
        self._save_current_tasker()

    def _cmd_task_search(self, arg):
        if not arg:
            self._window.log("Usage: search <query>")
            return
        tid = self._current_tasker_id
        results = self._task_service.search_tasks(tid, arg)
        tasker = self._tasker_service.get_tasker(tid)
        display = []
        for idx, task in results:
            display.append((str(idx), f"{task.date}|<{task.attribute}>|{task.content}"))
        self._window.show_search_results(display)
        self._window.log(f"Search '{arg}': {len(results)} results")

    def _cmd_task_delete(self, arg):
        tid = self._current_tasker_id
        tasker = self._tasker_service.get_tasker(tid)
        if not arg:
            self._window.log("Enter delete mode. Type the index to delete.")
            return
        # Try index
        from util.date_utils import convert_to_int
        idx = convert_to_int(arg)
        if idx is not None and 0 <= idx < len(tasker.task_list):
            task = tasker.task_list[idx]
            if self._confirm(f"Delete: {task.content}"):
                self._task_service.delete_task(tid, idx)
                tasker2 = self._tasker_service.get_tasker(tid)
                if self._task_table:
                    self._task_table.set_tasks(tasker2.task_list)
                self._window.log(f"Deleted task at index {idx}")
                self._save_current_tasker()
        else:
            # Search then delete last match
            results = self._task_service.search_tasks(tid, arg)
            if not results:
                self._window.log(f"No task matching '{arg}'")
                return
            idx, task = results[-1]
            if self._confirm(f"Delete: {task.content}"):
                self._task_service.delete_task(tid, idx)
                tasker2 = self._tasker_service.get_tasker(tid)
                if self._task_table:
                    self._task_table.set_tasks(tasker2.task_list)
                self._window.log(f"Deleted task at index {idx}")
                self._save_current_tasker()

    def _cmd_task_edit(self, arg):
        tid = self._current_tasker_id
        tasker = self._tasker_service.get_tasker(tid)
        if not arg:
            self._window.log("Usage: edit <index or search query>")
            return
        from util.date_utils import convert_to_int
        idx = convert_to_int(arg)
        if idx is not None and 0 <= idx < len(tasker.task_list):
            task = tasker.task_list[idx]
            from ui.task.task_edit_panel import TaskEditPanel
            panel = TaskEditPanel(self._window)
            panel.open_for_create({'date': task.date, 'attribute': task.attribute,
                                   'content': task.content, 'comment': task.comment})
            panel.task_submitted.connect(
                lambda fields, i=idx: self._do_edit_task(tid, i, fields, panel))
            panel.cancelled.connect(panel.hide_panel)
            self._window.log(f"Editing task at index {idx}")
        else:
            results = self._task_service.search_tasks(tid, arg)
            if not results:
                self._window.log(f"No task matching '{arg}'")
                return
            if len(results) == 1:
                idx, task = results[0]
                from ui.task.task_edit_panel import TaskEditPanel
                panel = TaskEditPanel(self._window)
                panel.open_for_create({'date': task.date, 'attribute': task.attribute,
                                       'content': task.content, 'comment': task.comment})
                panel.task_submitted.connect(
                    lambda fields, i=idx: self._do_edit_task(tid, i, fields, panel))
                panel.cancelled.connect(panel.hide_panel)
            else:
                self._window.show_search_results(
                    [(str(i), f"{t.date}|<{t.attribute}>|{t.content}") for i, t in results])
                self._window.log(f"Multiple matches. Type edit <index> to select.")

    def _do_edit_task(self, tid, idx, fields, panel):
        self._task_service.update_task(tid, idx, fields)
        panel.hide_panel()
        tasker = self._tasker_service.get_tasker(tid)
        if self._task_table:
            self._task_table.set_tasks(tasker.task_list)
        self._window.log(f"Updated task at index {idx}")
        self._save_current_tasker()

    def _cmd_task_end(self, arg):
        tid = self._current_tasker_id
        tasker = self._tasker_service.get_tasker(tid)
        if not hasattr(tasker, 'end_timer'):
            self._window.log("This tasker does not support 'end' command.")
            return
        from util.date_utils import convert_to_int
        running = tasker.get_running_tasks()
        if not running:
            self._window.log("No running timers.")
            return
        idx = convert_to_int(arg) if arg else running[0][0]
        if idx is not None:
            tasker.end_timer(idx)
            tasker2 = self._tasker_service.get_tasker(tid)
            if self._task_table:
                self._task_table.set_tasks(tasker2.task_list)
            self._window.log(f"Ended timer at index {idx}")
            self._save_current_tasker()

    # ================================================================
    # Helpers
    # ================================================================

    def _find_tasker_id(self, arg, taskers):
        from util.date_utils import convert_to_int
        idx = convert_to_int(arg)
        if idx is not None and 0 <= idx < len(taskers):
            return taskers[idx]['id']
        for t in taskers:
            if arg in t.get('label', ''):
                return t['id']
        self._window.log(f"No tasker matching '{arg}'")
        return None

    def _confirm(self, msg):
        from PySide6.QtWidgets import QMessageBox
        return QMessageBox.question(self._window, "Confirm", msg) == QMessageBox.Yes

    def _save_current_tasker(self):
        tid = self._current_tasker_id
        if not tid:
            return
        tasker = self._tasker_service.get_tasker(tid)
        if tasker:
            self._storage.segment.save(
                tasker.folder,
                [t.to_dict() for t in tasker.task_list],
                tasker.loaded_segments,
                tasker.dirty_segments,
            )

    def _on_exit(self):
        if self._state == self.STATE_MAIN:
            self._window.close()
            self._tray._on_exit()
        elif self._state == self.STATE_TASKER:
            self._save_current_tasker()
            self._enter_main()
        elif self._state == self.STATE_SETTINGS:
            self._enter_main()

    def _on_hide(self):
        if self._state == self.STATE_TASKER:
            self._save_current_tasker()

    def set_tasker_service(self, service):
        self._tasker_service = service
        self._refresh_tasker_list()

    def set_task_service(self, service):
        self._task_service = service

    def set_search_engine(self, engine):
        self._search_engine = engine

    def set_analysis_engine(self, engine):
        self._analysis_engine = engine

    def set_chart_server(self, server):
        self._chart_server = server
