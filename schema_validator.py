import yaml
import json
import os
import argparse

def validate_schema(schema_data):
    errors = []
    warnings = []

    # Required fields check
    required_fields = ["subreddit", "title", "body"]
    for field in required_fields:
        if field not in schema_data:
            errors.append(f"Missing required field: '{field}'")

    # Content type check (body, url, or crosspost_id)
    if not (schema_data.get("body") or schema_data.get("url") or schema_data.get("crosspost_id")):
        errors.append("One of 'body', 'url', or 'crosspost_id' is required.")

    # Basic subreddit name check (can be expanded with PRAW for live validation)
    subreddit = schema_data.get("subreddit")
    if subreddit and not isinstance(subreddit, str):
        errors.append("Subreddit must be a string.")
    elif subreddit and (" " in subreddit or "/" in subreddit):
        warnings.append(f"Subreddit name '{subreddit}' contains spaces or slashes. This might be invalid.")

    # Basic flair check (can be expanded with PRAW for live validation)
    flair_text = schema_data.get("flair_text")
    if flair_text and not isinstance(flair_text, str):
        errors.append("Flair text must be a string.")

    # Markdown preview (simple print for now)
    if schema_data.get("body") and schema_data.get("content_type") == "markdown":
        print("\n--- Markdown Body Preview ---")
        print(schema_data["body"])
        print("---------------------------")

    return errors, warnings

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate Reddit post schema files.")
    parser.add_argument("schema_path", help="Path to the schema file (YAML or JSON).")
    args = parser.parse_args()

    schema_data = None
    try:
        with open(args.schema_path, 'r') as f:
            if args.schema_path.endswith((".yaml", ".yml")):
                schema_data = yaml.safe_load(f)
            elif args.schema_path.endswith(".json"):
                schema_data = json.load(f)
            else:
                print("Error: Unsupported file type. Please provide a .yaml, .yml, or .json file.")
                exit(1)
    except FileNotFoundError:
        print(f"Error: Schema file not found at {args.schema_path}")
        exit(1)
    except (yaml.YAMLError, json.JSONDecodeError) as e:
        print(f"Error parsing schema file: {e}")
        exit(1)

    if schema_data:
        print(f"Validating schema: {args.schema_path}")
        errors, warnings = validate_schema(schema_data)

        if errors:
            print("\n--- Validation Errors ---")
            for error in errors:
                print(f"❌ {error}")
        
        if warnings:
            print("\n--- Validation Warnings ---")
            for warning in warnings:
                print(f"⚠️ {warning}")

        if not errors and not warnings:
            print("✅ Schema is valid and looks good!")
        elif not errors and warnings:
            print("✅ Schema is valid with warnings.")
        else:
            print("❌ Schema has errors. Please fix them.")
