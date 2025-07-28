import yaml
import json
import os

def convert_yaml_to_json(yaml_file_path):
    with open(yaml_file_path, 'r') as f:
        yaml_content = f.read()

    parts = yaml_content.split('---')

    # Process full schema
    full_schema_yaml_lines = []
    for line in parts[0].split('\n'):
        stripped_line = line.strip()
        if not stripped_line.startswith('#') and stripped_line:
            full_schema_yaml_lines.append(line)
    full_schema_yaml = '\n'.join(full_schema_yaml_lines)
    full_schema = yaml.safe_load(full_schema_yaml)
    
    # Ensure body is a string if it was parsed as a multiline scalar
    if isinstance(full_schema.get('body'), str):
        full_schema['body'] = full_schema['body'].strip()

    with open('post_schema_full.json', 'w') as f:
        json.dump(full_schema, f, indent=2)

    # Process minimal schema
    minimal_schema_yaml_lines = []
    for line in parts[1].split('\n'):
        stripped_line = line.strip()
        # Only include lines that look like key-value pairs after stripping initial #
        if stripped_line.startswith('#') and ':' in stripped_line:
            # Remove the leading # and any space, then add to list
            minimal_schema_yaml_lines.append(stripped_line[1:].strip())
        elif ':' in stripped_line and not stripped_line.startswith('#'): # For safety, if not commented
            minimal_schema_yaml_lines.append(line)

    # Filter out empty lines that might result from comment stripping
    minimal_schema_yaml = '\n'.join(filter(None, minimal_schema_yaml_lines))
    minimal_schema = yaml.safe_load(minimal_schema_yaml)

    with open('post_schema_minimal.json', 'w') as f:
        json.dump(minimal_schema, f, indent=2)

    print('Generated post_schema_full.json and post_schema_minimal.json')

if __name__ == "__main__":
    convert_yaml_to_json("post_schema.yaml")