from pydantic import BaseModel, Field


class AddressBase(BaseModel):
    cep: str = Field(..., min_length=8, max_length=9, examples=["01310-100"])
    street: str = Field(..., max_length=255, examples=["Av. Paulista"])
    number: str = Field(..., max_length=20, examples=["1000"])
    complement: str | None = Field(None, max_length=100, examples=["Apto 101"])
    city: str = Field(..., max_length=100, examples=["São Paulo"])
    state: str = Field(..., min_length=2, max_length=2, examples=["SP"])


class AddressCreate(AddressBase):
    pass


class AddressResponse(AddressBase):
    id: int
    latitude: float | None = None
    longitude: float | None = None

    class Config:
        from_attributes = True

