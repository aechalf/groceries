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
    
    def get_recipe_bank(self) -> List[Dict[str, Any]]:
        """Return the current recipe bank."""
        read = self._db_handler.read_recipes()
        return read.item_bank
    
    def remove(self, recipe_id: int) -> CurrentRecipe:
        """Remove a recipe from the database using its id or index."""
        read = self._db_handler.read_recipes()
        if read.error:
            return CurrentRecipe({}, read.error)
        try:
            recipe = read.item_bank.pop(recipe_id - 1)
        except IndexError:
            return CurrentRecipe({}, ID_ERROR)
        write = self._db_handler.write_recipes(read.item_bank)
        return CurrentRecipe(recipe, write.error)
    
    def remove_all(self) -> CurrentRecipe:
        """Remove all recipe itmes from the database."""
        write = self._db_handler.write_recipes([])
        return CurrentRecipe({}, write.error)