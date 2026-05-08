from pydantic import BaseModel, ConfigDict


class ConfigBase(BaseModel):
    key: str
    value: str
    description: str | None = None


class ConfigCreate(ConfigBase):
    pass


class ConfigUpdate(BaseModel):
    value: str | None = None
    description: str | None = None


class ConfigRead(ConfigBase):
    model_config = ConfigDict(from_attributes=True)
    id: int