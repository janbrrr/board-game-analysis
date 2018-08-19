import requests
import time

from data_collection.common.exceptions import DownloadFailedException

RETRY_DELAY_IN_SECONDS = 5
RETRY_DELAY_AFTER_DISCONNECT_IN_SECONDS = 30


class PageRequest:

    def request(self, url, **kwargs):
        try:
            result = requests.get(url)
        except:
            print("ERROR: Failed to download url={0}. Retrying in {1} seconds...".format(url, RETRY_DELAY_AFTER_DISCONNECT_IN_SECONDS))
            time.sleep(RETRY_DELAY_AFTER_DISCONNECT_IN_SECONDS)
            return self.request(url, **kwargs)
        if result.status_code == 429:
            print("WARNING: Too many requests (code=429)! Retrying in {0} seconds... For more information see below.".format(RETRY_DELAY_IN_SECONDS))
            print("(" + self._get_default_message(result.status_code, **kwargs) + ")")
            time.sleep(RETRY_DELAY_IN_SECONDS)
            return self.request(url, **kwargs)
        elif result.status_code != 200:
            raise DownloadFailedException(self._get_default_message(result.status_code, **kwargs))
        return result

    def _get_default_message(self, status_code, **kwargs):
        message = "status_code={0}".format(status_code)
        for key, value in kwargs.items():
            message += ", {0}={1}".format(key, value)
        return message
