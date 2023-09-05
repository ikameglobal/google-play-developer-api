#!/usr/bin/env python
"""Tests for `google_play_developer_api` package."""
# pylint: disable=redefined-outer-name

import os
import datetime
import pytest

from google_play_developer_api import BaseReportingService


@pytest.fixture
def credentials_path():
    cred_path = os.environ.get("CREDENTIALS_PATH", None)
    assert cred_path is not None
    return cred_path


def test_crash_rate_report_hourly(credentials_path):
    app_package_name = os.environ.get("APP_PACKAGE", None)
    assert app_package_name is not None

    report = BaseReportingService(credentials_path=credentials_path)
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

    report = BaseReportingService(credentials_path=credentials_path)
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


def test_anr_rate_report_daily(credentials_path):
    app_package_name = os.environ.get("APP_PACKAGE", None)
    assert app_package_name is not None

    report = BaseReportingService(credentials_path=credentials_path)
    assert report is not None

    # Set start_date to Yesterday 00:00 and end_date to Yesterday 02:00
    start_date = datetime.datetime.now() - datetime.timedelta(days=6)
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

    end_date = start_date + datetime.timedelta(days=5)

    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")
    print(start_date)
    print(end_date)

    report_data = report.get_anr_rate_report_daily(app_package_name=app_package_name,
                                                   start_time=start_date,
                                                   end_time=end_date)

    assert len(report_data) > 0


def test_crash_rate_report_daily(credentials_path):
    app_package_name = os.environ.get("APP_PACKAGE", None)
    assert app_package_name is not None

    report = BaseReportingService(credentials_path=credentials_path)
    assert report is not None

    # Set start_date to Yesterday 00:00 and end_date to Yesterday 02:00
    start_date = datetime.datetime.now() - datetime.timedelta(days=6)
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

    end_date = start_date + datetime.timedelta(days=5)

    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")
    print(start_date)
    print(end_date)

    report_data = report.get_crash_rate_report_daily(app_package_name=app_package_name,
                                                     start_time=start_date,
                                                     end_time=end_date)

    assert len(report_data) > 0
    print(f'Len: {len(report_data)}')


def test_crash_rate_report_daily_bulk(credentials_path):
    app_package_names = ['com.jura.coloring.page', 'com.dino.spider.master.rope',
                         'com.jura.robot.battle.transformation', 'com.ig.legend.car.racing',
                         'com.dino.toilet.monster.rope', 'com.jura.rolling.ball.balance',
                         'com.ig.robot.car.transformation', 'com.dino.craft.world', 'com.ione.robot.car.transformation',
                         'com.dino.moto.race.master', 'com.jura.robot.car.transformation', 'com.jura.car.crashes',
                         'com.ig.spider.fighting', 'com.ig.gangster.crime', 'com.ig.moto.traffic',
                         'com.cooking.games.fever.girls.city.craze.chef.master.dream.family',
                         'com.zegostudio.match3d.tripletile', 'com.gt.animal.simulator',
                         'tile.sort.triple.match.puzzle', 'com.tile.triple.match.puzzle3d',
                         'tile.match.triple.puzzle.sort.goods', 'com.zegostudio.triplemaster.match3d',
                         'com.jura.coloring.imposter']

    report = BaseReportingService(credentials_path=credentials_path)
    assert report is not None

    # Set start_date to Yesterday 00:00 and end_date to Yesterday 02:00
    start_date = datetime.datetime.now() - datetime.timedelta(days=15)
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

    end_date = start_date + datetime.timedelta(days=14)

    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")
    print(start_date)
    print(end_date)

    for app_package_name in app_package_names:
        try:
            report_data = report.get_crash_rate_report_daily(app_package_name=app_package_name,
                                                             start_time=start_date,
                                                             end_time=end_date)
            # Appen to log file
            with open('/home/dawn/log.txt', 'a') as f:
                f.write(f'{app_package_name} - {len(report_data)} records\n')
        except Exception as e:
            # Appen to file
            with open('/home/dawn/log.txt', 'a') as f:
                f.write(f'{app_package_name} - {e}\n')
