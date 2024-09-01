import click
import os
from groq import Groq  # Importing the Groq library for specific API interactions
from dotenv import load_dotenv  # dotenv for loading environment variables
from .create_readme import create_readme  # Importing a custom function to create README files

def init_groq():
    """
    Initializes the Groq API client by loading the API key from environment variables.
    This setup enhances security by avoiding hard-coded credentials.
    """
    load_dotenv(verbose=True)  # Load environment variables and show process if verbose
    return Groq(api_key=os.getenv("GROQ_API_KEY"))  # Create and return a Groq client using the API key

@click.group()
@click.pass_context
def cli(ctx):
    """
    Defines a Click command group to create a command-line interface.
    This CLI is named 'Windrak' and provides advanced file operations integrated with LLM capabilities.
    """
    ctx.ensure_object(dict)  # Ensure that the context is a dictionary to store shared data
    ctx.obj['groq_client'] = init_groq()  # Store the initialized Groq client in the context for use in other commands

cli.add_command(create_readme)  # Add the 'create_readme' command to the CLI group

if __name__ == '__main__':  # Ensures the script is run directly (not imported)
    cli()  # Execute the CLI