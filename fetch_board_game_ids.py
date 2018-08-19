from collections import namedtuple

import datetime
import time
import re
import os

from bs4 import BeautifulSoup

from data_collection.common.page_request import PageRequest
from data_collection.fetch_ids.config import ROOT_URL, ENTRY_URL_PATTERN_GET_ID, MIN_VOTERS, MAX_PAGES
from data_collection.fetch_ids.file_parsing import CSVWriter
from data_collection.fetch_ids.exceptions import NoEntriesFoundException, TooManyPagesException


class BoardGameIdsPageRequest(PageRequest):

    def download_ids(self, page, start_year, end_year, filename):
        url = ROOT_URL.format(page=page, start_year=start_year, end_year=end_year, min_voters=MIN_VOTERS)
        entry_id_regex = re.compile(ENTRY_URL_PATTERN_GET_ID)

        if page == MAX_PAGES + 1:
            raise TooManyPagesException()

        result = self.request(url, sender="BoardGameIdsPageRequest", page=page, start_year=start_year, end_year=end_year, filename=filename)
        soup = BeautifulSoup(result.text, "html.parser")

        entries = soup.find_all("tr", id="row_")
        if len(entries) == 0:
            raise NoEntriesFoundException()

        data = []
        for index, entry in enumerate(entries):
            try:
                a_tag = entry.find("td", class_="collection_objectname").find("a")
                name = a_tag.get_text()
                link = a_tag.get("href")
                match = entry_id_regex.search(str(link))
                game_id = match[1]
                data.append([game_id, name, str(link)])
            except Exception:
                print("ERROR: skipped entry no. {0} at page {1} from={2} to={3}".format(index, page, start_year, end_year))
                continue

        download_directory = os.path.join("data", "ids")
        CSVWriter(directory=download_directory).write(filename, data)


if __name__ == "__main__":
    START_YEAR = 1990
    END_YEAR = 2018
    TODAY = datetime.datetime.today().strftime('%Y-%m-%d')
    FILENAME = "ids_{0}-to-{1}_min-{2}_{3}.csv".format(START_YEAR, END_YEAR, MIN_VOTERS, TODAY)

    DateRange = namedtuple('DateRange', ['start', 'end'])
    ranges_to_download = []

    # Download two years at a time
    for starting_year in range(START_YEAR, END_YEAR+1, 2):
        ending_year = starting_year + 1 if starting_year + 1 <= END_YEAR else starting_year
        ranges_to_download.append(
            DateRange(start=starting_year, end=ending_year)
        )

    print("Starting!")
    print("Filename: {0}".format(FILENAME))
    for date_range in ranges_to_download:
        print("\nDateRange from={0} to={1}".format(date_range.start, date_range.end))
        for page_number in range(1, MAX_PAGES+1):
            try:
                BoardGameIdsPageRequest().download_ids(page_number, date_range.start, date_range.end, FILENAME)
                print("\tPage {0} successful!".format(page_number))
                time.sleep(1)
            except NoEntriesFoundException:
                break
    print("\nDone!")