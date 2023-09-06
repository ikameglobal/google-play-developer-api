from google_play_developer_api.report.base_report import BaseReportingService


class CrashRateReport(BaseReportingService):
    def __init__(self, credentials_path: str):
        super().__init__(credentials_path=credentials_path)
        self._default_dimensions = [
            "apiLevel",
            "deviceBrand",
            "versionCode",
            "countryCode",
            "deviceType",
            "deviceModel",
            "deviceRamBucket",
            "deviceSocMake",
            "deviceSocModel",
            "deviceCpuMake",
            "deviceCpuModel",
            "deviceGpuMake",
            "deviceGpuModel",
            "deviceGpuVersion",
            "deviceVulkanVersion",
            "deviceGlEsVersion",
            "deviceScreenSize",
            "deviceScreenDpi",
        ]

        self._default_metrics = [
            "crashRate",
            "userPerceivedCrashRate",
            "distinctUsers",
        ]

        self._metric_set = "crashRateMetricSet"
