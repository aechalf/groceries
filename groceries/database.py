"""This module provides the Groceries database functionality."""
# groceries/database.py

import configparser
import json
from pathlib import Path
from typing import Any, Dict, List, NamedTuple
from groceries import DB_READ_ERROR, DB_WRITE_ERROR, JSON_ERROR, SUCCESS

DEFAULT_DB_FILE_PATH = Path.home().joinpath(
    "." + Path.home().stem + "_groceries.json"
)

def get_database_path(config_file: Path) -> Path:
    """Return the current path to the grocries database."""
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return Path(config_parser["General"]["database"])

def init_database(db_path: Path) -> int:
    """Create the application's database."""
    try:
        db_path.write_text('{"grocery bank": [], "recipe bank": []}') # Empty grocery bank and recipe bank
        return SUCCESS
    except OSError:
        return DB_WRITE_ERROR
    
class DBResponse(NamedTuple):
    item_bank: List[Dict[str, Any]]
    error: int

class DatabaseHandler:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def read_items(self, bank_type: str) -> DBResponse:
        print(f'DB path is {self._db_path}')
        try:
            with self._db_path.open("r") as db:
                try:
                    json_data = json.load(db)
                    return DBResponse(json_data[bank_type], SUCCESS)
                except json.JSONDecodeError: # Catch wrong JSON format
                    return DBResponse([], JSON_ERROR)
        except OSError: # Catch file IO problems
            return DBResponse([], DB_READ_ERROR)
        
    def write_items(self, item_bank: List[Dict[str, Any]], bank_type: str) -> DBResponse:
        try:
            with self._db_path.open("r+") as db:
                json_data = json.load(db)
                json_data[bank_type] = item_bank
                db.seek(0)
                json.dump(json_data, db, indent=4)
            return DBResponse(item_bank, SUCCESS)
        except OSError: # Catch file IO problems
            return DBResponse(item_bank, DB_WRITE_ERROR)

    def read_groceries(self) -> DBResponse:
        return self.read_items("grocery bank")
        
    def write_groceries(self, grocery_bank: List[Dict[str, Any]]) -> DBResponse:
        return self.write_items(grocery_bank, "grocery bank")
        
    def read_recipes(self) -> DBResponse:
        return self.read_items("recipe bank")
        
    def write_recipes(self, recipe_bank: List[Dict[str, Any]]) -> DBResponse:
        return self.write_items(recipe_bank, "recipe bank")