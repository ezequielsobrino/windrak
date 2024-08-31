import os
import click
from groq import Groq
from dotenv import load_dotenv
from directory_info_extractor import get_directory_info
from .utils import generate_readme_content

# Try to load .env file, but don't raise an error if it doesn't exist
load_dotenv(verbose=True)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Predefined exclude patterns
EXCLUDE_PATTERNS = [
    '*.pyc', '__pycache__', '.git', '.github', '.flake8', '*.flac',
    '*.tiktoken', '*.ipynb', '*.npz', '*.png', '*.jpg',
    '*.jpeg', '*.gif', '*.bmp', '*.tiff', '*.svg', '*.ico',
    '*.webp', '*.heif', '*.bpg', '*.flif', '*.tga', '*.tif', '*.psd',
    'tests', '*.ttf', '*.mesh', '*.shape', '*.material', '*.glb', '*.ogg',
    'venv', 'env', 'node_modules', 'build', 'dist', 'site-packages',
    '*.egg-info', '*.dist-info', '*.egg', '*.whl', '*.lock', '*.log',
    '*.pickle', '*.pkl', '*.h5', '*.npy', '*.npz', '*.csv', '*.tsv',
    '*.exe', '*.dll', '*.so', '*.dylib', '*.bin', '*.dat', '*.dmg'
]

@click.command()
@click.option('--path', default='.', help='Path to the project directory')
@click.option('--output', default='README.md', help='Output file name')
def create_readme(path, output):
    """Create a README file."""
    click.echo(f"Analyzing project structure in {path}...")
    
    # Get directory info with predefined exclude patterns
    repo_info = get_directory_info(path, exclude_patterns=EXCLUDE_PATTERNS)
    
    click.echo("Generating README content...")
    readme_content = generate_readme_content(repo_info, client)
    
    # Save the README file
    with open(output, 'w') as f:
        f.write(readme_content)
    
    click.echo(f"README file created successfully: {output}")