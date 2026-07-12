"""阶段 1 验证测试——core 抽象层"""

import sys
import os

_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, _src)

# ============================================================
# Test 1: submodule imports
# ============================================================
from core.abstract import BaseTask, BaseTasker, BaseAnalyzer
from core.extension_registry import ExtensionRegistry
from core.base_service import BaseTaskerService, BaseTaskService
from core.input_processor import InputPreprocessor, step_plus_to_search
from core.types import TaskerSummary, QuickButtonDef, PresetFields, SearchQuery, AnalysisParams
print('Test 1 PASS: all submodule imports OK')

# ============================================================
# Test 2: util imports
# ============================================================
from util.date_utils import today_str, now_str, parse_date, is_valid_date, format_duration
print('Test 2 PASS: util imports OK')

# ============================================================
# Test 3: date_utils functions
# ============================================================
today = today_str()
assert len(today) == 10 and today[4] == '_' and today[7] == '_'
print(f'Test 3.1 PASS: today_str() = {today}')

now = now_str()
assert len(now) == 16 and now[10] == '-'
print(f'Test 3.2 PASS: now_str() = {now}')

assert parse_date('2026_07_11') is not None
assert parse_date('2026_07_11-14:30') is not None
print('Test 3.3 PASS: parse_date()')

assert is_valid_date('2026_07_11') is True
assert is_valid_date('invalid') is False
print('Test 3.4 PASS: is_valid_date()')

f = format_duration(3255)
assert '2d' in f and '6h' in f and '15m' in f
assert format_duration(0) == ' 0m'
assert format_duration(-1) == 'Error'
print(f'Test 3.5 PASS: format_duration(3255) = {f!r}')

# ============================================================
# Test 4: InputPreprocessor
# ============================================================
InputPreprocessor.clear()
InputPreprocessor.register_step(step_plus_to_search)
assert InputPreprocessor.process('+hello') == 'search hello'
assert InputPreprocessor.process('normal') == 'normal'
print('Test 4 PASS: InputPreprocessor')

# ============================================================
# Test 5: ExtensionRegistry
# ============================================================
from collections import OrderedDict

class _T(BaseTask):
    def to_dict(self): return OrderedDict([('type','t'),('content',self.content)])
    @classmethod
    def from_dict(cls, d):
        t = cls(); t.content = d.get('content',''); return t
    def matches_search(self, q): return q in self.content

ExtensionRegistry.register_task_type('test', _T)
t = ExtensionRegistry.create_task('test', content='hello')
assert t.matches_search('hello') and not t.matches_search('xyz')
print('Test 5 PASS: ExtensionRegistry')

# ============================================================
# Test 6: BaseTasker
# ============================================================
class _TR(BaseTasker):
    def get_commands(self): return ['new']
    def create_task(self, f): return _T(content=f.get('content',''))
    def execute_quick_button(self, bt):
        return self.create_task(bt.get('preset',{}))
    def mark_dirty(self, s): self.dirty_segments.add(s)

tr = _TR(tasker_id='t1', label='T')
tk = tr.create_task({'content':'x'})
assert tk.content == 'x'
tr.mark_dirty('s1.json')
assert 's1.json' in tr.dirty_segments
print('Test 6 PASS: BaseTasker')

# ============================================================
# Test 7: QuickButtonDef
# ============================================================
btn: QuickButtonDef = {
    'command': 'hw', 'label': '记作业',
    'preset': {'attribute': '作业', 'use_default_date': True}
}
assert btn['preset']['use_default_date'] is True
print('Test 7 PASS: QuickButtonDef')

# ============================================================
# Test 8: QuickButton execution
# ============================================================
result = tr.execute_quick_button({'preset': {'content': 'quick'}})
assert result is not None and result.content == 'quick'
print('Test 8 PASS: execute_quick_button')

print()
print('=== ALL 8 TESTS PASSED ===')
