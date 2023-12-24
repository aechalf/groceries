"""This module provides the Groceries CLI."""
# groceries/cli.py

from pathlib import Path
from typing import List, Optional
import typer
from groceries import (
    ERRORS, __app_name__, __version__, config, database, grocery
)

app = typer.Typer()

@app.command()
def init(
    db_path: str = typer.Option(
        str(database.DEFAULT_DB_FILE_PATH),
        "--db-path",
        "-db",
        prompt="groceries database location?",
    ),
) -> None:
    """Initialize the groceries database."""
    app_init_error = config.init_app(db_path)
    if app_init_error:
        typer.secho(
            f'Creating config file failed with "{ERRORS[app_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    db_init_error = database.init_database(Path(db_path))
    if db_init_error:
        typer.secho(
            f'Creating database failed with "{ERRORS[db_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(f"The groceries database is {db_path}", 
                    fg=typer.colors.GREEN)
        

def get_grocery_controller() -> grocery.GroceryController:
    if config.CONFIG_FILE_PATH.exists():
        db_path = database.get_database_path(config.CONFIG_FILE_PATH)
    else:
        typer.secho(
            'Config file not found. Please run "groceries init"',
            fg=typer.colors.Red,
        )
        raise typer.Exit(1)
    if db_path.exists():
        return grocery.GroceryController(db_path)
    else:
        typer.secho(
            'Database not found. Please run "groceries init"',
            fg=typer.colors.RED
        )
        raise typer.Exit(1)
    
@app.command()
def remove(
    grocery_id: int = typer.Argument(...),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force deletion without confirmation.",
    ),
) -> None:
    """Remove a grocery item using its GROCERY_ID."""
    gc = get_grocery_controller()

    def _remove():
        grocery, error = gc.remove(grocery_id)
        if error:
            typer.secho(
                f'Removing grocery item # {grocery_id} failed with "{ERRORS[error]}"',
                fg=typer.colors.RED,
            )
            raise typer.Exit(1)
        else:
            typer.secho(
                f"""grocery # {grocery_id}: '{grocery["Name"]}' was removed""",
                fg=typer.colors.GREEN,
            )

    if force:
        _remove()
    else:
        grocery_bank = gc.get_grocery_bank()
        try:
            grocery = grocery_bank[grocery_id - 1]
        except IndexError:
            typer.secho("Invalid GROCERY_ID", fg=typer.colors.RED)
            raise typer.Exit(1)
        delete = typer.confirm(
            f"Delete grocery # {grocery_id}: {grocery['Name']}?"
        )
        if delete:
            _remove()
        else:
            typer.echo("Operation canceled")

@app.command(name="clear")
def remove_all(
    force: bool = typer.Option(
        ...,
        prompt="Delete all grocery items?",
        help="Force deletion without confirmation.",
    ),
) -> None:
    """Remove all grocery items."""
    gc = get_grocery_controller()
    if force:
        error = gc.remove_all().error
        if error:
            typer.secho(
                f'Removing grocery items failed with "{ERRORS[error]}"',
                fg=typer.colors.RED,
            )
            raise typer.Exit(1)
        else:
            typer.secho("All grocery items were removed.",
                        fg=typer.colors.GREEN)
    else:
        typer.echo("Operation canceled")
    
@app.command()
def add(
    name: List[str] = typer.Argument(...),
    category: grocery.GroceryType = typer.Option(...,"--category", "-c", case_sensitive=False),
) -> None:
    """Add a new grocery with a CATEGORY."""
    gc = get_grocery_controller()
    grocery, error = gc.add(name, category)
    if error:
        typer.secho(
            f'Adding grocery item failed with "{ERRORS[error]}"',
            fg=typer.colors.RED
        )
        raise typer.Exit(1)
    else:
        typer.secho(
            f"""grocery: "{grocery['Name']}" was added"""
            f""" with category: {category}""",
            fg=typer.colors.GREEN,
        )

@app.command(name="list")
def list_all() -> None:
    """List all groceries in bank."""
    gc = get_grocery_controller()
    grocery_bank = gc.get_grocery_bank()
    if len(grocery_bank) == 0:
        typer.secho(
            "There are no groceries in the bank yet",
            fg=typer.colors.RED
        )
        raise typer.Exit()
    typer.secho("\ngrocery bank:\n", fg=typer.colors.BLUE, bold=True)
    columns = (
        "ID.  ",
        "| Category  ",
        "| Name  ",
    )
    headers = "".join(columns)
    typer.secho(headers, fg=typer.colors.BLUE, bold=True)
    typer.secho("-" * len(headers), fg=typer.colors.BLUE)
    for id, grocery in enumerate(grocery_bank, 1):
        name, category = grocery.values()
        typer.secho(
            f"{id}{(len(columns[0]) - len(str(id))) * ' '}"
            f"| {category}{(len(columns[1]) - len(str(category)) - 2) * ' '}"
            f"| {name}",
            fg=typer.colors.BLUE,
        )
    typer.secho("-" * len(headers) + "\n", fg=typer.colors.BLUE)

def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return