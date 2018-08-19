import xml.etree.ElementTree as etree

import xml
import re

from data_collection.common.page_request import PageRequest


class TotalPlaysPageRequest(PageRequest):

    def get_total_plays(self, game_id):
        url = "https://www.boardgamegeek.com/xmlapi2/plays?id={0}".format(game_id)

        result = self.request(url, sender="TotalPlaysPageRequest", game_id=game_id)
        try:
            root = etree.fromstring(result.text)
            total_plays = int(root.attrib["total"])
            return total_plays
        except xml.etree.ElementTree.ParseError:  # Some entries fail parsing (e.g. id=196217)
            total_plays_pattern = r'<plays total="(\d+)" page="1" termsofuse="[^"]+">'
            total_plays_regex = re.compile(total_plays_pattern)
            match = total_plays_regex.search(result.text)
            total_plays = int(match[1])
            return total_plays
        except:
            print("ERROR: Could not download the total_plays for game_id={0}".format(game_id))
            raise


if __name__ == "__main__":
    bg_id = 174430
    plays = TotalPlaysPageRequest().get_total_plays(bg_id)
    print(plays)
