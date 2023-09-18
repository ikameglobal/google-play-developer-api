import logging
import time
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


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
        retry_count: int = 3,
        sleep_time: int = 15,
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

            for i in range(retry_count):
                try:
                    report = self._metric_sets[metric_set].query(name=f"apps/{app_package_name}/{metric_set}",
                                                                 body=body).execute()
                    break
                except HttpError as e:
                    if e.resp.status == 403:
                        logging.warning(f'Permission denied for {app_package_name}')
                    elif e.resp.status == 400:
                        logging.warning(f'Bad request for {app_package_name}, {e.reason}')
                        raise e
                    return []

                except TimeoutError as e:
                    raise e
                except Exception as e:
                    if i == retry_count - 1:
                        raise e
                    else:
                        time.sleep(sleep_time)
                        logging.warning(f"Retry {i + 1}/{retry_count}...")
                        continue

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
                "eventDate": f"{year}-{month}-{day}{hour}",
                "timeZone": row["startTime"]["timeZone"]["id"],
                "appPackageName": app_package_name,
            }

            # dimensions
            _dimensions = row.get("dimensions", [])
            for dimension in _dimensions:
                if "stringValue" in dimension:
                    result[f'{dimension["dimension"]}'] = dimension["stringValue"]
                elif "int64Value" in dimension:
                    result[f'{dimension["dimension"]}'] = dimension["int64Value"]
                else:
                    result[f'{dimension["dimension"]}'] = ""
            # metrics
            _metrics = row.get("metrics", [])
            for metric in _metrics:
                result[f'{metric["metric"]}'] = metric["decimalValue"]["value"] if "decimalValue" in metric else ""

            result_list.append(result)

        return result_list

    def get_freshnesses(self,
                        app_package_name: str = None,
                        metric_set: str = None,
                        retry_count: int = 3,
                        sleep_time: int = 5):
        """
        Get freshnesses of a report

        Args:
            app_package_name: App package name
            metric_set: One of ['anrRateMetricSet', 'crashRateMetricSet', 'errorCountMetricSet', 'excessiveWakeupRateMetricSet', 'slowRenderingRateMetricSet', 'slowStartRateMetricSet', 'stuckBackgroundWakelockRateMetricSet']
            retry_count: number of retries
            sleep_time: time to sleep between retries (seconds)

        Returns:
            Dict with freshnesses
        """
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

    def get_hourly(
        self,
        app_package_name: str = "",
        start_time: str = "YYYY-MM-DD HH:MM",
        end_time: str = "YYYY-MM-DD HH:MM",
        dimensions: list[str] = [],
        metrics: list[str] = [],
        metric_set: str = None,
        **kwargs,
    ) -> list[dict]:
        """
        Get hourly report data from Google Play Developer API

        Args:
            app_package_name: App package name
            start_time: Start time (format: YYYY-MM-DD HH:MM)
            end_time: End time (format: YYYY-MM-DD HH:MM)
            dimensions: Dimensions
            metrics: Metrics
            metric_set: One of ['anrRateMetricSet', 'crashRateMetricSet', 'errorCountMetricSet', 'excessiveWakeupRateMetricSet', 'slowRenderingRateMetricSet', 'slowStartRateMetricSet', 'stuckBackgroundWakelockRateMetricSet']

        Returns:
            List of dicts with report data
        """
        dimensions = self._default_dimensions if dimensions is None else dimensions
        metrics = self._default_metrics if metrics is None else metrics
        metric_set = self._metric_set if metric_set is None else metric_set  # Default of each child class

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
            metric_set=metric_set,
            **kwargs,
        )

    def get_daily(
        self,
        app_package_name: str = "",
        start_time: str = "YYYY-MM-DD",
        end_time: str = "YYYY-MM-DD",
        dimensions: list[str] = None,
        metrics: list[str] = None,
        metric_set: str = None,
        **kwargs,
    ) -> list[dict]:
        """
        Get daily report data from Google Play Developer API

        Args:
            app_package_name: App package name
            start_time: Start time (format: YYYY-MM-DD)
            end_time: End time (format: YYYY-MM-DD)
            dimensions: Dimensions
            metrics: Metrics
            metric_set: One of ['anrRateMetricSet', 'crashRateMetricSet', 'errorCountMetricSet', 'excessiveWakeupRateMetricSet', 'slowRenderingRateMetricSet', 'slowStartRateMetricSet', 'stuckBackgroundWakelockRateMetricSet']

        Returns:
            List of dicts with report data
        """
        dimensions = self._default_dimensions if dimensions is None else dimensions
        metrics = self._default_metrics if metrics is None else metrics
        metric_set = self._metric_set if metric_set is None else metric_set  # Default of each child class

        start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d")
        end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d")

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

        return self._query(
            app_package_name=app_package_name,
            timeline_spec=timeline_spec,
            dimensions=dimensions,
            metrics=metrics,
            metric_set=metric_set,
            **kwargs,
        )
