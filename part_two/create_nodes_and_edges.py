import pandas as pd
import numpy as np


def create_node_list(engine, filename):
    """
    Creates a ``DataFrame`` of all categories based on the database and computes some additional properties
    like ``avg_rating``, ``avg_weight`` and the weighted versions of them.

    This ``DataFrame`` will then be exported as a ``.csv`` file that can then be imported into ``Gephi``
    as a node list.

    :param engine: the database engine
    :param filename: the filename where the node list should be stored
    """
    select_board_games_sql = "select id as boardgame_id, avg_rating, num_ratings, avg_weight, num_weights from boardgames;"
    boardgames_df = pd.read_sql(select_board_games_sql, engine)

    select_categories_to_board_games_sql = "select category_id, boardgame_id from categories_to_boardgames;"
    categories_to_boardgames_df = pd.read_sql(select_categories_to_board_games_sql, engine)

    categories_to_boardgames_df = categories_to_boardgames_df.join(boardgames_df.set_index("boardgame_id"),
                                                                   on="boardgame_id")

    select_categories_sql = "select id, name as label from categories;"
    result_df = pd.read_sql(select_categories_sql, engine).set_index("id")

    games_per_category_sql = "select category_id as id, count(*) as count from categories_to_boardgames " \
                             "group by category_id;"
    category_games_count_df = pd.read_sql(games_per_category_sql, engine).set_index("id")
    result_df = result_df.join(category_games_count_df)

    result_df["avg_rating"] = categories_to_boardgames_df.groupby("category_id")["avg_rating"].mean()
    result_df["norm_avg_rating"] = (result_df["avg_rating"] - result_df["avg_rating"].mean()).div(
        result_df["avg_rating"].std())

    result_df["avg_weight"] = categories_to_boardgames_df.groupby("category_id")["avg_weight"].mean()
    result_df["norm_avg_weight"] = (result_df["avg_weight"] - result_df["avg_weight"].mean()).div(
        result_df["avg_weight"].std())

    # Weighted average ratings
    num_ratings_sum_per_category = categories_to_boardgames_df.groupby("category_id")["num_ratings"].sum()
    categories_to_boardgames_df["weighted_avg_rating"] = categories_to_boardgames_df["avg_rating"].mul(
        categories_to_boardgames_df["num_ratings"])
    result_df["weighted_avg_rating"] = categories_to_boardgames_df.groupby("category_id")[
        "weighted_avg_rating"].sum().div(num_ratings_sum_per_category)

    result_df["norm_weighted_avg_rating"] = (
        result_df["weighted_avg_rating"] - result_df["weighted_avg_rating"].mean()).div(
        result_df["weighted_avg_rating"].std())

    # Weighted average weights
    num_weights_sum_per_category = categories_to_boardgames_df.groupby("category_id")["num_weights"].sum()
    categories_to_boardgames_df["weighted_avg_weight"] = categories_to_boardgames_df["avg_weight"].mul(
        categories_to_boardgames_df["num_weights"])
    result_df["weighted_avg_weight"] = categories_to_boardgames_df.groupby("category_id")[
        "weighted_avg_weight"].sum().div(num_weights_sum_per_category)

    result_df["norm_weighted_avg_weight"] = (
        result_df["weighted_avg_weight"] - result_df["weighted_avg_weight"].mean()).div(
        result_df["weighted_avg_weight"].std())

    result_df.to_csv(filename, sep=";")


def create_edge_list(engine, filename, keep_percentage=0.2):
    """
    Creates a ``DataFrame`` of the most important edges between the categories based on the database.
    Only keeps the X% most important edges for each category, specified by ``keep_percentage``.

    The weight for an edge between two categories c_0 and c_1 is calculated as follows:
    - First calculate the overlap from the perspective of c_0:
      -> (number of games with c_0 and c_1) / (number of games with c_0) * 100
    - Then calculate the overlap from the perspective of c_1:
      -> (number of games with c_0 and c_1) / (number of games with c_1) * 100
    - The final edge weight is simply the sum of both, meaning the maximum value is 200.

    This ``DataFrame`` will then be exported as a ``.csv`` file that can then be imported into ``Gephi``
    as an edge list.

    :param engine: the database engine
    :param filename: the filename where the edge list should be stored
    :param keep_percentage: only keep the X% most important edges for each
    """
    select_board_games_sql = "select id, name from boardgames;"
    boardgames_df = pd.read_sql(select_board_games_sql, engine)
    select_categories_sql = "select id, name as label from categories;"
    categories_df = pd.read_sql(select_categories_sql, engine).set_index("id")
    select_categories_to_board_games_sql = "select category_id, boardgame_id from categories_to_boardgames;"
    categories_to_boardgames_df = pd.read_sql(select_categories_to_board_games_sql, engine)

    # First we create a list of all edges.
    # We do this by iterating through each board game and we create two edges for each possible combination
    # of the categories associated with the board game (each category is once source and once target).
    edges_list = []
    for boardgame_id in boardgames_df.loc[:, "id"]:
        categories_for_this_boardgame = categories_to_boardgames_df[
            categories_to_boardgames_df["boardgame_id"] == boardgame_id].set_index("category_id")
        number_of_categories = len(categories_for_this_boardgame.index)
        if number_of_categories <= 1:
            continue
        for index, first_category in enumerate(categories_for_this_boardgame.index):
            remaining_categories = categories_for_this_boardgame.index[index+1:]
            for remaining_category in remaining_categories:
                edges_list.append([first_category, remaining_category, boardgame_id])
                edges_list.append([remaining_category, first_category, boardgame_id])
    all_edges_df = pd.DataFrame(edges_list, columns=["Source", "Target", "Boardgame"])

    # Calculate the edge weights.
    processed_categories = set()
    weighted_edges_list = []
    for category_id in categories_df.index:
        other_category_ids = categories_df[categories_df.index != category_id].index
        remaining_category_ids = other_category_ids[~other_category_ids.isin(processed_categories)]

        # number of board games this category appears in
        number_of_connections = all_edges_df[all_edges_df["Source"] == category_id]["Boardgame"].nunique()

        for partner_id in remaining_category_ids:
            number_of_connections_with_partner = np.sum(
                (all_edges_df["Source"] == category_id) & (all_edges_df["Target"] == partner_id))
            percentage_from_source_perspective = number_of_connections_with_partner / number_of_connections * 100

            total_partner_connections = all_edges_df[all_edges_df["Source"] == partner_id]["Boardgame"].nunique()
            number_of_connections_with_source = np.sum(
                (all_edges_df["Source"] == partner_id) & (all_edges_df["Target"] == category_id))
            percentage_from_partner_perspective = number_of_connections_with_source / total_partner_connections * 100

            total_edge_weight = percentage_from_source_perspective + percentage_from_partner_perspective
            weighted_edges_list.append([category_id, partner_id, total_edge_weight])

            processed_categories.add(category_id)
    weighted_edges_df = pd.DataFrame(weighted_edges_list, columns=["Source", "Target", "Weight"])
    weighted_edges_df = weighted_edges_df[weighted_edges_df["Weight"] != 0]

    # Only keep the most important edges for each category and discard the rest
    potential_removable_edges = set()
    edges_to_keep = set()
    for category_id in categories_df.index:
        source_edges_df = weighted_edges_df[weighted_edges_df["Source"] == category_id]
        target_edges_df = weighted_edges_df[weighted_edges_df["Target"] == category_id]
        category_edges_df = pd.concat([source_edges_df, target_edges_df]).sort_values("Weight", ascending=False)

        number_of_edges = len(category_edges_df)
        end_index = int(number_of_edges * keep_percentage)
        edges_keeping_df = category_edges_df.iloc[0:end_index]

        # Remove from Remove-Set
        for index_to_keep in edges_keeping_df.index:
            if index_to_keep in potential_removable_edges:
                potential_removable_edges.remove(index_to_keep)
            if index_to_keep not in edges_to_keep:
                edges_to_keep.add(index_to_keep)

        # Add rest to the Remove-Set if not in Keep-Set
        for index_to_remove in category_edges_df.iloc[end_index:].index:
            if index_to_remove not in potential_removable_edges and index_to_remove not in edges_to_keep:
                potential_removable_edges.add(index_to_remove)

    important_weighted_edges_df = weighted_edges_df[~weighted_edges_df.index.isin(potential_removable_edges)]
    important_weighted_edges_df = important_weighted_edges_df.sort_values("Weight", ascending=False)

    important_weighted_edges_df.set_index("Source").to_csv(filename, sep=";")


if __name__ == "__main__":
    from sqlalchemy import create_engine

    engine = create_engine("sqlite:///../data/database/data_2018-05-10.db")
    create_node_list(engine, "data/nodes_categories_test.csv")
    create_edge_list(engine, "data/edges_20_categories_test.csv", keep_percentage=0.20)
