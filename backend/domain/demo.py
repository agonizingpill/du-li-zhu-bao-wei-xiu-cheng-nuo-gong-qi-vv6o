from domain.pieces_model import pieces
from domain.bench_steps_model import bench_steps
from domain.lead_windows_model import lead_windows
from domain.promise_tickets_model import promise_tickets

FIXTURES = [
    (pieces, [{'code': 'JW-001',
  'description': '椭圆戒面 · 爪位松动',
  'mass_g': 5.6,
  'stone_count': 1,
  'seal': 'BAG-892A',
  'arrived': '2026-11-24'},
 {'code': 'JW-002',
  'description': '素银细镯 · 单面划痕',
  'mass_g': 9.2,
  'stone_count': 0,
  'seal': 'BAG-893B',
  'arrived': '2026-11-24'}]),
    (bench_steps, [{'code': 'OP-001',
  'piece': 'JW-001',
  'operation': '镶石拆装',
  'minutes': 85,
  'first_witness': None,
  'second_witness': None},
 {'code': 'OP-002',
  'piece': 'JW-001',
  'operation': '抛光',
  'minutes': 30,
  'first_witness': None,
  'second_witness': None},
 {'code': 'OP-003',
  'piece': 'JW-002',
  'operation': '抛光',
  'minutes': 45,
  'first_witness': None,
  'second_witness': None}]),
    (lead_windows, []),
    (promise_tickets, []),
]
