from pathlib import Path

import yaml

from app import db


def from_file(path: Path):
    with path.open() as f:
        data = yaml.safe_load(f)
    return from_dict(data)


def from_dict(data: dict):
    for event_id, event_data in data.get("events", {}).items():
        if db.get(db.Event, event_id):
            print(f"Event {event_id} already exists")
            continue
        event = db.Event(
            id=event_id,
            name=event_data["name"],
            description=event_data.get("description"),
            start_date=event_data.get("start_date"),
            end_date=event_data.get("end_date"),
            type=event_data.get("type"),
        )
        with db.session() as s:
            s.add(event)

    for name in data.get("users", []):
        with db.session() as s:
            if s.query(db.User).filter_by(username=name).count():
                print(f"User {name} already exists")
                continue
            user = db.User(username=name)
            s.add(user)
