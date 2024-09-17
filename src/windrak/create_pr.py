import click
import requests
import subprocess
import os

def get_branch_diff(owner, repo, base, head, github_token):
    url = f"https://api.github.com/repos/{owner}/{repo}/compare/{base}...{head}"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    comparison = response.json()
    
    diff = ""
    for file in comparison.get('files', []):
        diff += f"File: {file['filename']}\n"
        diff += f"Status: {file['status']}\n"
        if 'patch' in file:
            diff += f"Changes: {file['patch']}\n"
        diff += "\n"
    
    return diff

def generate_pr_content(diff, groq_client, feedback=None):
    if feedback:
        prompt = f"""
        Based on the following git diff and user feedback, generate an improved Pull Request title and description:

        Git diff:
        {diff}

        Previous content:
        {feedback['previous_content']}

        User feedback:
        {feedback['user_input']}

        Format the response as follows:
        Title: [Generated PR title]
        Description: [Generated PR description]

        Ensure the title is brief and descriptive, and the description provides context and summarizes the changes.
        Address the user's feedback in your new generation.
        """
    else:
        prompt = f"""
        Generate a concise and informative Pull Request title and description based on the following git diff:

        {diff}

        Format the response as follows:
        Title: [Generated PR title]
        Description: [Generated PR description]

        Ensure the title is brief and descriptive, and the description provides context and summarizes the changes.
        """
    
    response = groq_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="llama-3.1-70b-versatile",
        max_tokens=1024,
        temperature=0.5,
    )
    
    content = response.choices[0].message.content
    title, description = content.split('Description:', 1)
    return title.replace('Title:', '').strip(), description.strip()

def confirm_pr_content(title, description):
    click.echo(f"\nGenerated PR Title: {title}")
    click.echo(f"\nGenerated PR Description:\n{description}")
    
    while True:
        choice = click.prompt(
            "\nChoose an option:\n"
            "(a) Accept\n"
            "(r) Regenerate\n"
            "(m) Modify (provide feedback)\n"
            "(c) Cancel",
            type=click.Choice(['a', 'r', 'm', 'c'], case_sensitive=False)
        )
        
        if choice == 'a':
            print("Content accepted.")
            return True, None
        elif choice == 'r':
            print("Regenerating content...")
            return False, "regenerate"
        elif choice == 'm':
            feedback = click.prompt("\nPlease provide your feedback or modifications")
            return False, feedback
        elif choice == 'c':
            print("Operation cancelled.")
            return True, "cancel"

def get_current_branch():
    try:
        return subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode('utf-8').strip()
    except subprocess.CalledProcessError:
        click.echo("Error: Not a git repository or git command not found.")
        return None

def get_remote_url():
    try:
        remote_url = subprocess.check_output(['git', 'config', '--get', 'remote.origin.url']).decode('utf-8').strip()
        # Extract owner/repo from the URL
        if remote_url.endswith('.git'):
            remote_url = remote_url[:-4]
        return os.path.basename(os.path.dirname(remote_url)) + '/' + os.path.basename(remote_url)
    except subprocess.CalledProcessError:
        click.echo("Error: Unable to get remote URL. Make sure you're in a git repository with a remote named 'origin'.")
        return None

@click.command()
@click.option('--base', help='Base branch for comparison (default: main)')
@click.option('--head', help='Head branch for comparison (default: current branch)')
@click.option('--repo', help='GitHub repository in the format owner/repo (default: derived from remote origin)')
@click.pass_context
def create_pr(ctx, base, head, repo):
    try:
        github_token = ctx.obj['github_token']
        groq_client = ctx.obj['groq_client']
        
        if not base:
            base = 'main'
            click.echo(f"Using default base branch: {base}")
        
        if not head:
            head = get_current_branch()
            if not head:
                return
            click.echo(f"Using current branch as head: {head}")
        
        if not repo:
            repo = get_remote_url()
            if not repo:
                return
            click.echo(f"Using repository derived from remote: {repo}")
        
        owner, repo_name = repo.split('/')
        
        # Rest of the function remains the same...
        diff = get_branch_diff(owner, repo_name, base, head, github_token)
        
        feedback = None
        while True:
            title, description = generate_pr_content(diff, groq_client, feedback)
            confirmed, user_feedback = confirm_pr_content(title, description)
            
            if confirmed:
                if user_feedback == "cancel":
                    click.echo("Operation cancelled. No PR created.")
                    return
                break  # Exit the loop if the user accepts the content
            elif user_feedback == "regenerate":
                feedback = None  # Regenerate without specific feedback
            else:
                feedback = {
                    'previous_content': f"Title: {title}\nDescription: {description}",
                    'user_input': user_feedback
                }

        # Create the pull request
        url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        data = {
            "title": title,
            "body": description,
            "head": head,
            "base": base
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        pr = response.json()
        click.echo(f"Pull Request created successfully: {pr['html_url']}")
    except Exception as e:
        click.echo(f"Error creating Pull Request: {str(e)}")
