from domain.pieces_api import router as pieces
from domain.bench_steps_api import router as bench_steps
from domain.lead_windows_api import router as lead_windows
from domain.promise_tickets_api import router as promise_tickets
from domain.completion_api import router as completions

routers = (pieces, bench_steps, lead_windows, promise_tickets, completions,)
