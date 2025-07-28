import os
import sys
import yaml

# Add the parent directory to the Python path to import reddit_post_from_schema
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reddit_research_ai.reddit_post_from_schema import post_to_reddit, create_reddit_client

def load_schema_and_post(schema_path, publish=False):
    """
    Loads a Reddit post schema from a YAML file and attempts to post it.
    """
    try:
        with open(schema_path, 'r') as f:
            schema = yaml.safe_load(f)

        reddit_client = create_reddit_client()
        post_to_reddit(schema, reddit_client, publish=publish)

    except FileNotFoundError:
        print(f"Error: Schema file not found at {schema_path}")
    except yaml.YAMLError as e:
        print(f"Error parsing YAML schema: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Example usage (for testing purposes)
    # You would typically call load_schema_and_post from another script or CLI
    print("This script is intended to be imported or called with specific schema paths.")
    print("Example: load_schema_and_post('schemas/post_schema.yaml', publish=True)")
