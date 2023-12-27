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
    grocery_bank: List[Dict[str, Any]]
    error: int

class DatabaseHandler:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def read_groceries(self) -> DBResponse:
        print(f'DB path is {self._db_path}')
        try:
            with self._db_path.open("r") as db:
                try:
                    json_data = json.load(db)
                    return DBResponse(json_data["grocery bank"], SUCCESS)
                except json.JSONDecodeError: # Catch wrong JSON format
                    return DBResponse([], JSON_ERROR)
        except OSError: # Catch file IO problems
            return DBResponse([], DB_READ_ERROR)
        
    def write_groceries(self, grocery_bank: List[Dict[str, Any]]) -> DBResponse:
        try:
            with self._db_path.open("r+") as db:
                json_data = json.load(db)
                json_data["grocery bank"] = grocery_bank
                db.seek(0)
                json.dump(json_data, db, indent=4)
            return DBResponse(grocery_bank, SUCCESS)
        except OSError: # Catch file IO problems
            return DBResponse(grocery_bank, DB_WRITE_ERROR)