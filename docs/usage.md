For more information about the API (params, columns), see
the [Reporting API](https://google.com).

# Reporting API

## Get crash rate hourly report

```python
from google_play_developer_api import ReportingService

report = ReportingService(credentials_path='<path-to-your-credentials>')
result = report.get_crash_rate_report_hourly(app_package_name='your-app-package',
                                             start_time='YYYY-MM-DD HH:00',
                                             end_time='YYYY-MM-DD HH:00')
print(result)
```

## Get ANR rate daily report

```python
from google_play_developer_api import ReportingService

report = ReportingService(credentials_path='<path-to-your-credentials>')
result = report.get_anr_rate_report_daily(app_package_name='your-app-package',
                                          start_time='YYYY-MM-DD',
                                          end_time='YYYY-MM-DD')
```
