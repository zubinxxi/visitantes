from sqlmodel import Field, SQLModel

class Config(SQLModel, table=True):
    __tablename__ = "config"
    
    id: int | None = Field(default=None, primary_key=True)
    key: str = Field(unique=True, index=True)
    value: str = Field(default="")
    description: str | None = Field(default=None)
