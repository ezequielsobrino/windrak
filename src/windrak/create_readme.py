import os
import click
from groq import Groq
from dotenv import load_dotenv
from directory_info_extractor import get_directory_info
from .utils import generate_readme_content

# Try to load .env file, but don't raise an error if it doesn't exist
load_dotenv(verbose=True)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Inclusion patterns for useful files in various languages
INCLUDE_PATTERNS = [
    # Configuration and metadata files
    'README*', 'LICENSE*', 'CONTRIBUTING*', 'CHANGELOG*', '.gitignore',
    'requirements.txt', 'setup.py', 'package.json', 'Gemfile', 'Cargo.toml',
    'composer.json', 'build.gradle', 'pom.xml', '.env.example', 'Makefile',
    
    # Documentation
    'docs/*', '*.md',
    
    # Main source code
    '*.py', '*.js', '*.ts', '*.java', '*.rb', '*.php', '*.go', '*.rs', '*.cs',
    '*.cpp', '*.c', '*.h', '*.swift', '*.kt', '*.scala', '*.sh', '*.bat',
    
    # Configuration files
    '*.yml', '*.yaml', '*.toml', '*.ini', '*.cfg', '*.conf',
    
    # Other relevant files
    'Dockerfile'
]

# Exclusion patterns
EXCLUDE_PATTERNS = [
    # Python-specific
    '*.pyc', '__pycache__', '*.egg-info', '*.dist-info', '*.egg',
    
    # JavaScript/Node.js-specific
    'node_modules',
    
    # Build and distribution directories
    'build', 'dist', 'site-packages',
    
    # Version control
    '.git', '.github',
    
    # Virtual environments
    'venv', 'env', '.venv', '.env',
    
    # IDE and editor files
    '.vscode', '.idea', '*.swp', '*.swo',
    
    # Temporary and cache files
    '*.tmp', '*.bak', '*.cache',
    
    # Log files
    '*.log',
    
    # OS-specific
    '.DS_Store', 'Thumbs.db',
    
    # Binary and data files
    '*.exe', '*.dll', '*.so', '*.dylib', '*.bin', '*.dat', '*.dmg',
    '*.whl', '*.pkl', '*.pickle',
    
    # Image files
    '*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp', '*.tiff', '*.svg', '*.ico',
    '*.webp', '*.heif',
    
    # Audio files
    '*.mp3', '*.wav', '*.ogg', '*.flac',
    
    # Video files
    '*.mp4', '*.avi', '*.mov',
    
    # Document files
    '*.pdf', '*.doc', '*.docx', '*.xls', '*.xlsx', '*.ppt', '*.pptx',
    
    # Archive files
    '*.zip', '*.tar', '*.gz', '*.rar',
    
    # Database files
    '*.db', '*.sqlite', '*.sqlite3',
    
    # Other specific files and directories
    'tests', '.flake8', '*.ipynb', '*.npz', '*.h5', '*.npy', 
    '*.csv', '*.tsv', '*.ttf', '*.mesh', '*.shape', '*.material', 
    '*.glb', '*.tiktoken'
]


@click.command()
@click.option('--path', default='.', help='Path to the project directory')
@click.option('--output', default='README.md', help='Output file name')
def create_readme(path, output):
    """Create a README file."""
    click.echo(f"Analyzing project structure in {path}...")
    
    # Get directory info with custom include and exclude patterns
    repo_info = get_directory_info(
        path,
        include_project_structure=True,
        include_file_contents=True,
        include_patterns=INCLUDE_PATTERNS,
        exclude_patterns=EXCLUDE_PATTERNS,
        recursive=True
    )
    
    click.echo("Generating README content...")
    readme_content = generate_readme_content(repo_info, client)
    
    # Create the full path for the README file
    readme_path = os.path.join(path, output)
    
    # Save the README file
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    click.echo(f"README file created successfully: {readme_path}")