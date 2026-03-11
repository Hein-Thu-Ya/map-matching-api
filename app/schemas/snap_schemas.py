from pydantic import BaseModel
from typing import List


class Point(BaseModel):
    lat: float
    lon: float


class SnapRequest(BaseModel):
    lat: float
    lon: float
    

class BatchSnapRequest(BaseModel):
    points: List[Point]
    