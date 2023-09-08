from .anr_rate import AnrRateReport
from .crash_rate import CrashRateReport
from .error_count import ErrorCountReport
from .excessive_wake_up_rate import ExcessiveWakeUpRateReport
from .slow_start_rate import SlowStartRateReport
from .slow_rendering_rate import SlowRenderingRateReport
from .stuck_background_wake_lock_rate import StuckBackgroundWakelockRateReport

mapping = {
    "anr_rate": AnrRateReport,
    "crash_rate": CrashRateReport,
    "error_count": ErrorCountReport,
    "excessive_wake_up_rate": ExcessiveWakeUpRateReport,
    "slow_rendering_rate": SlowRenderingRateReport,
    "slow_start_rate": SlowStartRateReport,
    "stuck_background_wake_lock_rate": StuckBackgroundWakelockRateReport
}
