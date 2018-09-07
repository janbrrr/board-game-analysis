import pandas as pd
import time
from sqlalchemy import create_engine
from multiprocessing.pool import Pool


def calculate_edges(arguments):
    edge_weight_threshold = 75
    print_every_x_steps = 100

    process_id = arguments[0]
    boardgame_ids = arguments[1]

    # Load DataFrames
    engine = create_engine("sqlite:///../data/database/data_2018-05-10.db")
    boardgames_df = pd.read_sql(
        "select id as boardgame_id, bgg_id, name, year_published, avg_rating, num_ratings, avg_weight, num_weights from boardgames;",
        engine)
    boardgames_df = boardgames_df.set_index("boardgame_id")
    categories_to_boardgames_df = pd.read_sql("select category_id, boardgame_id from categories_to_boardgames;", engine)
    mechanics_to_boardgames_df = pd.read_sql("select mechanic_id, boardgame_id from mechanics_to_boardgames;", engine)

    # Cache dictionaries containing mechanics and categories for each board game
    categories_dict = {}
    mechanics_dict = {}
    for boardgame_id in boardgames_df.index:
        this_categories = categories_to_boardgames_df[
            categories_to_boardgames_df["boardgame_id"] == boardgame_id].set_index("category_id")
        this_mechanics = mechanics_to_boardgames_df[
            mechanics_to_boardgames_df["boardgame_id"] == boardgame_id].set_index("mechanic_id")

        categories_dict[boardgame_id] = this_categories
        mechanics_dict[boardgame_id] = this_mechanics

    # Calculate the edge weights
    weighted_edges_list = []
    count = 0
    start_time = time.time()
    for boardgame_id in boardgame_ids:

        this_categories = categories_dict[boardgame_id]
        this_mechanics = mechanics_dict[boardgame_id]

        remaining_boardgame_ids = boardgames_df[boardgames_df.index > boardgame_id].index

        for partner_id in remaining_boardgame_ids:

            partner_categories = categories_dict[partner_id]
            partner_mechanics = mechanics_dict[partner_id]

            category_overlap = len(this_categories.index.intersection(partner_categories.index))
            mechanic_overlap = len(this_mechanics.index.intersection(partner_mechanics.index))

            if (len(this_categories) + len(this_mechanics)) == 0 or (len(partner_categories) + len(partner_mechanics)) == 0:
                total_similarity = 0
            else:
                similarity_this_perspective = (category_overlap + mechanic_overlap) / (len(this_categories)+len(this_mechanics)) * 100
                similarity_partner_perspective = (category_overlap + mechanic_overlap) / (len(partner_categories)+len(partner_mechanics)) * 100
                total_similarity = similarity_this_perspective + similarity_partner_perspective

            edge_weight = total_similarity

            if edge_weight >= edge_weight_threshold:
                weighted_edges_list.append([boardgame_id, partner_id, edge_weight])

        count += 1
        if count % print_every_x_steps == 0:
            print("{0} | Processed {1}/{2} ({3})".format(process_id, count, len(boardgame_ids), time.time() - start_time))
            start_time = time.time()
    return weighted_edges_list


def filter_edge_list(engine, all_edges_filename, filename, keep_percentage=0.20):
    boardgames_df = pd.read_sql(
        "select id as boardgame_id, bgg_id, name, year_published, avg_rating, num_ratings, avg_weight, num_weights from boardgames;",
        engine)
    boardgames_df = boardgames_df.set_index("boardgame_id")
    all_edges_df = pd.read_csv(all_edges_filename, sep=";")

    potential_removable_edges = set()
    edges_to_keep = set()
    for boardgame_id in boardgames_df.index:
        source_edges_df = all_edges_df[all_edges_df["Source"] == boardgame_id]
        target_edges_df = all_edges_df[all_edges_df["Target"] == boardgame_id]
        boardgame_edges_df = pd.concat([source_edges_df, target_edges_df]).sort_values("Weight", ascending=False)

        number_of_edges = len(boardgame_edges_df)
        end_index = int(number_of_edges * keep_percentage)
        edges_keeping_df = boardgame_edges_df.iloc[0:end_index]

        # Remove from the removable set
        for index_to_keep in edges_keeping_df.index:
            if index_to_keep in potential_removable_edges:
                potential_removable_edges.remove(index_to_keep)
            if index_to_keep not in edges_to_keep:
                edges_to_keep.add(index_to_keep)

        # Add rest to the removable set if not in set containing the keepings
        for index_to_remove in boardgame_edges_df.iloc[end_index:].index:
            if index_to_remove not in potential_removable_edges and index_to_remove not in edges_to_keep:
                potential_removable_edges.add(index_to_remove)

    important_edges_df = all_edges_df[~all_edges_df.index.isin(potential_removable_edges)]
    important_edges_df = important_edges_df.sort_values("Weight", ascending=False)

    important_edges_df.to_csv(filename, sep=";", index=False)


def create_node_list(engine, filename):
    boardgames_to_csv_df = pd.read_sql(
        "select id as boardgame_id, bgg_id, name, year_published, avg_rating, num_ratings, avg_weight, num_weights from boardgames;",
        engine)
    boardgames_to_csv_df = boardgames_to_csv_df[
        ["boardgame_id", "name", "bgg_id"] + boardgames_to_csv_df.columns.tolist()[3:]]
    boardgames_to_csv_df.columns = ["id", "label"] + boardgames_to_csv_df.columns.tolist()[2:]
    boardgames_to_csv_df.to_csv(filename, sep=";", index=False)


if __name__ == "__main__":
    engine = create_engine("sqlite:///../data/database/data_2018-05-10.db")

    NUM_PROCESSES = 14

    args = [
        [i, []] for i in range(NUM_PROCESSES)
    ]

    # Load Balancing
    boardgames_df = pd.read_sql(
        "select id as boardgame_id, bgg_id, name, year_published, avg_rating, num_ratings, avg_weight, num_weights from boardgames;",
        engine)
    boardgames_df = boardgames_df.set_index("boardgame_id")
    board_game_count = len(boardgames_df.index)
    for i in range(0, board_game_count, NUM_PROCESSES):
        for process_index in range(NUM_PROCESSES):
            if (i+process_index) < board_game_count:
                args[process_index][1].append(boardgames_df.index[i+process_index])

    pool = Pool(processes=NUM_PROCESSES)

    start = time.time()
    all_weighted_edges_list = []
    for result in pool.imap(calculate_edges, args):
        all_weighted_edges_list += result
    print("Took {0} seconds".format(time.time() - start))
    print("Found {} edges.".format(len(all_weighted_edges_list)))

    all_edges_df = pd.DataFrame(all_weighted_edges_list, columns=["Source", "Target", "Weight"])
    all_edges_df.to_csv("data/board_games_all_edges.csv", sep=";", index=False)

    print("\nStarted to filter edges...")
    start = time.time()
    filter_edge_list(engine, "data/board_games_all_edges.csv", "data/board_games_20p_edges.csv", keep_percentage=0.20)
    print("Took {0} seconds".format(time.time() - start))

    create_node_list(engine, "data/board_games_nodes.csv")
