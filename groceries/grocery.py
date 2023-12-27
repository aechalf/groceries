"""This module provides the Groceries model-controller."""
# groceries/grocery.py

from pathlib import Path
from enum import Enum
from typing import Any, Dict, List, NamedTuple
from groceries import DB_READ_ERROR, EXISTS_ERROR, ID_ERROR
from groceries.database import DatabaseHandler

class GroceryType(str, Enum): 
    produce  = "produce"
    dairy    = "dairy"
    meat     = "meat"
    pantry   = "pantry"
    frozen   = "frozen"
    beverage = "beverage"

class CurrentGrocery(NamedTuple):
    grocery: Dict[str, Any]
    error: int

class GroceryController:
    def __init__(self, db_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)

    def add(self, name: List[str], category: GroceryType) -> CurrentGrocery:
        """Add a new grocery item to the database."""
        name_text = " ".join(name)
        name_text = name_text.lower()

        category_text = category.value

        grocery = {
            "Name": name_text,
            "Category": category_text,
        }

        read = self._db_handler.read_groceries()
        if read.error:
            return CurrentGrocery(grocery, read.error)
        
        if grocery in read.grocery_bank:
            return CurrentGrocery(grocery, EXISTS_ERROR)
        
        read.grocery_bank.append(grocery)
        write = self._db_handler.write_groceries(read.grocery_bank)
        return CurrentGrocery(grocery, write.error)
    
    def get_grocery_bank(self) -> List[Dict[str, Any]]:
        """Return the current grocery bank."""
        read = self._db_handler.read_groceries()
        return read.grocery_bank
    
    def remove(self, grocery_id: int) -> CurrentGrocery:
        """Remove a grocery item from the database using its id or index."""
        read = self._db_handler.read_groceries()
        if read.error:
            return CurrentGrocery({}, read.error)
        try:
            grocery = read.grocery_bank.pop(grocery_id - 1)
        except IndexError:
            return CurrentGrocery({}, ID_ERROR)
        write = self._db_handler.write_groceries(read.grocery_bank)
        return CurrentGrocery(grocery, write.error)
    
    def remove_all(self) -> CurrentGrocery:
        """Remove all grocery items from the database."""
        write = self._db_handler.write_groceries([])
        return CurrentGrocery({}, write.error)