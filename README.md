# Analyzing the Data on BoardGameGeek

## Introduction

This project is about analyzing the data on board games available on [BoardGameGeek](https://boardgamegeek.com/).

The analysis is divided into three parts and there is (will be) a short post on my blog for every one of them.
* [Growth over Time and Kickstarter](#part_one)
* TBD
* TBD

## Collecting the Data

At the time of the collection (May 2018) there is no way to download the data for all board games at once. 
When using the [API](https://boardgamegeek.com/wiki/page/BGG_XML_API2) of BoardGameGeek we have to specify the board games we want to gather data on.
So the first step is to create a list of all board games that we want to gather data on.

We can create such a list by making use of the [Advanced Search](https://boardgamegeek.com/advsearch/boardgame) on BGG. 
This search is able to return a list of all board games that satisfy our search criteria, but it is limited to 50 pages of results so we cannot retrieve all at once and have to apply filters such that the results do not reach 50 pages.
We can achieve this by searching on a year by year basis or at most include two years at once. 

Before we start, we can define search parameters to filter the board games we want data on. 
In this case we require board games to have at least 20 votes regarding the rating or we will not include it. 
This is to exclude homebrew games, unreleased and unknown games. Basically to make the numbers more manageable while losing not much information.

So we will download the results of the Advanced Search for every year of interest (1990 to 2018) and we store the IDs of the board games in a file.
Later on we can iterate through this file (i.e., every board game ID) to download all the data via the API.

The first step in collecting is to create the list of board game ids to download data on.
This is done with the `fetch_board_game_ids.py` script where only `START_YEAR` and `END_YEAR` have to be specified.
The script will basically enter two years at a time into the advanced search along with the parameters and store all the resulting board game ids in a file.
For more information see `data_collection/fetch_ids`.

The communication with the BGG API is handled in `data_collection/fetch_data`.
In there `boardgames.py` is the API access point for general information on a given board game id,
`plays.py` returns the total number of plays for a given board game id (this information is already used in `boardgames.py`) and `ratings.py` returns the ratings breakdown
of a board game id. The ratings breakdown is a list of number of votes for 10 points, the number of votes for 9 points, and so on. Basically the data of the histogram on any ratings page of any board game 
(e.g., https://boardgamegeek.com/boardgame/174430/gloomhaven/ratings) .

The actual download and storage in the database is done with the script `download_board_game_database.py` and it makes use of the functions mentioned above.
Warning, the download is very slow due to the rate limitations (and maybe due to the implementation).

## Storing the Data

The data is being stored in a *SQLite* database. The database I used is located in `data/database/data_2018-05-10.db` and it is based
on the list of ids located in `data/ids/ids_1990-to-2018_min-20_2018-05-07`.

Here are examples of the tables that are being used:
- `boardgames`: id on BGG, name, year, rating, weight, #votes, #plays, etc.
- `categories`: id on BGG, name
- `categories_to_boardgames`: N:M relation of categories and boardgames
- `mechanics`: id on BGG, name
- `mechanics_to_boardgames` : N:M relation of mechanics and boardgames
- and some more, but the above are the most important ones

For more information either refer to `data_collection/database/tables.py` or `database_schema.png`.

## <a name="part_one"></a>Part One - Growth over Time and Kickstarter

*The corresponding blog post is available [here](https://janbarrera.com/blog/post/board-game-analysis-part-1/)*.

The first part is divided into the following topics:
1. The Rise of Board Games
2. The Influence of Kickstarter
3. The Categories of the Board Games on Kickstarter
4. Are the Board Games on Kickstarter better?

For every topic, there is corresponding Jupyter Notebook in `part_one/`.

## Special Thanks

Special thanks to *Alex Olteanu* who wrote a [tutorial](https://www.dataquest.io/blog/making-538-plots/) on creating graphs in the style of [FiveThirtyEight](https://fivethirtyeight.com/) at [Dataquest](https://www.dataquest.io/).
The plots created in this work are based on his work.

