DEFAULT_SECTIONS = """
1. Project Name: The name of the project.
2. Brief Description: A concise overview of the project's purpose and objectives.
3. Main Features: A comprehensive list of the primary features and functionalities.
4. Prerequisites: Detailed requirements needed to run or develop the project.
5. Installation: Step-by-step instructions for installing and configuring the project.
6. Usage: Detailed instructions on how to use the project.
7. Examples: Concrete examples and use cases demonstrating how to utilize the project's features.
8. Project Structure: A detailed description of the folder structure and key files.
9. API Reference: Detailed API documentation, if applicable.
10. How to Contribute: Guidelines for contributing to the project.
11. Troubleshooting: Common issues and their resolutions.
12. Changelog: A log of notable changes, improvements, and bug fixes.
13. License: Information about the project's licensing terms.
14. Contact: How to get in touch with the project maintainers.
"""

def generate_readme_content(repo_info, client, sections=None):
    if sections is None:
        sections = DEFAULT_SECTIONS
    
    prompt = f"""
    Generate an expert-level README.md for a project based on the following repository information:

    {repo_info}

    The README should include the following sections with their respective descriptions:
    {sections}

    Use Markdown for formatting. Ensure that the content is detailed, clear, and informative.
    """
    
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="llama-3.1-70b-versatile",
        max_tokens=2048,
        temperature=0.5,
    )
    
    return response.choices[0].message.content