from tools.tool_interface import ToolInterface
from reddit_post_from_schema import post_to_reddit, create_reddit_client, load_schema

class RedditPostTool(ToolInterface):
    name = "reddit_poster"
    description = "Post content to Reddit using a YAML or JSON schema."

    def run(self, input_data):
        # input_data can be a path to YAML or dict-like schema
        reddit = create_reddit_client()
        if isinstance(input_data, str):
            schema = load_schema(input_data)
        else:
            schema = input_data
        return post_to_reddit(schema, reddit, publish=schema.get("publish", False))

