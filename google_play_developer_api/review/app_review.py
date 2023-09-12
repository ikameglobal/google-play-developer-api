import logging
import time
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class ReviewService:
    def __init__(self, credentials_path: str):
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=["https://www.googleapis.com/auth/androidpublisher"]
        )
        self._service = build(serviceName="androidpublisher",
                              version="v3",
                              credentials=credentials,
                              cache_discovery=False)

    def get(
        self,
        app_package_name: str = "",
        max_results: int = 1000,
        retry_count: int = 3,
        sleep_time: int = 15,
    ) -> list[dict]:
        # GET DATA
        token = ""
        reviews_list = []
        count = 0
        while True:
            for i in range(retry_count):
                try:
                    report = self._service.reviews().list(packageName=app_package_name,
                                                          token=token,
                                                          maxResults=max_results,
                                                          translationLanguage='en').execute()
                    break
                except HttpError as e:
                    if e.resp.status == 403:
                        logging.warning(f'Permission denied for {app_package_name}')
                    elif e.resp.status == 400:
                        raise Exception(f'Bad request for {app_package_name}, {e.reason}')
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

            reviews_list.extend(report.get("reviews", []))
            token_pagination = report.get("tokenPagination", {})
            token = token_pagination.get("nextPageToken", "")
            print(f'Batch {count + 1}: {len(report.get("reviews", []))} reviews')
            count += 1
            if not token:
                break

        return reviews_list


if __name__ == '__main__':
    service = ReviewService(credentials_path='/home/dawn/work/.secrets/ikame_game_google_play_developer_report.json')
    data = service.get(app_package_name='com.citybay.farming.citybuilding')
    print(f'Total reviews: {len(data)}')
    print('------------------------------------------\n')
    print(data[0])
