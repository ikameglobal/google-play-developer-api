#!/usr/bin/env python
"""Tests for `google_play_developer_api` package."""
# pylint: disable=redefined-outer-name

import os
import datetime
import pytest

from google_play_developer_api import ReportingService


@pytest.fixture
def credentials_path():
    cred_path = os.environ.get("CREDENTIALS_PATH", None)
    assert cred_path is not None
    return cred_path


def test_crash_rate_report_hourly(credentials_path):
    app_package_name = os.environ.get("APP_PACKAGE", None)
    assert app_package_name is not None

    report = ReportingService(credentials_path=credentials_path)
    assert report is not None

    # Set start_date to Yesterday 00:00 and end_date to Yesterday 02:00
    start_date = datetime.datetime.now() - datetime.timedelta(days=1)
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + datetime.timedelta(hours=3)

    start_date = start_date.strftime("%Y-%m-%d %H:%M")
    end_date = end_date.strftime("%Y-%m-%d %H:%M")

    report_data = report.get_crash_rate_report_hourly(app_package_name=app_package_name,
                                                      start_time=start_date,
                                                      end_time=end_date)

    assert len(report_data) > 0


def test_anr_rate_report_hourly(credentials_path):
    app_package_name = os.environ.get("APP_PACKAGE", None)
    assert app_package_name is not None

    report = ReportingService(credentials_path=credentials_path)
    assert report is not None

    # Set start_date to Yesterday 00:00 and end_date to Yesterday 02:00
    start_date = datetime.datetime.now() - datetime.timedelta(days=1)
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + datetime.timedelta(hours=10)

    start_date = start_date.strftime("%Y-%m-%d %H:%M")
    end_date = end_date.strftime("%Y-%m-%d %H:%M")

    report_data = report.get_anr_rate_report_hourly(app_package_name=app_package_name,
                                                    start_time=start_date,
                                                    end_time=end_date)

    assert len(report_data) > 0
    # create  dataframes and write to csv
    # import pandas as pd
    # df = pd.DataFrame(report_data)
    # df.to_csv("anr_rate_report_hourly.csv", index=False)
