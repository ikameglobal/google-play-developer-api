import datetime
from google_play_developer_api.report.base_report import BaseReportingService


class AnrRateReport(BaseReportingService):
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
            "anrRate",
            "userPerceivedAnrRate",
            "distinctUsers",
        ]

        self._metric_set = "anrRateMetricSet"

    def get_hourly(
        self,
        app_package_name: str = "",
        start_time: str = "YYYY-MM-DD HH:MM",
        end_time: str = "YYYY-MM-DD HH:MM",
        dimensions: list[str] = [],
        metrics: list[str] = [],
    ) -> list[dict]:
        """
        Get ANR rate report hourly

        Note:
            Read this doc https://developers.google.com/play/developer/reporting/reference/rest/v1beta1/vitals.anrrate

        Args:
            app_package_name: App package name
            start_time: Start time (format YYYY-MM-DD HH:MM)
            end_time: End time (format YYYY-MM-DD HH:MM)
            dimensions: Dimensions (see docs above)
            metrics: Metrics (see docs above)

        Returns:
            List of dicts with report data
        """
        dimensions = self._default_dimensions if not dimensions else dimensions
        metrics = self._default_metrics if not metrics else metrics

        start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M")
        end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M")

        timeline_spec = {
            "aggregationPeriod": "HOURLY",
            "startTime": {
                "year": start_time.year,
                "month": start_time.month,
                "day": start_time.day,
                "hours": start_time.hour,
            },
            "endTime": {
                "year": end_time.year,
                "month": end_time.month,
                "day": end_time.day,
                "hours": end_time.hour,
            },
        }

        return self._query(
            app_package_name=app_package_name,
            timeline_spec=timeline_spec,
            dimensions=dimensions,
            metrics=metrics,
            metric_set=self._metric_set,
        )

    def get_daily(
        self,
        app_package_name: str = "",
        start_time: str = "YYYY-MM-DD",
        end_time: str = "YYYY-MM-DD",
        dimensions: list[str] = [],
        metrics: list[str] = [],
    ) -> list[dict]:
        """
        Get ANR rate report daily

        Note:
            Read this doc https://developers.google.com/play/developer/reporting/reference/rest/v1beta1/vitals.anrrate

        Args:
            app_package_name: App package name
            start_time: Start time (format YYYY-MM-DD)
            end_time: End time (format YYYY-MM-DD)
            dimensions: Dimensions (see docs above)
            metrics: Metrics (see docs above)

        Returns:
            List of dicts with report data
        """
        dimensions = self._default_dimensions if not dimensions else dimensions
        metrics = self._default_metrics if not metrics else metrics

        start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d")
        end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d")

        timeline_spec = {
            "aggregationPeriod": "DAILY",
            "startTime": {
                "year": start_time.year,
                "month": start_time.month,
                "day": start_time.day,
                "timeZone": {"id": "America/Los_Angeles"}
            },
            "endTime": {
                "year": end_time.year,
                "month": end_time.month,
                "day": end_time.day,
                "timeZone": {"id": "America/Los_Angeles"}
            },
        }

        return self._query(
            app_package_name=app_package_name,
            timeline_spec=timeline_spec,
            dimensions=dimensions,
            metrics=metrics,
            metric_set=self._metric_set,
        )
