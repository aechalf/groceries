# test/test_groceries.py

import json
import pytest
from typer.testing import CliRunner
from groceries import (
    DB_READ_ERROR,
    SUCCESS,
    EXISTS_ERROR,
    ID_ERROR,
    JSON_ERROR,
    __app_name__,
    __version__,
    cli,
    grocery
)

runner = CliRunner()

def test_version():
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout

@pytest.fixture
def mock_json_file(tmp_path):
    grocery = {"grocery bank": [{"Name": "egg", "Category": "dairy"}], "recipe bank": []}
    db_file = tmp_path / "groceries.json"
    with db_file.open("w") as db:
        json.dump(grocery, db, indent=4)
    return db_file

test_data1 = {
    "name": ["chili", "powder"],
    "category": grocery.GroceryType.pantry,
    "grocery": {
        "Name": "chili powder",
        "Category": "pantry",
    },
}

test_data2 = {
    "name": ["milk"],
    "category": grocery.GroceryType.dairy,
    "grocery": {
        "Name": "milk",
        "Category": "dairy",
    },
}

@pytest.mark.parametrize(
    "name, category, expected",
    [
        pytest.param(
            test_data1["name"],
            test_data1["category"],
            (test_data1["grocery"], SUCCESS),
        ),
        pytest.param(
            test_data2["name"],
            test_data2["category"],
            (test_data2["grocery"], SUCCESS),
        ),
    ],
)

def test_add(mock_json_file, name, category, expected):
    gc = grocery.GroceryController(mock_json_file)
    assert gc.add(name, category) == expected
    read = gc._db_handler.read_groceries()
    assert len(read.grocery_bank) == 2
    assert gc.add(name, category).error == EXISTS_ERROR
    read = gc._db_handler.read_groceries()
    assert len(read.grocery_bank) == 2


@pytest.fixture
def mock_wrong_json_file(tmp_path):
    db_file = tmp_path / "groceries.json"
    return db_file

def test_add_wrong_json_file(mock_wrong_json_file):
    gc = grocery.GroceryController(mock_wrong_json_file)
    response = gc.add(["test item"], grocery.GroceryType.pantry)
    assert response.error == DB_READ_ERROR
    read = gc._db_handler.read_groceries()
    assert len(read.grocery_bank) == 0

@pytest.fixture
def mock_wrong_json_format(tmp_path):
    db_file = tmp_path / "groceries.json"
    with db_file.open("w") as db:
        db.write("")
    return db_file

def test_add_wrong_json_format(mock_wrong_json_format):
    gc = grocery.GroceryController(mock_wrong_json_format)
    assert gc.add(test_data1["name"], test_data1["category"]) == (test_data1["grocery"],
     JSON_ERROR,
    )
    read = gc._db_handler.read_groceries()
    assert len(read.grocery_bank) == 0

test_grocery1 = {
    "Name": "egg",
    "Category": grocery.GroceryType.dairy,
}
test_grocery2 = {}

@pytest.mark.parametrize(
    "grocery_id, expected",
    [
        pytest.param(1, (test_grocery1, SUCCESS)),
        pytest.param(3, (test_grocery2, ID_ERROR)),
    ],
)
def test_remove(mock_json_file, grocery_id, expected):
    gc = grocery.GroceryController(mock_json_file)
    assert gc.remove(grocery_id) == expected

def test_remove_all(mock_json_file):
    gc = grocery.GroceryController(mock_json_file)
    assert gc.remove_all() == ({}, SUCCESS)