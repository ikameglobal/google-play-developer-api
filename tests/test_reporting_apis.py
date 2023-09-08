#!/usr/bin/env python
"""Tests for `google_play_developer_api` package."""
# pylint: disable=redefined-outer-name

import os
import datetime
import pytest


@pytest.fixture
def credentials_path():
    cred_path = os.environ.get("CREDENTIALS_PATH", None)
    assert cred_path is not None
    return cred_path


def test_crash_rate_report(credentials_path):
    from google_play_developer_api.report import CrashRateReport

    app_package_name = os.environ.get("APP_PACKAGE", None)
    assert app_package_name is not None

    report = CrashRateReport(credentials_path=credentials_path)
    assert report is not None

    # Set start_date to Yesterday 00:00 and end_date to Yesterday 02:00
    start_date = datetime.datetime.now() - datetime.timedelta(days=3)
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + datetime.timedelta(hours=1, days=1)

    report_data = report.get_hourly(app_package_name=app_package_name,
                                    start_time=start_date.strftime("%Y-%m-%d %H:00"),
                                    end_time=end_date.strftime("%Y-%m-%d %H:00"))
    assert len(report_data) > 0

    report_data = report.get_daily(app_package_name=app_package_name,
                                   start_time=start_date.strftime("%Y-%m-%d"),
                                   end_time=end_date.strftime("%Y-%m-%d"))
    assert len(report_data) > 0


def test_anr_rate_report(credentials_path):
    from google_play_developer_api.report import AnrRateReport
    app_package_name = os.environ.get("APP_PACKAGE", None)
    assert app_package_name is not None

    report = AnrRateReport(credentials_path=credentials_path)
    assert report is not None

    # Set start_date to Yesterday 00:00 and end_date to Yesterday 02:00
    start_date = datetime.datetime.now() - datetime.timedelta(days=6)
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

    end_date = start_date + datetime.timedelta(hours=1, days=1)

    report_data = report.get_daily(app_package_name=app_package_name,
                                   start_time=start_date.strftime("%Y-%m-%d"),
                                   end_time=end_date.strftime("%Y-%m-%d"))
    assert len(report_data) > 0

    report_data = report.get_hourly(app_package_name=app_package_name,
                                    start_time=start_date.strftime("%Y-%m-%d %H:00"),
                                    end_time=end_date.strftime("%Y-%m-%d %H:00"))
    assert len(report_data) > 0
