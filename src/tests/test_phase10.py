"""Phase 10 test -- verify main.py entry point and end-to-end pipeline."""

import sys, os, tempfile

_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, _src)

from core.extension_registry import ExtensionRegistry
from core.input_processor import InputPreprocessor, step_plus_to_search
ExtensionRegistry._task_types.clear(); ExtensionRegistry._tasker_types.clear()
ExtensionRegistry._analyzers.clear()
InputPreprocessor.clear()
InputPreprocessor.register_step(step_plus_to_search)

from extensions.default.default_task import DefaultTask
from extensions.default.default_tasker import DefaultTasker
ExtensionRegistry.register_task_type('default', DefaultTask)
ExtensionRegistry.register_tasker_type('default', DefaultTasker)

from extensions.timer.timer_task import TimerTask
from extensions.timer.timer_tasker import TimerTasker
ExtensionRegistry.register_task_type('timer', TimerTask)
ExtensionRegistry.register_tasker_type('timer', TimerTasker)

from extensions.account.account_task import AccountTask
from extensions.account.account_tasker import AccountTasker
ExtensionRegistry.register_task_type('account', AccountTask)
ExtensionRegistry.register_tasker_type('account', AccountTasker)

from extensions.label.label_task import LabelTask
from extensions.label.label_tasker import LabelTasker
ExtensionRegistry.register_task_type('label', LabelTask)
ExtensionRegistry.register_tasker_type('label', LabelTasker)

assert len(ExtensionRegistry.list_task_types()) == 4
print("Test 1 OK: 4 types registered")

d = tempfile.mkdtemp()
from core.storage.storage_manager import StorageManager
from core.service.default_tasker_service import DefaultTaskerService
from core.service.default_task_service import DefaultTaskService

smgr = StorageManager(d)
dts = DefaultTaskerService(smgr)
dtsk = DefaultTaskService(smgr, tasker_service=dts)

ts = dts.create_tasker({'type': 'default', 'label': 'E2E'})
assert ts['label'] == 'E2E'
dtsk.create_task(ts['id'], {'content': 'test'})
tasker = dts.get_tasker(ts['id'])
assert len(tasker.task_list) == 1
print("Test 2 OK: create tasker + task")

from analysis.attribute_counter import AttributeCounter
from analysis.monthly_counter import MonthlyCounter
ExtensionRegistry.register_analyzer('attr_count', AttributeCounter)
ExtensionRegistry.register_analyzer('monthly_count', MonthlyCounter)
assert 'attr_count' in ExtensionRegistry._analyzers
print("Test 3 OK: analyzers registered")

from analysis.analysis_engine import AnalysisEngine
engine = AnalysisEngine(smgr)
tasker2 = dts.get_tasker(ts['id'])
smgr.segment.save(tasker2.folder, [t.to_dict() for t in tasker2.task_list],
    tasker2.loaded_segments, tasker2.dirty_segments)
dts._tasker_cache.clear()
r = engine.analyze('attr_count', {'tasker_id': ts['id']})
assert r['values'] == [1]
print("Test 4 OK: analysis engine")

import shutil; shutil.rmtree(d)
print()
print("ALL 4 TESTS PASSED")
