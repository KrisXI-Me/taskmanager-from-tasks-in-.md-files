import os

def find_markdown_files(directory):
    """Find all Markdown files in the given directory (recursively)."""
    markdown_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                markdown_files.append(os.path.join(root, file))
    return markdown_files