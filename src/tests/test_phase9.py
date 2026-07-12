"""Phase 9 test -- data import/export."""

import sys, os
_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, _src)

from import_export.txt_exporter import TxtExporter
from import_export.export_service import ExportService
from import_export.import_service import ImportService

from core.extension_registry import ExtensionRegistry
ExtensionRegistry._task_types.clear(); ExtensionRegistry._tasker_types.clear()

from extensions.default.default_task import DefaultTask
from extensions.default.default_tasker import DefaultTasker
ExtensionRegistry.register_task_type('default', DefaultTask)
ExtensionRegistry.register_tasker_type('default', DefaultTasker)

import tempfile; d = tempfile.mkdtemp()
from core.storage.storage_manager import StorageManager
from core.service.default_tasker_service import DefaultTaskerService
from core.service.default_task_service import DefaultTaskService

smgr = StorageManager(d)
dts = DefaultTaskerService(smgr)
ts = dts.create_tasker({'type': 'default', 'label': 'Test'})
tid = ts['id']
dtsk = DefaultTaskService(smgr, tasker_service=dts)

dtsk.create_task(tid, {'attribute': 'homework', 'content': 'math'})
dtsk.create_task(tid, {'attribute': 'homework', 'content': 'english'})
dtsk.create_task(tid, {'attribute': 'buy', 'content': 'food'})

# Test 1: TxtExporter by tasker
tasker = dts.get_tasker(tid)
lines = TxtExporter().export([tasker], sort_mode="tasker")
assert any("Tasker: Test" in li for li in lines)
assert any("homework" in li for li in lines)
assert any("math" in li for li in lines)
print("Test 1 OK: TxtExporter by tasker")

# ============================================================
# Test 2: TxtExporter by date
# ============================================================
lines2 = TxtExporter().export([tasker], sort_mode="date")
has_date = False
has_math = False
for li in lines2:
    if "Date:" in li:
        has_date = True
    if "math" in li:
        has_math = True
assert has_date
assert has_math
print("Test 2 OK: TxtExporter by date")

# ============================================================
# Test 3: ExportService
# ============================================================
es = ExportService()
text = es.export_txt([tasker], sort_mode="tasker")
assert "Tasker: Test" in text
print("Test 3 OK: ExportService.export_txt")

# ============================================================
# Test 4: Storage backup
# ============================================================
bd = os.path.join(d, 'backup_test')
smgr.backup_all(bd)
assert os.path.exists(os.path.join(bd, 'taskers.json'))

ims = ImportService()
reloaded = ims.reload_backup(smgr, bd)
assert reloaded is not None
assert len(reloaded) == 1
print("Test 4 OK: Storage backup/restore")

# ============================================================
# Test 5: PklMigrator
# ============================================================
import pickle
old_tasker = DefaultTasker(tasker_id='old1', label='OldTasker', folder='Old_old1')
old_tasker.task_list = [
    DefaultTask(attribute='old_attr', content='old content', date='2023_01_01'),
    DefaultTask(attribute='old_attr', content='old content 2', date='2023_01_02'),
]
pkl_path = os.path.join(d, 'test.pkl')
with open(pkl_path, 'wb') as f:
    pickle.dump([old_tasker], f)

d2 = os.path.join(d, 'migrated')
os.makedirs(d2, exist_ok=True)
result9 = ims.migrate_pkl(pkl_path, d2)
assert result9[0] == 1
assert result9[1] == 2
print('Test 5 OK: pkl migrated')

msmgr = StorageManager(d2)
mtaskers = msmgr.tasker_index.load()
assert len(mtaskers) == 1
assert mtaskers[0]['label'] == 'OldTasker'
print('Test 6 OK: migrated readable')

import shutil
shutil.rmtree(d)
print()
print('ALL 6 TESTS PASSED')
