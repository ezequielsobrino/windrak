import subprocess
import click
import base64
from github import Github
from github.GithubException import GithubException
import fnmatch

from .utils import generate_readme_content, require_api_keys

# Patrones de inclusión predeterminados
DEFAULT_INCLUDE_PATTERNS = [
    # Python
    '*.py',
    'requirements.txt',
    'setup.py',
    'Pipfile',
    'pyproject.toml',
    
    # JavaScript/TypeScript
    '*.js',
    '*.jsx',
    '*.ts',
    '*.tsx',
    'package.json',
    'tsconfig.json',
    
    # Java
    '*.java',
    'pom.xml',
    'build.gradle',
    
    # C#
    '*.cs',
    '*.csproj',
    '*.sln',
    
    # PHP
    '*.php',
    'composer.json',
    
    # Ruby
    '*.rb',
    'Gemfile',
    
    # Go
    '*.go',
    'go.mod',
    'go.sum',
    
    # Rust
    '*.rs',
    'Cargo.toml',
    
    # Swift
    '*.swift',
    'Package.swift',
    
    # Kotlin
    '*.kt',
    '*.kts',
    
    # Archivos comunes
    '*.md',
    'LICENSE*',
    'Dockerfile',
    '.gitignore',
    'docs/*',
]

# Patrones de exclusión predeterminados
DEFAULT_EXCLUDE_PATTERNS = [
    'README.md',

    # Python
    '*.pyc',
    '__pycache__/*',
    '*.pyo',
    '*.pyd',
    '.Python',
    'pip-selfcheck.json',
    
    # JavaScript/TypeScript
    'node_modules/*',
    'package-lock.json',
    'yarn.lock',
    '*.min.js',
    
    # Java
    '*.class',
    '*.jar',
    'target/*',
    '.gradle/*',
    
    # C#
    'bin/*',
    'obj/*',
    '*.dll',
    
    # PHP
    'vendor/*',
    'composer.lock',
    
    # Ruby
    '*.gem',
    '.bundle/*',
    
    # Go
    '/vendor/',
    
    # Rust
    'target/*',
    'Cargo.lock',
    
    # Swift
    '.build/*',
    'Packages/*',
    
    # Entornos virtuales y configuración
    'venv/*',
    'env/*',
    '.venv/*',
    '.env/*',
    'virtualenv/*',
    '*env*/*',
    '.env',
    '*.env',
    '.env.*',
    'config.local.js',
    'local_settings.py',
    '*.local',
    '*.local.*',
    
    # IDE y editores
    '.vscode/*',
    '.idea/*',
    '*.swp',
    '*.swo',
    '*.swn',
    '*.bak',
    
    # Archivos del sistema operativo
    '.DS_Store',
    'Thumbs.db',
    
    # Directorios de compilación y distribución
    'build/*',
    'dist/*',
    '*.egg-info/*',
    
    # Git
    '.git/*',
    '.gitattributes',
    
    # CI/CD
    '.github/*',
    '.travis.yml',
    '.gitlab-ci.yml',
    'circle.yml',
    'appveyor.yml',
    
    # Docker
    '.dockerignore',
    
    # Pruebas
    'tests/*',
    'test/*',
    '*_test.*',
    '*_tests.*',
    
    # Logs
    '*.log',
    'logs/*',
    
    # Bases de datos
    '*.sqlite3',
    '*.db',
    
    # Archivos temporales
    'tmp/*',
    'temp/*',
    '*.tmp',
    '*.temp',
    
    # Archivos compilados
    '*.so',
    '*.dylib',
    '*.dll',
    
    # Informes de cobertura
    '.coverage',
    'htmlcov/*',
    
    # Jupyter Notebook
    '.ipynb_checkpoints/*',
]

def get_current_repo():
    """
    Get the current repository information from git config.
    Returns a tuple of (owner, repo) or (None, None) if not in a git repository.
    """
    try:
        # Get the remote URL
        remote_url = subprocess.check_output(["git", "config", "--get", "remote.origin.url"]).decode().strip()
        
        # Parse the URL to get owner and repo
        if remote_url.endswith('.git'):
            remote_url = remote_url[:-4]
        parts = remote_url.split('/')
        owner = parts[-2]
        repo = parts[-1]
        
        return owner, repo
    except subprocess.CalledProcessError:
        return None, None

def should_include_file(file_path, include_patterns, exclude_patterns):
    """
    Determine if a file should be included based on the inclusion and exclusion patterns.
    """
    # Check exclusions first
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(file_path, pattern):
            return False
    
    # Then check inclusions
    for pattern in include_patterns:
        if fnmatch.fnmatch(file_path, pattern):
            return True
    
    return False

@click.command()
@click.pass_context
@click.option('--repo', help='GitHub repository in the format "owner/repo". If not provided, uses the current repository.')
@click.option('--output', default='README.md', help='Output file name')
@click.option('--include', multiple=True, help='Additional file patterns to include')
@click.option('--exclude', multiple=True, help='Additional file patterns to exclude')
@require_api_keys('groq', 'github')
def create_readme(ctx, repo, output, include, exclude):
    """
    Creates a README file for the specified GitHub repository or the current repository if not specified.
    This function now generates a readable string representation of the repository structure and file contents.
    """
    # Combine default and user-specified patterns
    include_patterns = list(DEFAULT_INCLUDE_PATTERNS) + list(include)
    exclude_patterns = list(DEFAULT_EXCLUDE_PATTERNS) + list(exclude)

    # Initialize GitHub client
    github_client = Github(ctx.obj['github_token'])

    # If repo is not provided, try to get the current repository
    if not repo:
        owner, repo_name = get_current_repo()
        if owner and repo_name:
            repo = f"{owner}/{repo_name}"
        else:
            click.echo("Error: Not in a git repository and no repository specified.")
            return

    click.echo(f"Analyzing GitHub repository: {repo}...")

    try:
        # Get the repository
        repository = github_client.get_repo(repo)

        # Initialize the string to store repository information
        repo_info = f"Repository: {repository.name}\n"
        repo_info += f"Description: {repository.description}\n\n"
        repo_info += "Project Structure:\n"

        # Initialize a string to store only the project structure
        project_structure = "Project Structure:\n"

        # Get repository contents
        contents = repository.get_contents("")
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repository.get_contents(file_content.path))
            else:
                if should_include_file(file_content.path, include_patterns, exclude_patterns):
                    repo_info += f"\n- {file_content.path}\n"
                    project_structure += f"- {file_content.path}\n"
                    # Get file content for text-based files
                    if file_content.path.lower().endswith(('.py', '.md', '.txt', '.yml', '.yaml', '.json', '.js', '.css', '.html')):
                        try:
                            file_content_data = base64.b64decode(file_content.content).decode('utf-8')
                            repo_info += "  Content:\n"
                            repo_info += "  " + "\n  ".join(file_content_data.split("\n")) + "\n"
                        except UnicodeDecodeError:
                            repo_info += "  Warning: Could not decode file content. Skipping content.\n"

        # Print only the project structure to the console
        click.echo("Collected repository structure:")
        click.echo(project_structure)

        # Generate README content using the full repo_info
        click.echo("Generating README content...")
        readme_content = generate_readme_content(repo_info, ctx.obj['groq_client'])

        # Write README content to file
        with open(output, 'w') as f:
            f.write(readme_content)

        click.echo(f"README file created successfully: {output}")

    except GithubException as e:
        click.echo(f"Error accessing GitHub repository: {e}")