For more information about the API (params, columns), see
the [Reporting API](https://google.com).

# Reporting API

## Get crash rate hourly report

```python
from google_play_developer_api.report import CrashRateReport

report = CrashRateReport(credentials_path='<path-to-your-credentials>')
result = report.get_hourly(app_package_name='your-app-package',
                           start_time='YYYY-MM-DD HH:MM',
                           end_time='YYYY-MM-DD HH:MM')
print(result)
```

## Get ANR rate daily report

```python
from google_play_developer_api.report import AnrRateReport

report = AnrRateReport(credentials_path='<path-to-your-credentials>')
result = report.get_daily(app_package_name='your-app-package',
                          start_time='YYYY-MM-DD',
                          end_time='YYYY-MM-DD')
```
