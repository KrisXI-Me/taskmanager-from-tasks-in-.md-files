import re

def parse_tasks(markdown_file):
    """Parse tasks and subtasks from a Markdown file, handling any level of nesting."""
    tasks = []
    with open(markdown_file, 'r', encoding='utf-8') as file:
        for line in file:
            # Match tasks (e.g., "- [ ] Task description" or "  - [ ] Subtask")
            match = re.match(r'(\s*)-\s*\[(.)\]\s*(.*)', line)
            if match:
                indent = len(match.group(1))  # Number of spaces for indentation
                status = "Completed" if match.group(2).strip() == 'x' else "Pending"
                description = match.group(3).strip()
                # Extract tag (e.g., @work)
                tag_match = re.search(r'@(\w+)', description)
                tag = tag_match.group(0) if tag_match else ""
                tasks.append((indent, status, description, tag, markdown_file, line))
    return tasks