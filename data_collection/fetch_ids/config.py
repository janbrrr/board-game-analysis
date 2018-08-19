# Args: {page}, {start_year}, {end_year}, {min_voters}
# Does not include expansions!
ROOT_URL = "https://boardgamegeek.com/search/boardgame/page/{" \
           "page}?advsearch=1&q=&include%5Bdesignerid%5D=&include%5Bpublisherid%5D=&geekitemname=&range" \
           "%5Byearpublished%5D%5Bmin%5D={start_year}&range%5Byearpublished%5D%5Bmax%5D={" \
           "end_year}&range%5Bminage%5D%5Bmax%5D=&range%5Bnumvoters%5D%5Bmin%5D={" \
           "min_voters}&range%5Bnumweights%5D%5Bmin%5D=&range%5Bminplayers%5D%5Bmax%5D=&range%5Bmaxplayers%5D%5Bmin" \
           "%5D=&range%5Bleastplaytime%5D%5Bmin%5D=&range%5Bplaytime%5D%5Bmax%5D=&floatrange%5Bavgrating%5D%5Bmin%5D" \
           "=&floatrange%5Bavgrating%5D%5Bmax%5D=&floatrange%5Bavgweight%5D%5Bmin%5D=&floatrange%5Bavgweight%5D%5Bmax" \
           "%5D=&colfiltertype=&searchuser=&nosubtypes%5B0%5D=boardgameexpansion&playerrangetype=normal&B1=Submit "

ENTRY_URL_PATTERN_GET_ID = r'\/boardgame\/(\d+)\/.*'

MIN_VOTERS = 20

MAX_PAGES = 50  # BGG only allows up to 50 pages, if more are required the search was too broad!