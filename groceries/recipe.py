"""This module provides the Recipes model-controller."""
# groceries/recipe.py

from pathlib import Path
from typing import Any, Dict, List, NamedTuple
from groceries import DB_READ_ERROR, EXISTS_ERROR, ID_ERROR
from groceries.database import DatabaseHandler

class CurrentRecipe(NamedTuple):
    recipe: Dict[str, Any]
    error: int

class RecipeController:
    def __init__(self, db_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)