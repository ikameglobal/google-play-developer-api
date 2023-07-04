import datetime

from google.oauth2 import service_account
from googleapiclient.discovery import build


class ReportingService:
    def __init__(self, credentials_path: str):
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=["https://www.googleapis.com/auth/playdeveloperreporting"]
        )
        self._reporting_service = build(
            "playdeveloperreporting", "v1beta1", credentials=credentials, cache_discovery=False
        )

    def _get_report_data(
        self,
        app_package_name: str = "",
        timeline_spec: dict = {},
        dimensions: list[str] = [],
        metrics: list[str] = [],
        metric_set: str = "",
        page_size: int = 100000,
    ) -> list[dict]:
        """
        Get report data from Google Play Developer API

        Note: Read this doc
        https://developers.google.com/play/developer/reporting/reference/rest/v1beta1/vitals.crashrate/query#request-body

        Args:
            app_package_name: App package name
            timeline_spec: Timeline spec (see docs above)
            dimensions: Dimensions (see docs above)
            metrics: Metrics (see docs above)
            metric_set: One of the following *anrRateMetricSet*, *crashRateMetricSet*, *excessiveWakeupRateMetricSet*, *stuckBackgroundWakelockRateMetricSet*
            page_size: Page size

        Returns:
            List of dicts with report data
        """

        dimensions = (
            [
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
            if not dimensions
            else dimensions
        )

        # GET DATA
        page_token = ""
        rows = []
        while True:
            body = {
                "dimensions": dimensions,
                "metrics": metrics,
                "timelineSpec": timeline_spec,
                "pageSize": page_size,
                "pageToken": page_token
            }

            if metric_set == "anrRateMetricSet":
                report = (
                    self._reporting_service.vitals()
                    .anrrate()
                    .query(
                        name=f"apps/{app_package_name}/{metric_set}",
                        body=body,
                    )
                    .execute()
                )
            elif metric_set == "crashRateMetricSet":
                report = (
                    self._reporting_service.vitals()
                    .crashrate()
                    .query(
                        name=f"apps/{app_package_name}/{metric_set}",
                        body=body,
                    )
                    .execute()
                )
            elif metric_set == "excessiveWakeupRateMetricSet":
                report = (
                    self._reporting_service.vitals()
                    .excessivewakeuprate()
                    .query(
                        name=f"apps/{app_package_name}/{metric_set}",
                        body=body,
                    )
                    .execute()
                )
            elif metric_set == "stuckBackgroundWakelockRateMetricSet":
                report = (
                    self._reporting_service.vitals()
                    .stuckbackgroundwakelockrate()
                    .query(
                        name=f"apps/{app_package_name}/{metric_set}",
                        body=body,
                    )
                    .execute()
                )

            rows.extend(report.get("rows", []))
            page_token = report.get("nextPageToken", "")
            if not page_token:
                break

        # PARSE DATA
        result_list = []
        for row in rows:
            year = row["startTime"].get("year")
            month = row["startTime"].get("month")
            day = row["startTime"].get("day")

            # Add hour if aggregationPeriod is HOURLY
            if timeline_spec["aggregationPeriod"] == "HOURLY":
                hour = row["startTime"].get("hours", "00")
                hour = f" {hour}:00"
            else:
                hour = ""

            result = {
                "event_date": f"{year}-{month}-{day}{hour}",
                "time_zone": row["startTime"]["timeZone"]["id"],
                "app_package_name": app_package_name,
            }

            # dimensions
            for dimension in row["dimensions"]:
                if "stringValue" in dimension:
                    result[f'{dimension["dimension"]}'] = dimension["stringValue"]
                elif "int64Value" in dimension:
                    result[f'{dimension["dimension"]}'] = dimension["int64Value"]
                else:
                    result[f'{dimension["dimension"]}'] = ""
            # metrics
            for metric in row["metrics"]:
                result[f'{metric["metric"]}'] = metric["decimalValue"]["value"] if "decimalValue" in metric else ""

            result_list.append(result)

        return result_list

    def get_crash_rate_report_hourly(
        self,
        app_package_name: str = "",
        start_time: str = "YYYY-MM-DD HH:00",
        end_time: str = "YYYY-MM-DD HH:00",
        dimensions: list[str] = [],
        metrics: list[str] = [],
    ) -> list[dict]:
        """
        Get crash rate report hourly

        Note:
            Read this doc https://developers.google.com/play/developer/reporting/reference/rest/v1beta1/vitals.crashrate/query#request-body

        Args:
            app_package_name: App package name
            start_time: Start time (format YYYY-MM-DD HH:00)
            end_time: End time (format YYYY-MM-DD HH:00)
            dimensions: Dimensions (see docs above)
            metrics: Metrics (see docs above)

        Returns:
            List of dicts with report data
        """
        dimensions = (
            [
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
            if not dimensions
            else dimensions
        )

        metrics = (
            [
                "crashRate",
                "userPerceivedCrashRate",
                "distinctUsers",
            ]
            if not metrics
            else metrics
        )
        metric_set = "crashRateMetricSet"

        start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:00")
        end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:00")

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

        return self._get_report_data(
            app_package_name=app_package_name,
            timeline_spec=timeline_spec,
            dimensions=dimensions,
            metrics=metrics,
            metric_set=metric_set,
        )

    def get_anr_rate_report_hourly(
        self,
        app_package_name: str = "",
        start_time: str = "YYYY-MM-DD HH:00",
        end_time: str = "YYYY-MM-DD HH:00",
        dimensions: list[str] = [],
        metrics: list[str] = [],
    ) -> list[dict]:
        """
        Get ANR rate report hourly

        Note:
            Read this doc https://developers.google.com/play/developer/reporting/reference/rest/v1beta1/vitals.anrrate

        Args:
            app_package_name: App package name
            start_time: Start time (format YYYY-MM-DD HH:00)
            end_time: End time (format YYYY-MM-DD HH:00)
            dimensions: Dimensions (see docs above)
            metrics: Metrics (see docs above)

        Returns:
            List of dicts with report data
        """
        dimensions = (
            [
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
            if not dimensions
            else dimensions
        )

        metrics = (
            [
                "anrRate",
                "userPerceivedAnrRate",
                "distinctUsers",
            ]
            if not metrics
            else metrics
        )
        metric_set = "anrRateMetricSet"

        start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:00")
        end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:00")

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

        return self._get_report_data(
            app_package_name=app_package_name,
            timeline_spec=timeline_spec,
            dimensions=dimensions,
            metrics=metrics,
            metric_set=metric_set,
        )
