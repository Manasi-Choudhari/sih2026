"""
Trace Engine Limits and Control Parameters (from BUILD.md)
- Max depth: hard ceiling, initial target 8 hops.
- Value cutoff: stop branches once cumulative value falls below ~1% of origin.
- Fan-out cap: large fan-out terminates as a mixer-scale/pattern event, not a normal branch.
- Termination states: VASP reached, mixer/privacy boundary, depth/value limit, unresolved/cold data.
"""

MAX_TRACE_DEPTH = 8
VALUE_CUTOFF_PCT = 0.01  # 1% of origin
FANOUT_CAP = 10
TIME_BUDGET_SECONDS = 10.0

TERMINATION_VASP = "vasp_reached"
TERMINATION_MIXER = "evidentiary_break_mixer"
TERMINATION_LIMIT = "limit_reached"
TERMINATION_FANOUT = "mixer_scale_fanout"
TERMINATION_COLD = "unresolved_cold_data"
