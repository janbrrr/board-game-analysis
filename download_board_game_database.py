import time

from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker
from collections import namedtuple

from data_collection.fetch_data.boardgames import BoardGamePageRequest
from data_collection.fetch_data.plays import TotalPlaysPageRequest
from data_collection.fetch_data.ratings import RatingsPageRequest
from data_collection.database.tables import *
from data_collection.database.utils import get_or_create
from data_collection.fetch_ids.file_parsing import CSVReader

SUCCESS = 1
ERROR = 0
EXISTS = 2


def download_data(game_id_list, url_dict, session):
    boardgame_list = BoardGamePageRequest().get_boardgames(game_id_list)

    status_dict = {}
    for bg in boardgame_list:
        game_id = bg.bgg_id

        if session.query(exists().where(BoardGame.bgg_id == game_id)).scalar():
            status_dict[game_id] = EXISTS
            continue

        total_plays = TotalPlaysPageRequest().get_total_plays(game_id)
        ratings_dict = RatingsPageRequest().get_ratings_breakdown(game_id)

        boardgame = BoardGame(bgg_id=game_id, url=url_dict[game_id], thumbnail_url=bg.thumbnail_url,
                              image_url=bg.image_url, name=bg.name,
                              description=bg.description, year_published=bg.year_published, min_players=bg.min_players,
                              max_players=bg.max_players, playtime=bg.playtime, min_playtime=bg.min_playtime,
                              max_playtime=bg.max_playtime, min_age=bg.min_age, num_ratings=bg.num_ratings,
                              avg_rating=bg.avg_rating, num_owning=bg.num_owning, num_trading=bg.num_trading,
                              num_wanting=bg.num_wanting, num_wishing=bg.num_wishing, num_weights=bg.num_weights,
                              avg_weight=bg.avg_weight, total_plays=total_plays)
        session.add(boardgame)
        session.flush()

        category_list = bg.category_list
        for element in category_list:
            category, created = get_or_create(session, Category, bgg_id=element.bgg_id, name=element.name)
            category_to_boardgame = CategoryToBoardGame(category_id=category.id, boardgame_id=boardgame.id)
            session.add(category_to_boardgame)

        mechanic_list = bg.mechanic_list
        for element in mechanic_list:
            mechanic, created = get_or_create(session, Mechanic, bgg_id=element.bgg_id, name=element.name)
            mechanic_to_boardgame = MechanicToBoardGame(mechanic_id=mechanic.id, boardgame_id=boardgame.id)
            session.add(mechanic_to_boardgame)

        family_list = bg.family_list
        for element in family_list:
            family, created = get_or_create(session, Family, bgg_id=element.bgg_id, name=element.name)
            family_to_boardgame = FamilyToBoardGame(family_id=family.id, boardgame_id=boardgame.id)
            session.add(family_to_boardgame)

        designer_list = bg.designer_list
        for element in designer_list:
            designer, created = get_or_create(session, Designer, bgg_id=element.bgg_id, name=element.name)
            designer_to_boardgame = DesignerToBoardGame(designer_id=designer.id, boardgame_id=boardgame.id)
            session.add(designer_to_boardgame)

        artist_list = bg.artist_list
        for element in artist_list:
            artist, created = get_or_create(session, Designer, bgg_id=element.bgg_id, name=element.name)
            artist_to_boardgame = ArtistToBoardGame(artist_id=artist.id, boardgame_id=boardgame.id)
            session.add(artist_to_boardgame)

        publisher_list = bg.publisher_list
        for element in publisher_list:
            publisher, created = get_or_create(session, Publisher, bgg_id=element.bgg_id, name=element.name)
            publisher_to_boardgame = PublisherToBoardGame(publisher_id=publisher.id, boardgame_id=boardgame.id)
            session.add(publisher_to_boardgame)

        player_count_list = bg.player_count_list
        for element in player_count_list:
            player_count_to_boardgame = PlayerCountToBoardGame(boardgame_id=boardgame.id, player_count=element.player_count,
                                                               num_best=element.num_best,
                                                               num_recommended=element.num_recommended,
                                                               num_not_recommended=element.num_not_recommended)
            session.add(player_count_to_boardgame)

        ranking_list = bg.ranking_list
        for element in ranking_list:
            ranktype, created = get_or_create(session, RankType, bgg_id=element.bgg_id, name=element.name)
            boardgame_ranking = BoardGameRanking(boardgame_id=boardgame.id, ranktype_id=ranktype.id, rank=element.rank,
                                                 geek_rating=element.geek_rating)
            session.add(boardgame_ranking)

        ratings_breakdown = RatingsBreakdown(boardgame_id=boardgame.id, num_10=ratings_dict[10], num_9=ratings_dict[9],
                                             num_8=ratings_dict[8], num_7=ratings_dict[7], num_6=ratings_dict[6],
                                             num_5=ratings_dict[5], num_4=ratings_dict[4], num_3=ratings_dict[3],
                                             num_2=ratings_dict[2], num_1=ratings_dict[1])
        session.add(ratings_breakdown)

        try:
            session.commit()
            status_dict[game_id] = SUCCESS
        except Exception as e:
            session.rollback()
            status_dict[game_id] = ERROR
        time.sleep(0.5)
    return status_dict


if __name__ == "__main__":
    DATABASE_NAME = "test.db"

    Entry = namedtuple("Entry", ["id", "name", "url"])

    entries = CSVReader().read(file_path="data/ids/ids_1990-to-2018_min-20_2018-05-07.csv")

    engine = create_engine("sqlite:///data/database/{0}".format(DATABASE_NAME))
    create_all_tables(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    size = len(entries)
    progress = 0  # also the start index
    step_size = 15
    print("Starting!\n")
    print("Progress: {0}/{1}".format(progress, size))
    for start_index in range(progress, len(entries), step_size):
        start_time = time.time()
        end_index = start_index + step_size if start_index + step_size <= len(entries) else len(entries)
        entries_subset = entries[start_index:end_index]

        id_list = [entry.id for entry in entries_subset]
        url_dict = {entry.id: entry.url for entry in entries_subset}

        status_dict = download_data(id_list, url_dict, session)
        for key, status in status_dict.items():
            if status == SUCCESS:
                print("\tSuccessfully added {:7d} to the database!".format(key))
            elif status == ERROR:
                print("\tERROR: Failed to add {:7d} to the database!".format(key))
            elif status == EXISTS:
                print("\tSkipped {:7d}, already exists!".format(key))
            else:
                print("\tWARNING: Unknown status for {0}!".format(key))
        print("Step took {0} seconds (size of {1})".format(time.time() - start_time, step_size))
        progress += (end_index - start_index)
        print("Progress: {0}/{1}".format(progress, size))

    print("\nDone!")
    session.close()
