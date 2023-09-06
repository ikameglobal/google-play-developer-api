from google_play_developer_api.report.base_report import BaseReportingService


class ErrorCountReport(BaseReportingService):
    def __init__(self, credentials_path: str):
        super().__init__(credentials_path=credentials_path)
        # Note: can use isUserPerceived dimension (Google internal-only) to filter out non-user-perceived errors.
        self._default_dimensions = [
            "reportType",
            'versionCode',
            'issueId',
            'apiLevel',
            'deviceModel',
            'deviceBrand',
            'deviceType',
            'deviceRamBucket',
            'deviceSocMake',
            'deviceSocModel',
            'deviceCpuMake',
            'deviceCpuModel',
            'deviceGpuMake',
            'deviceGpuModel',
            'deviceGpuVersion',
            'deviceVulkanVersion',
            'deviceGlEsVersion',
            'deviceScreenSize',
            'deviceScreenDpi'
        ]

        self._default_metrics = [
            "errorReportCount",
            "distinctUsers"
        ]

        self._metric_set = "errorCountMetricSet"
