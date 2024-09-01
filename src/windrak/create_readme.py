import os
import click
from directory_info_extractor import get_directory_info
from .utils import generate_readme_content

# Inclusion patterns for useful files in various languages
INCLUDE_PATTERNS = [
    # Configuration and metadata files
    'README', 'LICENSE', 'CONTRIBUTING', 'CHANGELOG', '.gitignore',
    'requirements.txt', 'setup.py', 'package.json', 'Gemfile', 'Cargo.toml',
    'composer.json', 'build.gradle', 'pom.xml', '.env.example', 'Makefile',

    # Documentation
    'docs/', '.md',

    # Main source code
    '.py', '.js', '.ts', '.java', '.rb', '.php', '.go', '.rs', '.cs',
    '.cpp', '.c', '.h', '.swift', '.kt', '.scala', '.sh', '*.bat',

    # Configuration files
    '.yml', '.yaml', '.toml', '.ini', '.cfg', '.conf',

    # Other relevant files
    'Dockerfile'
]

# Exclusion patterns
EXCLUDE_PATTERNS = [
    # Python-specific
    '.pyc', 'pycache', '.egg-info', '.dist-info', '.egg',

    # JavaScript/Node.js-specific
    'node_modules',

    # Build and distribution directories
    'build', 'dist', 'site-packages',

    # Version control
    '.git', '.github',

    # Virtual environments
    'venv', 'env', '.venv', '.env',

    # IDE and editor files
    '.vscode', '.idea', '.swp', '.swo',

    # Temporary and cache files
    '.tmp', '.bak', '*.cache',

    # Log files
    '*.log',

    # OS-specific
    '.DS_Store', 'Thumbs.db',

    # Binary and data files
    '.exe', '.dll', '.so', '.dylib', '.bin', '.dat', '.dmg',
    '.whl', '.pkl', '.pickle',

    # Image files
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.svg', '.ico',
    '.webp', '.heif',

    # Audio files
    '.mp3', '.wav', '.ogg', '.flac',

    # Video files
    '.mp4', '.avi', '*.mov',

    # Document files
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '*.pptx',

    # Archive files
    '.zip', '.tar', '.gz', '.rar',

    # Database files
    '.db', '.sqlite', '*.sqlite3',

    # Other specific files and directories
    'tests', '.flake8', '.ipynb', '.npz', '.h5', '.npy', 
    '.csv', '.tsv', '.ttf', '.mesh', '.shape', '.material', 
    '.glb', '.tiktoken'
]

@click.command()
@click.option('--path', default='.', help='Path to the project directory')
@click.option('--output', default='README.md', help='Output file name')
@click.pass_context
def create_readme(ctx, path, output):
    """
    Creates a README file in the specified project directory.
    This function leverages the Groq client stored in the context for generating content
    based on the analyzed directory structure and file contents.
    """
    # Notifies the user that the project directory is being analyzed
    click.echo(f"Analyzing project structure in {path}...")

    # Collects detailed information about the directory structure and file contents
    repo_info = get_directory_info(
        path,
        include_project_structure=True,  # Include the structure of the project directories
        include_file_contents=True,      # Include the contents of the files
        include_patterns=INCLUDE_PATTERNS,  # Specify patterns of files to include
        exclude_patterns=EXCLUDE_PATTERNS,  # Specify patterns of files to exclude
        recursive=True  # Recursively go through directories
    )

    # Notifies the user that the README content is being generated
    click.echo("Generating README content...")

    # Generates the content for the README file using the collected repo information
    readme_content = generate_readme_content(repo_info, ctx.obj['groq_client'])

    # Determines the full path where the README will be written
    readme_path = os.path.join(path, output)

    # Writes the generated README content to the specified file
    with open(readme_path, 'w') as f:
        f.write(readme_content)

    # Confirms the creation of the README file to the user
    click.echo(f"README file created successfully: {readme_path}")
