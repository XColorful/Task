"""Phase 8 test -- analysis engine, analyzers, 3D builder, HTTP server, chart pages."""

import sys, os, tempfile, json, time, urllib.request

_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, _src)

from core.extension_registry import ExtensionRegistry
ExtensionRegistry._task_types.clear(); ExtensionRegistry._tasker_types.clear()
ExtensionRegistry._analyzers.clear()

from extensions.default.default_task import DefaultTask
from extensions.default.default_tasker import DefaultTasker
ExtensionRegistry.register_task_type('default', DefaultTask)
ExtensionRegistry.register_tasker_type('default', DefaultTasker)

from extensions.timer.timer_task import TimerTask
from extensions.timer.timer_tasker import TimerTasker
ExtensionRegistry.register_task_type('timer', TimerTask)
ExtensionRegistry.register_tasker_type('timer', TimerTasker)

from analysis.attribute_counter import AttributeCounter
from analysis.monthly_counter import MonthlyCounter
from analysis.duration_analyzer import DurationAnalyzer
from analysis.heatmap_builder import HeatmapBuilder
ExtensionRegistry.register_analyzer('attr_count', AttributeCounter)
ExtensionRegistry.register_analyzer('monthly_count', MonthlyCounter)
ExtensionRegistry.register_analyzer('duration', DurationAnalyzer)
ExtensionRegistry.register_analyzer('heatmap', HeatmapBuilder)

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
dtsk.create_task(tid, {'attribute': 'buy', 'content': 'book'})
dtsk.create_task(tid, {'attribute': 'dev', 'content': 'coding'})

# Save to disk so analyzers can read
tasker = dts.get_tasker(tid)
smgr.segment.save(tasker.folder,
    [t.to_dict() for t in tasker.task_list],
    tasker.loaded_segments, tasker.dirty_segments)
dts._tasker_cache.clear()

# ============================================================
from analysis.analysis_engine import AnalysisEngine
engine = AnalysisEngine(smgr)

result = engine.analyze('attr_count', {'tasker_id': tid})
assert result['labels']
assert sum(result['values']) == 5
print("Test 1 OK: AttributeCounter")

result2 = engine.analyze('monthly_count', {'tasker_id': tid})
assert len(result2['labels']) >= 1
assert result2['values'][0] == 5
print("Test 2 OK: MonthlyCounter")

# ============================================================
ts2 = dts.create_tasker({'type': 'timer', 'label': 'Timer'})
ttid = ts2['id']
dtsk2 = DefaultTaskService(smgr, tasker_service=dts)
dtsk2.create_task(ttid, {'content': 'coding', 'attribute': 'dev',
    'start_time': '2026_07_11-10:00', 'end_time': '2026_07_11-12:30'})
dtsk2.create_task(ttid, {'content': 'meeting', 'attribute': 'meet',
    'start_time': '2026_07_11-14:00', 'end_time': '2026_07_11-15:00'})

tasker2 = dts.get_tasker(ttid)
smgr.segment.save(tasker2.folder,
    [t.to_dict() for t in tasker2.task_list],
    tasker2.loaded_segments, tasker2.dirty_segments)
dts._tasker_cache.clear()

result3 = engine.analyze('duration', {'tasker_id': ttid})
assert 'dev' in result3['labels']
assert result3['unit'] == 'hours'
print("Test 3 OK: DurationAnalyzer")

result4 = engine.analyze('heatmap', {'tasker_id': tid})
assert len(result4['x_labels']) >= 1
assert len(result4['data']) > 0
print("Test 4 OK: HeatmapBuilder")

# ============================================================
from visualization.monthly_3d_builder import Monthly3DBuilder
tasker3 = dts.get_tasker(ttid)
smgr.segment.save(tasker3.folder,
    [t.to_dict() for t in tasker3.task_list],
    tasker3.loaded_segments, tasker3.dirty_segments)
dts._tasker_cache.clear()

# Load fresh from disk
all_timer = smgr.segment.load_all(tasker3.folder)
from core.service.default_tasker_service import DefaultTaskerService as DTS
svc3 = DTS(smgr)
timer_tasks = [svc3._create_task_from_dict(td, 'timer') for td in all_timer]

result5 = Monthly3DBuilder.build(timer_tasks)
assert len(result5['data']) == 2
assert result5['labels'] == ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
assert len(result5['color_map']) >= 1
print("Test 5 OK: Monthly3DBuilder")

# ============================================================
from ui.chart.chart_http_server import ChartHttpServer
srv = ChartHttpServer(port=19528)
srv.set_engine(engine)
srv.set_chart_dir(os.path.join(_src, 'extensions'))
srv.start()
time.sleep(0.3)

resp = urllib.request.urlopen('http://127.0.0.1:19528/api/analysis/attr_count')
body = json.loads(resp.read())
assert 'labels' in body
print("Test 6 OK: ChartHttpServer API")

resp2 = urllib.request.urlopen('http://127.0.0.1:19528/chart/attr_count.html')
assert resp2.status == 200
assert b'echarts' in resp2.read()
print("Test 7 OK: ChartHttpServer serves HTML")

srv.stop()
time.sleep(0.2)

try:
    urllib.request.urlopen('http://127.0.0.1:19528/api/analysis/attr_count', timeout=1)
    assert False
except Exception:
    print("Test 8 OK: ChartHttpServer stopped")

import shutil; shutil.rmtree(d)
print()
print("ALL 8 TESTS PASSED")
