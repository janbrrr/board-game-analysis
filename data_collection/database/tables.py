from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Sequence, ForeignKey, UniqueConstraint

Base = declarative_base()


def create_all_tables(engine):
    Base.metadata.create_all(engine)


class BoardGame(Base):
    __tablename__ = "boardgames"

    id = Column(Integer, Sequence('boardgame_id_seq'), primary_key=True)
    bgg_id = Column(Integer, unique=True)
    url = Column(String, nullable=False)
    thumbnail_url = Column(String)
    image_url = Column(String)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    year_published = Column(Integer, nullable=False)
    min_players = Column(Integer)
    max_players = Column(Integer)
    playtime = Column(Integer)
    min_playtime = Column(Integer)
    max_playtime = Column(Integer)
    min_age = Column(Integer)
    num_ratings = Column(Integer, nullable=False)
    avg_rating = Column(Float, nullable=False)
    num_owning = Column(Integer, nullable=False)
    num_trading = Column(Integer)
    num_wanting = Column(Integer)
    num_wishing = Column(Integer, nullable=False)
    num_weights = Column(Integer, nullable=False)
    avg_weight = Column(Float, nullable=False)
    total_plays = Column(Integer, nullable=False)

    def __repr__(self):
        return "<BoardGame(name={0}, bgg_id={1})>".format(self.name, self.bgg_id)


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, Sequence('category_id_seq'), primary_key=True)
    bgg_id = Column(Integer, unique=True)
    name = Column(String, nullable=False)

    def __repr__(self):
        return "<Category(name={0}, bgg_id={1})>".format(self.name, self.bgg_id)


class CategoryToBoardGame(Base):
    __tablename__ = "categories_to_boardgames"

    id = Column(Integer, Sequence('category_to_boardgame_id_seq'), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    boardgame_id = Column(Integer, ForeignKey("boardgames.id"), nullable=False)

    __table_args__ = (UniqueConstraint("category_id", "boardgame_id", name="_category_boardgame_uc"),)

    def __repr__(self):
        return "<CategoryToBoardGame(category={0}, boardgame={1})>".format(self.category_id,
                                                                           self.boardgame_id)


class Mechanic(Base):
    __tablename__ = "mechanics"

    id = Column(Integer, Sequence('mechanic_id_seq'), primary_key=True)
    bgg_id = Column(Integer, unique=True)
    name = Column(String, nullable=False)

    def __repr__(self):
        return "<Mechanic(name={0}, bgg_id={1})>".format(self.name, self.bgg_id)


class MechanicToBoardGame(Base):
    __tablename__ = "mechanics_to_boardgames"

    id = Column(Integer, Sequence('mechanic_to_boardgame_id_seq'), primary_key=True)
    mechanic_id = Column(Integer, ForeignKey("mechanics.id"), nullable=False)
    boardgame_id = Column(Integer, ForeignKey("boardgames.id"), nullable=False)

    __table_args__ = (UniqueConstraint("mechanic_id", "boardgame_id", name="_mechanic_boardgame_uc"),)

    def __repr__(self):
        return "<MechanicToBoardGame(mechanic={0}, boardgame={1})>".format(self.mechanic_id,
                                                                           self.boardgame_id)


class Family(Base):
    __tablename__ = "families"

    id = Column(Integer, Sequence('family_id_seq'), primary_key=True)
    bgg_id = Column(Integer, unique=True)
    name = Column(String, nullable=False)

    def __repr__(self):
        return "<Family(name={0}, bgg_id={1})>".format(self.name, self.bgg_id)


class FamilyToBoardGame(Base):
    __tablename__ = "families_to_boardgames"

    id = Column(Integer, Sequence('family_to_boardgame_id_seq'), primary_key=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    boardgame_id = Column(Integer, ForeignKey("boardgames.id"), nullable=False)

    __table_args__ = (UniqueConstraint("family_id", "boardgame_id", name="_family_boardgame_uc"),)

    def __repr__(self):
        return "<FamilyToBoardGame(family={0}, boardgame={1})>".format(self.family_id,
                                                                           self.boardgame_id)


class Designer(Base):
    __tablename__ = "designers"

    id = Column(Integer, Sequence('designer_id_seq'), primary_key=True)
    bgg_id = Column(Integer, unique=True)
    name = Column(String, nullable=False)

    def __repr__(self):
        return "<Designer(name={0}, bgg_id={1})>".format(self.name, self.bgg_id)


class DesignerToBoardGame(Base):
    __tablename__ = "designers_to_boardgames"

    id = Column(Integer, Sequence('designer_to_boardgame_id_seq'), primary_key=True)
    designer_id = Column(Integer, ForeignKey("designers.id"), nullable=False)
    boardgame_id = Column(Integer, ForeignKey("boardgames.id"), nullable=False)

    __table_args__ = (UniqueConstraint("designer_id", "boardgame_id", name="_designer_boardgame_uc"),)

    def __repr__(self):
        return "<DesignerToBoardGame(designer={0}, boardgame={1})>".format(self.designer_id,
                                                                           self.boardgame_id)


class Artist(Base):
    __tablename__ = "artists"

    id = Column(Integer, Sequence('artist_id_seq'), primary_key=True)
    bgg_id = Column(Integer, unique=True)
    name = Column(String, nullable=False)

    def __repr__(self):
        return "<Artist(name={0}, bgg_id={1})>".format(self.name, self.bgg_id)


class ArtistToBoardGame(Base):
    __tablename__ = "artists_to_boardgames"

    id = Column(Integer, Sequence('artist_to_boardgame_id_seq'), primary_key=True)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)
    boardgame_id = Column(Integer, ForeignKey("boardgames.id"), nullable=False)

    __table_args__ = (UniqueConstraint("artist_id", "boardgame_id", name="_artist_boardgame_uc"),)

    def __repr__(self):
        return "<ArtistToBoardGame(artist={0}, boardgame={1})>".format(self.artist_id,
                                                                           self.boardgame_id)


class Publisher(Base):
    __tablename__ = "publishers"

    id = Column(Integer, Sequence('publisher_id_seq'), primary_key=True)
    bgg_id = Column(Integer, unique=True)
    name = Column(String, nullable=False)

    def __repr__(self):
        return "<Publisher(name={0}, bgg_id={1})>".format(self.name, self.bgg_id)


class PublisherToBoardGame(Base):
    __tablename__ = "publishers_to_boardgames"

    id = Column(Integer, Sequence('publisher_to_boardgame_id_seq'), primary_key=True)
    publisher_id = Column(Integer, ForeignKey("publishers.id"), nullable=False)
    boardgame_id = Column(Integer, ForeignKey("boardgames.id"), nullable=False)

    __table_args__ = (UniqueConstraint("publisher_id", "boardgame_id", name="_publisher_boardgame_uc"),)

    def __repr__(self):
        return "<PublisherToBoardGame(publisher={0}, boardgame={1})>".format(self.publisher_id,
                                                                           self.boardgame_id)


class PlayerCountToBoardGame(Base):
    __tablename__ = "playercounts_to_boardgames"

    id = Column(Integer, Sequence('playercount_to_boardgame_id_seq'), primary_key=True)
    boardgame_id = Column(Integer, ForeignKey("boardgames.id"), nullable=False)
    player_count = Column(String, nullable=False)
    num_best = Column(Integer, nullable=False)
    num_recommended = Column(Integer, nullable=False)
    num_not_recommended = Column(Integer, nullable=False)

    __table_args__ = (UniqueConstraint("player_count", "boardgame_id", name="_playercount_boardgame_uc"),)

    def __repr__(self):
        return "<PlayerCountToBoardGame(boardgame={0}, playercount={1})>".format(self.boardgame_id,
                                                                             self.player_count)


class RankType(Base):
    __tablename__ = "ranktypes"

    id = Column(Integer, Sequence('ranktype_id_seq'), primary_key=True)
    bgg_id = Column(Integer, unique=True)
    name = Column(String, nullable=False)

    def __repr__(self):
        return "<RankType(name={0}, bgg_id={1})>".format(self.name, self.bgg_id)


class BoardGameRanking(Base):
    __tablename__ = "boardgame_rankings"

    id = Column(Integer, Sequence('ranking_id_seq'), primary_key=True)
    boardgame_id = Column(Integer, ForeignKey("boardgames.id"), nullable=False)
    ranktype_id = Column(Integer, ForeignKey("ranktypes.id"), nullable=False)
    rank = Column(Integer, nullable=True)  # Rank of None means "Not Ranked"
    geek_rating = Column(Float, nullable=True)  # Rank of None means "Not Ranked"

    __table_args__ = (UniqueConstraint("ranktype_id", "boardgame_id", name="_ranktype_boardgame_uc"),)

    def __repr__(self):
        return "<BoardGameRanking(boardgame={0}, ranktype={1}, rank={2})>".format(self.boardgame_id,
                                                                                self.ranktype_id,
                                                                                self.rank)


class RatingsBreakdown(Base):
    __tablename__ = "ratings_breakdown"

    id = Column(Integer, Sequence('ratings_id_seq'), primary_key=True)
    boardgame_id = Column(Integer, ForeignKey("boardgames.id"), nullable=False, unique=True)
    num_10 = Column(Integer, nullable=False)
    num_9 = Column(Integer, nullable=False)
    num_8 = Column(Integer, nullable=False)
    num_7 = Column(Integer, nullable=False)
    num_6 = Column(Integer, nullable=False)
    num_5 = Column(Integer, nullable=False)
    num_4 = Column(Integer, nullable=False)
    num_3 = Column(Integer, nullable=False)
    num_2 = Column(Integer, nullable=False)
    num_1 = Column(Integer, nullable=False)

    def __repr__(self):
        return "<RatingsBreakdown(boardgame={0})>".format(self.boardgame_id)
