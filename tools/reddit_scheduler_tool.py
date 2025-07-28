from tools.tool_interface import ToolInterface
from datetime import datetime
import pytz

class RedditSchedulerTool(ToolInterface):
    name = "reddit_schedule_check"
    description = "Check if a Reddit schema's scheduled_at field is due for posting."

    def run(self, schema):
        if "scheduled_at" not in schema:
            return {"ready": True, "reason": "No schedule set"}

        try:
            scheduled_time = datetime.fromisoformat(schema["scheduled_at"])
            now = datetime.now(tz=scheduled_time.tzinfo or pytz.UTC)
            if now >= scheduled_time:
                return {"ready": True, "reason": "Time met"}
            else:
                return {"ready": False, "reason": f"Too early, waits until {scheduled_time}"}
        except Exception as e:
            return {"ready": False, "error": f"Could not parse scheduled_at: {e}"}

