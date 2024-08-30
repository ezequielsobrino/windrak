import click
from .create_readme import create_readme

@click.group()
def cli():
    """Windrak CLI tool for advanced file operations with LLM capabilities."""
    pass

cli.add_command(create_readme)

if __name__ == '__main__':
    cli()