import click
import requests
from groq import Groq

def get_branch_diff(owner, repo, base, head, github_token):
    url = f"https://api.github.com/repos/{owner}/{repo}/compare/{base}...{head}"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        click.echo(f"Error: {response.status_code} - {response.text}")
        return None
    
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
            "\nDo you want to (a)ccept, (r)eject and regenerate, or (m)odify the content?",
            type=click.Choice(['a', 'r', 'm'], case_sensitive=False)
        )
        
        if choice == 'a':
            return True, None
        elif choice == 'r':
            return False, None
        elif choice == 'm':
            feedback = click.prompt("\nPlease provide your feedback or modifications")
            return False, feedback


@click.command()
@click.option('--base', default='main', help='Base branch for comparison')
@click.option('--head', default='', help='Head branch for comparison (current branch if empty)')
@click.option('--repo', help='GitHub repository in the format owner/repo')
@click.pass_context
def create_pr(ctx, base, head, repo):
    try:
        github_token = ctx.obj['github_token']
        groq_client = ctx.obj['groq_client']
        
        owner, repo_name = repo.split('/')
        
        if not head:
            # Get the default branch
            url = f"https://api.github.com/repos/{owner}/{repo_name}"
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            head = response.json()['default_branch']

        diff = get_branch_diff(owner, repo_name, base, head, github_token)
        
        feedback = None
        while True:
            title, description = generate_pr_content(diff, groq_client, feedback)
            confirmed, user_feedback = confirm_pr_content(title, description)
            
            if confirmed:
                break
            elif user_feedback is None:
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

    try:
        owner, repo_name = repo.split('/')
        
        if not head:
            # Get the default branch
            url = f"https://api.github.com/repos/{owner}/{repo_name}"
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            head = response.json()['default_branch']

        diff = get_branch_diff(owner, repo_name, base, head, github_token)
        
        feedback = None
        while True:
            title, description = generate_pr_content(diff, groq_client, feedback)
            confirmed, user_feedback = confirm_pr_content(title, description)
            
            if confirmed:
                break
            elif user_feedback is None:
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
