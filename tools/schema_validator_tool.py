from tools.tool_interface import ToolInterface
from schema_validator import validate_schema

class SchemaValidatorTool(ToolInterface):
    name = "reddit_schema_validator"
    description = "Validate the structure of a Reddit post schema (YAML or JSON)."

    def run(self, input_data):
        # input_data can be a path or a loaded schema dict
        if isinstance(input_data, str):
            with open(input_data, "r") as f:
                import yaml
                schema = yaml.safe_load(f)
        else:
            schema = input_data

        return validate_schema(schema)

