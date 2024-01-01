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
    grocery,
    recipe
)

runner = CliRunner()

def test_version():
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout

@pytest.fixture
def mock_json_file(tmp_path):
    grocery = {"grocery bank": [{"Name": "egg", "Category": "dairy"}], \
               "recipe bank": [{"Name": "white chicken chili", "Link": "https://www.halfbakedharvest.com/creamy-white-chicken-chili/"}]}
    db_file = tmp_path / "groceries.json"
    with db_file.open("w") as db:
        json.dump(grocery, db, indent=4)
    return db_file

test_grocery_data1 = {
    "name": ["chili", "powder"],
    "category": grocery.GroceryType.pantry,
    "grocery": {
        "Name": "chili powder",
        "Category": "pantry",
    },
}

test_grocery_data2 = {
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
            test_grocery_data1["name"],
            test_grocery_data1["category"],
            (test_grocery_data1["grocery"], SUCCESS),
        ),
        pytest.param(
            test_grocery_data2["name"],
            test_grocery_data2["category"],
            (test_grocery_data2["grocery"], SUCCESS),
        ),
    ],
)

def test_grocery_add(mock_json_file, name, category, expected):
    gc = grocery.GroceryController(mock_json_file)
    assert gc.add(name, category) == expected
    read = gc._db_handler.read_groceries()
    assert len(read.item_bank) == 2
    assert gc.add(name, category).error == EXISTS_ERROR
    read = gc._db_handler.read_groceries()
    assert len(read.item_bank) == 2


@pytest.fixture
def mock_wrong_json_file(tmp_path):
    db_file = tmp_path / "groceries.json"
    return db_file

def test_grocery_add_wrong_json_file(mock_wrong_json_file):
    gc = grocery.GroceryController(mock_wrong_json_file)
    response = gc.add(["test item"], grocery.GroceryType.pantry)
    assert response.error == DB_READ_ERROR
    read = gc._db_handler.read_groceries()
    assert len(read.item_bank) == 0

@pytest.fixture
def mock_wrong_json_format(tmp_path):
    db_file = tmp_path / "groceries.json"
    with db_file.open("w") as db:
        db.write("")
    return db_file

def test_grocery_add_wrong_json_format(mock_wrong_json_format):
    gc = grocery.GroceryController(mock_wrong_json_format)
    assert gc.add(test_grocery_data1["name"], test_grocery_data1["category"]) == (test_grocery_data1["grocery"],
     JSON_ERROR,
    )
    read = gc._db_handler.read_groceries()
    assert len(read.item_bank) == 0

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
def test_grocery_remove(mock_json_file, grocery_id, expected):
    gc = grocery.GroceryController(mock_json_file)
    assert gc.remove(grocery_id) == expected

def test_grocery_remove_all(mock_json_file):
    gc = grocery.GroceryController(mock_json_file)
    assert gc.remove_all() == ({}, SUCCESS)


test_recipe_data1 = {
    "name": ["coconut", "curry", "noodle", "soup"],
    "link": "https://www.halfbakedharvest.com/coconut-curry-noodle-soup/",
    "recipe": {
        "Name": "coconut curry noodle soup",
        "Link": "https://www.halfbakedharvest.com/coconut-curry-noodle-soup/",
    },
}

test_recipe_data2 = {
    "name": ["BUTTERNUT", "SQUASH", "baked", "PaStA"],
    "link": "https://www.bonappetit.com/recipe/butternut-squash-baked-pasta",
    "recipe": {
        "Name": "butternut squash baked pasta",
        "Link": "https://www.bonappetit.com/recipe/butternut-squash-baked-pasta",
    },
}

@pytest.mark.parametrize(
    "name, link, expected",
    [
        pytest.param(
            test_recipe_data1["name"],
            test_recipe_data1["link"],
            (test_recipe_data1["recipe"], SUCCESS),
        ),
        pytest.param(
            test_recipe_data2["name"],
            test_recipe_data2["link"],
            (test_recipe_data2["recipe"], SUCCESS),
        ),
    ],
)

def test_recipe_add(mock_json_file, name, link, expected):
    rc = recipe.RecipeController(mock_json_file)
    assert rc.add(name, link) == expected
    read = rc._db_handler.read_recipes()
    assert len(read.item_bank) == 2
    assert rc.add(name, link).error == EXISTS_ERROR
    read = rc._db_handler.read_recipes()
    assert len(read.item_bank) == 2

test_recipe1 = {
    "Name": "white chicken chili",
    "Link": "https://www.halfbakedharvest.com/creamy-white-chicken-chili/",
}
test_recipe2 = {}

@pytest.mark.parametrize(
        "recipe_id, expected",
        [
            pytest.param(1, (test_recipe1, SUCCESS)),
            pytest.param(3, (test_recipe2, ID_ERROR)),
        ],
)

def test_recipe_remove(mock_json_file, recipe_id, expected):
    rc = recipe.RecipeController(mock_json_file)
    assert rc.remove(recipe_id) == expected

def test_recipe_remove_all(mock_json_file):
    rc = recipe.RecipeController(mock_json_file)
    assert rc.remove_all() == ({}, SUCCESS)