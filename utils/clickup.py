import requests
from utils.logger import logger


_BASE = "https://api.clickup.com/api/v2"


def create_task(
    api_token: str,
    list_id: str,
    name: str,
    description: str,
    priority: int = 3,
) -> str | None:
    """Create a ClickUp task. Returns the task URL on success, None on failure."""
    if not api_token or not list_id:
        logger.debug("ClickUp not configured — skipping task creation")
        return None

    url = f"{_BASE}/list/{list_id}/task"
    headers = {"Authorization": api_token, "Content-Type": "application/json"}
    payload = {
        "name": name,
        "description": description,
        "priority": priority,
        "notify_all": False,
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        task = resp.json()
        task_url = task.get("url", "")
        logger.info(f"ClickUp task created: {name} → {task_url}")
        return task_url
    except Exception as exc:
        logger.warning(f"ClickUp task creation failed: {exc}")
        return None
