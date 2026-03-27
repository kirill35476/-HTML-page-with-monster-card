from pydantic import BaseModel, Field
from typing import Optional

class Monster(BaseModel):
    """Модель монстра с картинкой"""
    id: Optional[int] = None
    name: str = Field(..., description="Имя монстра", example="Огненный дракон")
    type: str = Field(..., description="Тип монстра", example="огненный")
    power: int = Field(..., ge=1, le=100, description="Сила монстра от 1 до 100", example=95)
    hp: int = Field(..., ge=1, le=1000, description="Здоровье монстра от 1 до 1000", example=800)
    is_rare: bool = Field(False, description="Редкость монстра")
    image: str = Field(..., description="Имя файла изображения", example="dragon.png")
    description: Optional[str] = Field(None, description="Описание монстра")