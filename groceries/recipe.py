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

    def add(self, name: List[str], link: str) -> CurrentRecipe:
        """Add a new recipe to the database."""
        name_text = " ".join(name).lower()
        
        recipe = {
            "Name": name_text,
            "Link": link,
        }

        read = self._db_handler.read_recipes()
        if read.error:
            return CurrentRecipe(recipe, read.error)
        
        if recipe in read.item_bank:
            return CurrentRecipe(recipe, EXISTS_ERROR)
        
        read.item_bank.append(recipe)
        write = self._db_handler.write_recipes(read.item_bank)
        return CurrentRecipe(recipe, write.error)