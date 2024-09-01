import click
import os
from groq import Groq
from dotenv import load_dotenv
from .create_readme import create_readme

def init_groq():
    load_dotenv(verbose=True)
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

@click.group()
@click.pass_context
def cli(ctx):
    """Windrak CLI tool for advanced file operations with LLM capabilities."""
    ctx.ensure_object(dict)
    ctx.obj['groq_client'] = init_groq()

cli.add_command(create_readme)

if __name__ == 'main':
    cli()