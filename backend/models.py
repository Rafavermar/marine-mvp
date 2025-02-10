# backend/models.py
from pydantic import BaseModel
from datetime import date

class PriceQuery(BaseModel):
    port_name: str
    boat_length: float
    arrival_date: date
    departure_date: date
    want_electricity: bool
    want_water: bool

class PriceResponse(BaseModel):
    total_price: float
    detail: str


class OccupancyQuery(BaseModel):
    port_name: str
    boat_length: float
