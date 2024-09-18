import click
import os
from functools import wraps
from groq import Groq
from dotenv import load_dotenv
from .create_pr import create_pr
from .create_readme import create_readme

def init_groq():
    """
    Initializes the Groq API client by loading the API key from environment variables.
    Returns None if the API key is not set.
    """
    load_dotenv(verbose=True)
    api_key = os.getenv("GROQ_API_KEY")
    return Groq(api_key=api_key) if api_key else None

def init_github():
    """
    Initializes the GitHub token by loading it from environment variables.
    Returns None if the token is not set.
    """
    load_dotenv(verbose=True)
    return os.getenv("GITHUB_TOKEN")

@click.group()
@click.pass_context
def cli(ctx):
    """
    Defines a Click command group to create a command-line interface.
    This CLI is named 'Windrak' and provides advanced file operations integrated with LLM capabilities.
    """
    ctx.ensure_object(dict)
    ctx.obj['github_token'] = init_github()
    ctx.obj['groq_client'] = init_groq()

cli.add_command(create_pr)  
cli.add_command(create_readme) # Add the 'create_readme' command to the CLI group

if __name__ == '__main__':  # Ensures the script is run directly (not imported)
    cli()  # Execute the CLI