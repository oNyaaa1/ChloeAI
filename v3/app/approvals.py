from datetime import datetime, timedelta
import uuid
from pathlib import Path
from sqlalchemy import select
from .config import settings
from .db import PendingAction, SessionLocal


def request_file_write(relative_path: str, content: str) -> dict:
    """Queue a file write. No file is changed until the user approves the action."""
    root = Path(settings.workspace_dir).resolve()
    target = (root / relative_path).resolve()
    if target != root and root not in target.parents:
        raise ValueError("Path must remain inside the configured workspace")
    action_id = str(uuid.uuid4())
    now = datetime.utcnow()
    payload = {"path": str(target), "content": content}
    with SessionLocal() as db:
        db.add(PendingAction(id=action_id, action_type="write_file", payload=payload,
                             status="pending", created_at=now,
                             expires_at=now + timedelta(minutes=settings.approval_expiry_minutes)))
        db.commit()
    return {"id": action_id, "status": "pending_approval", "action": "write_file",
            "path": str(target), "expires_at": (now + timedelta(minutes=settings.approval_expiry_minutes)).isoformat()}


def decide_action(action_id: str, approve: bool) -> dict:
    with SessionLocal() as db:
        action = db.scalar(select(PendingAction).where(PendingAction.id == action_id))
        if not action:
            raise LookupError("Action not found")
        if action.status != "pending":
            raise ValueError(f"Action is already {action.status}")
        if action.expires_at < datetime.utcnow():
            action.status = "expired"
            db.commit()
            raise ValueError("Approval request expired")
        if not approve:
            action.status = "rejected"
            db.commit()
            return {"id": action.id, "status": "rejected"}
        # Deliberately allow-list only. Add new action types only with explicit review.
        if action.action_type != "write_file":
            raise ValueError("This action type is not enabled")
        payload = action.payload
        root = Path(settings.workspace_dir).resolve()
        target = Path(payload["path"]).resolve()
        if target != root and root not in target.parents:
            raise ValueError("Refusing path outside workspace")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(payload["content"], encoding="utf-8")
        action.status = "approved_executed"
        action.result = f"Wrote {target}"
        db.commit()
        return {"id": action.id, "status": action.status, "result": action.result}
