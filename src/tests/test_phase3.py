"""阶段 3 验证测试——存储层"""

import sys, os, tempfile, json
from collections import OrderedDict

_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, _src)

d = tempfile.mkdtemp()

# ============================================================
# Test 1: TaskerIndexManager — save/load order
# ============================================================
from core.storage.tasker_index_manager import TaskerIndexManager

tim = TaskerIndexManager(d)
assert tim.load() == []
print("Test 1 OK: empty load")

taskers = [
    OrderedDict([('id', 'a1'), ('type', 'default'), ('label', 'B'), ('description', ''), ('folder', 'B_a1'), ('quick_buttons', [])]),
    OrderedDict([('id', 'z9'), ('type', 'default'), ('label', 'A'), ('description', ''), ('folder', 'A_z9'), ('quick_buttons', [])]),
]
tim.save(taskers)
loaded = tim.load()
assert len(loaded) == 2 and loaded[0]['id'] == 'a1' and loaded[1]['id'] == 'z9'
print("Test 2 OK: save/load order preserved")

# ============================================================
# Test 3-8: SegmentManager
# ============================================================
from core.storage.segment_manager import SegmentManager
sm = SegmentManager(d)
folder = 'test_abc12345'
sd = os.path.join(d, folder)
os.makedirs(sd, exist_ok=True)

for i in range(1, 4):
    seg = OrderedDict([('tasks', [
        OrderedDict([('i', i*100 + j), ('content', f'seg{i}_task{j}')]) for j in range(3)
    ])])
    with open(os.path.join(sd, f'segment_{i:04d}.json'), 'w', encoding='utf-8') as f:
        json.dump(seg, f, ensure_ascii=False)

last = sm.load_last(folder, 2)
assert len(last) == 6 and last[0]['content'] == 'seg2_task0' and last[3]['content'] == 'seg3_task0'
print("Test 3 OK: load_last(2)")

allt = sm.load_all(folder)
assert len(allt) == 9
print("Test 4 OK: load_all")

# modify only seg3
allt[8]['content'] = 'MODIFIED'
loaded_set = {'segment_0002.json', 'segment_0003.json'}
dirty_set = {'segment_0003.json'}
sm.save(folder, allt, loaded_set, dirty_set, max_per_segment=3)

with open(os.path.join(sd, 'segment_0002.json'), 'r') as f:
    seg2 = json.load(f)
assert seg2['tasks'][0]['content'] == 'seg2_task0'
print("Test 5 OK: clean segment untouched")

with open(os.path.join(sd, 'segment_0003.json'), 'r') as f:
    seg3 = json.load(f)
assert seg3['tasks'][-1]['content'] == 'MODIFIED'
print("Test 6 OK: dirty segment rewritten")

# expansion: 9+1 tasks, max=3 => 4 segments
allt.append(OrderedDict([('i', 999), ('content', 'new')]))
sm.save(folder, allt, set(), {'segment_0003.json'}, max_per_segment=3)
assert len(sm.list_files(folder)) == 4
print("Test 7 OK: expansion to 4 segments")

# contraction: 1 task => 1 segment
single = [allt[0]]
all_s = set(f'segment_{i:04d}.json' for i in range(1, 5))
sm.save(folder, single, all_s, all_s, max_per_segment=3)
assert len(sm.list_files(folder)) == 1
print("Test 8 OK: contraction to 1 segment")

# ============================================================
# Test 9: AutoSaveManager
# ============================================================
from core.storage.auto_save_manager import AutoSaveManager
saved = []
am = AutoSaveManager()
am.schedule(lambda: saved.append('a'), 50)
am.schedule(lambda: saved.append('b'), 50)
am.flush()
assert saved == ['a', 'b']
am.schedule(lambda: saved.append('c'), 50)
am.cancel()
assert saved == ['a', 'b']
print("Test 9 OK: AutoSaveManager flush/cancel")

# ============================================================
# Test 10: IndexBuilder
# ============================================================
from core.storage.index_builder import IndexBuilder
tim.save(taskers)
result = IndexBuilder.rebuild(d)
assert len(result) == 1 and result[0]['folder'] == folder
print("Test 10 OK: IndexBuilder rebuild")

# ============================================================
# Test 11-12: StorageManager facade + backup
# ============================================================
from core.storage.storage_manager import StorageManager
smgr = StorageManager(d)
tl = smgr.load_tasker_list()
assert len(tl) == 2
assert len(smgr.list_segment_files(folder)) == 1
assert smgr.count_tasks(folder) == 1
print("Test 11 OK: StorageManager facade")

bd = os.path.join(d, 'backup_test')
smgr.backup_all(bd)
assert os.path.exists(os.path.join(bd, 'taskers.json'))
print("Test 12 OK: backup_all")

reloaded = smgr.reload_from_backup(bd)
assert reloaded is not None and len(reloaded) == 2
print("Test 13 OK: reload_from_backup")

import shutil
shutil.rmtree(d)
print()
print("ALL 13 TESTS PASSED")
