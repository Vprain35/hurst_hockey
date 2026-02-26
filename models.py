from sqlmodel import SQLModel,Field,create_engine

class Bio(SQLModel, table = True):
    first_name: str = Field(default = None, primary_key = True)
    last_name: str = Field(default = None, primary_key = True)
    position: str | None = None
    jersey_number: int | None = None
    weight: int | None = None
    height: str | None = None
    class_year: str | None = None
    home_town: str | None = None
    highschool: str | None = None

class Stats(SQLModel, table = True):
    jersey_number: int | None = None
    first_name: str = Field(default = None, foreign_key="bio.first_name", primary_key = True)
    last_name: str = Field(default = None, foreign_key="bio.last_name", primary_key = True)
    G: int | None = None
    GP: int | None = None
    A: int | None = None
    PTS: int | None = None
    SH: int | None = None
    SH_PCT: float | None = None
    Plus_Minus: int | None = None
    PPG: int | None = None
    SHG: int | None = None
    FG: int | None = None
    GWG: int | None = None
    GTG: int | None = None
    OTG: int | None = None
    HTG: int | None = None
    UAG: int | None = None
    PN_PIM: str | None = None
    MIN: int | None = None
    MAJ: int | None = None
    OTH: int | None = None
    BLK: int | None = None

engine = create_engine('sqlite:///hockey.db')
SQLModel.metadata.create_all(engine)