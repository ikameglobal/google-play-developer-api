import datetime

from google.oauth2 import service_account
from googleapiclient.discovery import build


class BaseReportingService:
    def __init__(self, credentials_path: str):
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=["https://www.googleapis.com/auth/playdeveloperreporting"]
        )
        self._reporting_service = build(serviceName="playdeveloperreporting",
                                        version="v1beta1",
                                        credentials=credentials,
                                        cache_discovery=False)

        self._metric_sets = {
            'anomalies': self._reporting_service.anomalies(),
            'anrRateMetricSet': self._reporting_service.vitals().anrrate(),
            'crashRateMetricSet': self._reporting_service.vitals().crashrate(),
            'errorCountMetricSet': self._reporting_service.vitals().errors().counts(),
            'errorIssues': self._reporting_service.vitals().errors().issues(),
            'errorReports': self._reporting_service.vitals().errors().reports(),
            'excessiveWakeupRateMetricSet': self._reporting_service.vitals().excessivewakeuprate(),
            'slowRenderingRateMetricSet': self._reporting_service.vitals().slowrenderingrate(),
            'slowStartRateMetricSet': self._reporting_service.vitals().slowstartrate(),
            'stuckBackgroundWakelockRateMetricSet': self._reporting_service.vitals().stuckbackgroundwakelockrate(),
        }

    def _query(
        self,
        app_package_name: str = "",
        timeline_spec: dict = {},
        dimensions: list[str] = [],
        metrics: list[str] = [],
        metric_set: str = "",
        page_size: int = 50000,
    ) -> list[dict]:
        """
        Query report data from Google Play Developer API

        Note: Read this doc
        https://developers.google.com/play/developer/reporting/reference/rest

        Args:
            app_package_name: App package name
            timeline_spec: Timeline spec (see docs above)
            dimensions: Dimensions (see docs above)
            metrics: Metrics (see docs above)
            metric_set: One of ['anrRateMetricSet', 'crashRateMetricSet', 'errorCountMetricSet', 'excessiveWakeupRateMetricSet', 'slowRenderingRateMetricSet', 'slowStartRateMetricSet', 'stuckBackgroundWakelockRateMetricSet']
            page_size: Page size

        Returns:
            List of dicts with report data
        """
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

            report = self._metric_sets[metric_set].query(name=f"apps/{app_package_name}/{metric_set}",
                                                         body=body).execute()

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

    def get_freshnesses(self,
                        app_package_name: str = None,
                        metric_set: str = None,
                        retry_count: int = 3,
                        sleep_time: int = 5):
        import time

        metric_set = self._metric_set if not metric_set else metric_set  # Default of each child class
        for i in range(retry_count):
            try:
                data = self._metric_sets[metric_set].get(name=f"apps/{app_package_name}/{metric_set}").execute()
                break
            except Exception as e:
                if i == retry_count - 1:
                    raise e
                else:
                    time.sleep(sleep_time)
                    continue

        freshnesses = data.get('freshnessInfo', {}).get('freshnesses', [])
        result = {
            'HOURLY': {},
            'DAILY': {},
        }

        for freshness in freshnesses:
            latest_end_time = freshness.get('latestEndTime', {})
            time_zone = latest_end_time.get('timeZone', {})
            year = latest_end_time.get('year')
            month = latest_end_time.get('month')
            day = latest_end_time.get('day')
            hour = latest_end_time.get('hours', 0)

            result[freshness['aggregationPeriod']] = {
                'event_date': f"{year}-{month}-{day} {hour}:00",
                'time_zone': time_zone,
            }

        return result


if __name__ == '__main__':
    report_service = BaseReportingService(
        credentials_path='/home/dawn/work/.secrets/ikame_game_google_play_developer_report.json')

    start_time = datetime.datetime.strptime('2023-09-01', "%Y-%m-%d")
    end_time = datetime.datetime.strptime('2023-09-04', "%Y-%m-%d")

    timeline_spec = {
        "aggregationPeriod": "DAILY",
        "startTime": {
            "year": start_time.year,
            "month": start_time.month,
            "day": start_time.day,
            "timeZone": {"id": "America/Los_Angeles"},
        },
        "endTime": {
            "year": end_time.year,
            "month": end_time.month,
            "day": end_time.day,
            "timeZone": {"id": "America/Los_Angeles"},
        },
    }

    dimensions = ['reportType', 'versionCode', 'issueId', 'apiLevel', 'deviceModel', 'deviceBrand',
                  'deviceType', 'deviceRamBucket', 'deviceSocMake', 'deviceSocModel', 'deviceCpuMake', 'deviceCpuModel',
                  'deviceGpuMake', 'deviceGpuModel', 'deviceGpuVersion', 'deviceVulkanVersion', 'deviceGlEsVersion',
                  'deviceScreenSize', 'deviceScreenDpi']
    metrics = ['errorReportCount', 'distinctUsers']

    # a = report_service._query(
    #     app_package_name='com.jura.coloring.page',
    #     timeline_spec=timeline_spec,
    #     dimensions=dimensions,
    #     metrics=metrics,
    #     metric_set='errorCountMetricSet',
    #     page_size=50000
    # )

    a = report_service.get_freshnesses(
        app_package_name='com.jura.coloring.page',
        metric_set='stuckBackgroundWakelockRateMetricSet',
    )

    print(a)
#     def get_crash_rate_report_hourly(
#         self,
#         app_package_name: str = "",
#         start_time: str = "YYYY-MM-DD HH:00",
#         end_time: str = "YYYY-MM-DD HH:00",
#         dimensions: list[str] = [],
#         metrics: list[str] = [],
#     ) -> list[dict]:
#         """
#         Get crash rate report hourly
#
#         Note:
#             Read this doc https://developers.google.com/play/developer/reporting/reference/rest/v1beta1/vitals.crashrate/query#request-body
#
#         Args:
#             app_package_name: App package name
#             start_time: Start time (format YYYY-MM-DD HH:00)
#             end_time: End time (format YYYY-MM-DD HH:00)
#             dimensions: Dimensions (see docs above)
#             metrics: Metrics (see docs above)
#
#         Returns:
#             List of dicts with report data
#         """
#         dimensions = (
#             [
#                 "apiLevel",
#                 "deviceBrand",
#                 "versionCode",
#                 "countryCode",
#                 "deviceType",
#                 "deviceModel",
#                 "deviceRamBucket",
#                 "deviceSocMake",
#                 "deviceSocModel",
#                 "deviceCpuMake",
#                 "deviceCpuModel",
#                 "deviceGpuMake",
#                 "deviceGpuModel",
#                 "deviceGpuVersion",
#                 "deviceVulkanVersion",
#                 "deviceGlEsVersion",
#                 "deviceScreenSize",
#                 "deviceScreenDpi",
#             ]
#             if not dimensions
#             else dimensions
#         )
#
#         metrics = (
#             [
#                 "crashRate",
#                 "userPerceivedCrashRate",
#                 "distinctUsers",
#             ]
#             if not metrics
#             else metrics
#         )
#         metric_set = "crashRateMetricSet"
#
#         start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:00")
#         end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:00")
#
#         timeline_spec = {
#             "aggregationPeriod": "HOURLY",
#             "startTime": {
#                 "year": start_time.year,
#                 "month": start_time.month,
#                 "day": start_time.day,
#                 "hours": start_time.hour,
#             },
#             "endTime": {
#                 "year": end_time.year,
#                 "month": end_time.month,
#                 "day": end_time.day,
#                 "hours": end_time.hour,
#             },
#         }
#
#         return self._query(
#             app_package_name=app_package_name,
#             timeline_spec=timeline_spec,
#             dimensions=dimensions,
#             metrics=metrics,
#             metric_set=metric_set,
#         )
#
#
#
#     def get_crash_rate_report_daily(
#         self,
#         app_package_name: str = "",
#         start_time: str = "YYYY-MM-DD",
#         end_time: str = "YYYY-MM-DD",
#         dimensions: list[str] = [],
#         metrics: list[str] = [],
#     ) -> list[dict]:
#         """
#         Get crash rate report daily
#
#         Note:
#             Read this doc https://developers.google.com/play/developer/reporting/reference/rest/v1beta1/vitals.crashrate/query#request-body
#
#         Args:
#             app_package_name: App package name
#             start_time: Start time (format YYYY-MM-DD)
#             end_time: End time (format YYYY-MM-DD)
#             dimensions: Dimensions (see docs above)
#             metrics: Metrics (see docs above)
#
#         Returns:
#             List of dicts with report data
#         """
#         dimensions = (
#             [
#                 "apiLevel",
#                 "deviceBrand",
#                 "versionCode",
#                 "countryCode",
#                 "deviceType",
#                 "deviceModel",
#                 "deviceRamBucket",
#                 "deviceSocMake",
#                 "deviceSocModel",
#                 "deviceCpuMake",
#                 "deviceCpuModel",
#                 "deviceGpuMake",
#                 "deviceGpuModel",
#                 "deviceGpuVersion",
#                 "deviceVulkanVersion",
#                 "deviceGlEsVersion",
#                 "deviceScreenSize",
#                 "deviceScreenDpi",
#             ]
#             if not dimensions
#             else dimensions
#         )
#
#         metrics = (
#             [
#                 "crashRate",
#                 "userPerceivedCrashRate",
#                 "distinctUsers",
#             ]
#             if not metrics
#             else metrics
#         )
#         metric_set = "crashRateMetricSet"
#
#         start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d")
#         end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d")
#
#         timeline_spec = {
#             "aggregationPeriod": "DAILY",
#             "startTime": {
#                 "year": start_time.year,
#                 "month": start_time.month,
#                 "day": start_time.day,
#                 "timeZone": {"id": "America/Los_Angeles"},
#             },
#             "endTime": {
#                 "year": end_time.year,
#                 "month": end_time.month,
#                 "day": end_time.day,
#                 "timeZone": {"id": "America/Los_Angeles"},
#             },
#         }
#
#         return self._query(
#             app_package_name=app_package_name,
#             timeline_spec=timeline_spec,
#             dimensions=dimensions,
#             metrics=metrics,
#             metric_set=metric_set,
#         )
#
#
