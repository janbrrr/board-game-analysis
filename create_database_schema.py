from sqlalchemy import MetaData
from sqlalchemy_schemadisplay import create_schema_graph

if __name__ == "__main__":
    graph = create_schema_graph(metadata=MetaData("sqlite:///data/database/data_2018-05-10.db"),
                                show_datatypes=False,
                                show_indexes=False,
                                rankdir="LR",
                                concentrate=False
                                )
    graph.write_png("database_schema.png")