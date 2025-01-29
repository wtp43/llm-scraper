from pydantic import BaseModel, Field


class Ammo(BaseModel):
    name: str = Field(description="The name of the ammo")
    original_price: float = Field(description="The price of the ammo")
    manufacturer: str = Field(description="The manufacturer of the ammo")
    rounds: int = Field(description="The description of the dish")
    sale_price: float = Field(description="The discounted price of the ammo")
    bullet_type: str = Field(description="The type of the bullet")
    grain: int = Field(description="The grain of the bullet")
    stock_available: int = Field(description="How much stock the vendor has")
    sku: str = Field(description="SKU or part # of the ammunition")
    calibre: str = Field(description="Calibre of the bullet")


class Quantity(BaseModel):
    rounds: int
    price_per_box: float


class Price(BaseModel):
    title: str = Field(description="The title of the ammo")
    manufacturer: str
    current_price: float = Field(description="The price of the ammo")
    sale_price: float = Field(description="The discounted price of the ammo")
    price: float = Field(description="The price of the product")
    stock_available: int = Field(description="How much stock the vendor has")
    sku: str = Field(description="SKU or part # of the ammunition")
    upc: str = Field(description="UPC of the ammunition")
    item_number: str = Field(description="Item or part # of the bullet")
    quantity_options: list[Quantity]


class Prices(BaseModel):
    Prices: list[Price]


class Ammos(BaseModel):
    ammos: list[Ammo]
