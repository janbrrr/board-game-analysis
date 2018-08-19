import json
from data_collection.common.page_request import PageRequest
from data_collection.fetch_data.exceptions import IllegalRatingKeysException


class RatingsPageRequest(PageRequest):

    def get_ratings_breakdown(self, game_id):
        ratings_url = "https://boardgamegeek.com/api/collectionstatsgraph?objectid={0}&objecttype=thing&type=BarChart".\
            format(game_id)

        result = self.request(ratings_url, sender="RatingsPageRequest", game_id=game_id)
        json_dict = json.loads(result.text)
        rows = json_dict["data"]["rows"]
        breakdown = {}
        expected_key_set = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
        for row in rows:
            content = row["c"]
            rating = int(content[0]["v"])
            count = int(content[1]["v"])
            if rating in expected_key_set:  # some games have votes for a rating of 0 so this is necessary
                breakdown[rating] = count
        final_key_set = set(breakdown.keys())
        if not final_key_set == expected_key_set:
            raise IllegalRatingKeysException("game_id={0}, keys_found={1}".format(game_id, final_key_set))
        return breakdown


if __name__ == "__main__":

    bg_id = "174430"  # Gloomhaven
    ratings_breakdown = RatingsPageRequest().get_ratings_breakdown(bg_id)
    for rating in range(1, 11):
        print("{0} - {1}".format(rating, ratings_breakdown[rating]))
