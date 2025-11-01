from pydantic import BaseModel
from typing import List, Optional

class PokemonResponse(BaseModel):
    sprite: str
    options: List[str]
    correct_answer: str
    types: List[str]

class AnswerCheck(BaseModel):
    selected_name: str
    correct_answer: str
    correct: bool
