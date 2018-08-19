import xml.etree.ElementTree as etree
from collections import namedtuple

from data_collection.common.page_request import PageRequest
from data_collection.fetch_data.exceptions import CouldNotFindPlayerCountPollException, \
    IllegalPlayerCountFormatException, CouldNotFindNameException

# SimpleContainer is used for Category, Mechanic, Family, Designer, Artist, Publisher
SimpleContainer = namedtuple("SimpleContainer", ["bgg_id", "name"])
RankingContainer = namedtuple("Ranking", ["bgg_id", "name", "rank", "geek_rating"])
PlayerCountContainer = namedtuple("PlayerCount", ["player_count", "num_best", "num_recommended", "num_not_recommended"])
BoardGameContainer = namedtuple("BoardGame", ["bgg_id", "thumbnail_url", "image_url", "name", "description",
                                              "year_published", "min_players", "max_players", "playtime",
                                              "min_playtime", "max_playtime", "min_age", "num_ratings",
                                              "avg_rating", "num_owning", "num_trading", "num_wanting",
                                              "num_wishing", "num_weights", "avg_weight", "category_list",
                                              "mechanic_list", "family_list", "designer_list", "artist_list",
                                              "publisher_list", "ranking_list", "player_count_list"])


class BoardGamePageRequest(PageRequest):

    def get_boardgames(self, game_id_list):
        id_list = ""
        for index, item in enumerate(game_id_list):
            if index != len(game_id_list)-1:
                id_list += str(item)+","
            else:
                id_list += str(item)

        url = "https://www.boardgamegeek.com/xmlapi2/thing?id={0}&stats=1".format(id_list)
        result = self.request(url, sender="BoardGamePageRequest", game_id_list=game_id_list)
        root = etree.fromstring(result.text)

        boardgame_container_list = []
        for item_root in root:
            game_id = int(item_root.get("id"))
            try:
                thumbnail_url = self._get_or_get_none(item_root.find("thumbnail"))
                image_url = self._get_or_get_none(item_root.find("image"))

                name = self._get_name(item_root)

                description = item_root.find("description").text or ""
                year_published = int(item_root.find("yearpublished").get("value"))
                min_players = int(item_root.find("minplayers").get("value"))
                max_players = int(item_root.find("maxplayers").get("value"))
                playtime = int(item_root.find("playingtime").get("value"))
                min_playtime = int(item_root.find("minplaytime").get("value"))
                max_playtime = int(item_root.find("maxplaytime").get("value"))
                min_age = int(item_root.find("minage").get("value"))

                category_list = self._get_simple_list(item_root, type_value="boardgamecategory")
                mechanic_list = self._get_simple_list(item_root, type_value="boardgamemechanic")
                family_list = self._get_simple_list(item_root, type_value="boardgamefamily")
                designer_list = self._get_simple_list(item_root, type_value="boardgamedesigner")
                artist_list = self._get_simple_list(item_root, type_value="boardgameartist")
                publisher_list = self._get_simple_list(item_root, type_value="boardgamepublisher")

                player_count_list = self._get_player_count_list(item_root)

                ratings_root = item_root.find("statistics").find("ratings")
                num_ratings = int(ratings_root.find("usersrated").get("value"))
                avg_rating = float(ratings_root.find("average").get("value"))
                num_owning = int(ratings_root.find("owned").get("value"))
                num_trading = int(ratings_root.find("trading").get("value"))
                num_wanting = int(ratings_root.find("wanting").get("value"))
                num_wishing = int(ratings_root.find("wishing").get("value"))
                num_weights = int(ratings_root.find("numweights").get("value"))
                avg_weight = float(ratings_root.find("averageweight").get("value"))

                ranking_list = self._get_ranking_list(ratings_root)

                boardgame = BoardGameContainer(bgg_id=game_id, thumbnail_url=thumbnail_url, image_url=image_url, name=name,
                                               description=description, year_published=year_published, min_players=min_players,
                                               max_players=max_players, playtime=playtime, min_playtime=min_playtime,
                                               max_playtime=max_playtime, min_age=min_age, num_ratings=num_ratings,
                                               avg_rating=avg_rating, num_owning=num_owning, num_trading=num_trading,
                                               num_wanting=num_wanting, num_wishing=num_wishing, num_weights=num_weights,
                                               avg_weight=avg_weight, category_list=category_list, mechanic_list=mechanic_list,
                                               family_list=family_list, designer_list=designer_list, artist_list=artist_list,
                                               publisher_list=publisher_list, ranking_list=ranking_list,
                                               player_count_list=player_count_list)
                boardgame_container_list.append(boardgame)
            except Exception as e:
                print("ERROR: Unexpected error for game_id={0}".format(game_id))
                raise
        return boardgame_container_list

    def _get_or_get_none(self, node):
        return node.text if node is not None else None

    def _get_name(self, xml_root):
        name_nodes = xml_root.findall("name")
        for name_node in name_nodes:
            if name_node.get("type") == "primary":
                name = name_node.get("value")
                return name
        raise CouldNotFindNameException()

    def _get_simple_list(self, xml_root, type_value):
        nodes = xml_root.findall('.//link[@type="{0}"]'.format(type_value))
        simple_list = []
        for simple in nodes:
            simple_bgg_id = int(simple.get("id"))
            simple_name = simple.get("value")
            simple_list.append(SimpleContainer(bgg_id=simple_bgg_id, name=simple_name))
        return simple_list

    def _get_player_count_list(self, xml_root):
        poll_roots = xml_root.findall("poll")
        player_count_poll = None
        for poll in poll_roots:
            if poll.get("name") == "suggested_numplayers":
                player_count_poll = poll
                break

        if player_count_poll is None:
            raise CouldNotFindPlayerCountPollException()

        if player_count_poll.get("totalvotes") == 0:
            return []

        player_count_list = []
        for results in player_count_poll.findall("results"):
            player_count = results.get("numplayers")
            num_best = 0
            num_recommended = 0
            num_not_recommended = 0
            for result in results.findall("result"):
                result_type = result.get("value")
                result_votes = int(result.get("numvotes"))
                if result_type == "Best":
                    num_best = result_votes
                elif result_type == "Recommended":
                    num_recommended = result_votes
                elif result_type == "Not Recommended":
                    num_not_recommended = result_votes
                else:
                    raise IllegalPlayerCountFormatException()
            player_count_list.append(PlayerCountContainer(player_count=player_count, num_best=num_best,
                                                          num_recommended=num_recommended,
                                                          num_not_recommended=num_not_recommended))
        return player_count_list

    def _get_ranking_list(self, xml_ratings_root):
        ranking_list = []
        for rank in xml_ratings_root.find("ranks"):
            rank_bgg_id = int(rank.get("id"))
            rank_name = rank.get("friendlyname")
            try:
                rank_rank = int(rank.get("value"))
            except ValueError:
                rank_rank = None
            try:
                rank_geek_rating = float(rank.get("bayesaverage"))
            except ValueError:
                rank_geek_rating = None
            ranking_obj = RankingContainer(bgg_id=rank_bgg_id, name=rank_name, rank=rank_rank, geek_rating=rank_geek_rating)
            ranking_list.append(ranking_obj)
        return ranking_list


if __name__ == "__main__":
    bg_id = 174430
    boardgames = BoardGamePageRequest().get_boardgames([174430, 215, 173])
    for boardgame in boardgames:
        print(boardgame)
