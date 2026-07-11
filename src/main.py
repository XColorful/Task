"""Task 2.0 — Application entry point.

Usage:
    python main.py [--data-dir DIR] [--port PORT]

All new source code is under src/. This file imports from src/ modules.
Old project code stays in the root directory untouched.
"""

import sys
import os

# Add src to path
_src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, _src_dir)


def register_extensions():
    """Scan and import all extension __init__.py to trigger registration."""
    from core.extension_registry import ExtensionRegistry
    from core.input_processor import InputPreprocessor, step_plus_to_search

    # Clear registries for fresh start
    ExtensionRegistry._task_types.clear()
    ExtensionRegistry._tasker_types.clear()
    ExtensionRegistry._analyzers.clear()
    InputPreprocessor.clear()
    InputPreprocessor.register_step(step_plus_to_search)

    extensions_dir = os.path.join(_src_dir, 'extensions')
    if os.path.isdir(extensions_dir):
        for name in sorted(os.listdir(extensions_dir)):
            pkg_path = os.path.join(extensions_dir, name)
            init_path = os.path.join(pkg_path, '__init__.py')
            if os.path.isfile(init_path) and os.path.getsize(init_path) > 10:
                try:
                    __import__(f'extensions.{name}', fromlist=['*'])
                    print(f"  Loaded extension: {name}")
                except Exception as e:
                    print(f"  Failed to load extension '{name}': {e}")


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description='Task 2.0')
    parser.add_argument('--data-dir', default='./data', help='Data directory')
    parser.add_argument('--port', type=int, default=19527, help='Chart HTTP server port')
    args = parser.parse_args()

    print("Task 2.0 starting...")
    print(f"  Data dir: {args.data_dir}")

    # Register extensions
    register_extensions()

    # Initialize storage
    from core.storage.storage_manager import StorageManager
    storage = StorageManager(args.data_dir)

    # Initialize services
    from core.service.default_tasker_service import DefaultTaskerService
    from core.service.default_task_service import DefaultTaskService
    from core.service.search_engine import SearchEngine

    tasker_service = DefaultTaskerService(storage)
    task_service = DefaultTaskService(storage, tasker_service=tasker_service)
    search_engine = SearchEngine(storage, tasker_service=tasker_service)

    # Initialize analysis engine
    from analysis.analysis_engine import AnalysisEngine
    analysis_engine = AnalysisEngine(storage)

    # Register built-in analyzers
    from analysis.attribute_counter import AttributeCounter
    from analysis.monthly_counter import MonthlyCounter
    from analysis.duration_analyzer import DurationAnalyzer
    from analysis.heatmap_builder import HeatmapBuilder
    from core.extension_registry import ExtensionRegistry
    ExtensionRegistry.register_analyzer('attr_count', AttributeCounter)
    ExtensionRegistry.register_analyzer('monthly_count', MonthlyCounter)
    ExtensionRegistry.register_analyzer('duration', DurationAnalyzer)
    ExtensionRegistry.register_analyzer('heatmap', HeatmapBuilder)

    # Start GUI
    os.environ['QT_QPA_PLATFORM'] = os.environ.get('QT_QPA_PLATFORM', '')
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)

    from ui.main.main_window import MainWindow
    from ui.main.system_tray import SystemTray
    from ui.main.main_controller import MainController

    window = MainWindow()
    tray = SystemTray(window)
    controller = MainController(window, tray, storage)
    controller.set_tasker_service(tasker_service)
    controller.set_task_service(task_service)

    # Set up chart launcher
    from ui.chart.chart_http_server import ChartHttpServer
    chart_server = ChartHttpServer(port=args.port)
    chart_server.set_engine(analysis_engine)
    chart_dir = os.path.join(_src_dir, 'extensions')
    chart_server.set_chart_dir(chart_dir)

    from ui.chart.chart_launcher import ChartLauncher
    chart_launcher = ChartLauncher()
    chart_launcher.set_server(chart_server)

    tray.show()
    window.show()

    print("Task 2.0 ready.")
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
