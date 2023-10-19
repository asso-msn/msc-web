from datetime import datetime

import flask
import sqlalchemy as sa
from flask import current_app as app
from werkzeug.datastructures import FileStorage

from app import archive, config, db


@app.get("/events/")
def events_list():
    query = sa.select(db.Event)
    with db.session() as s:
        events = s.execute(query).scalars().all()
    return flask.render_template("events_list.html.j2", events=events)


@app.get("/events/<string:id>")
def event_page(id):
    return flask.render_template("event.html.j2", event=db.get(db.Event, id))


@app.get("/events/<string:id>/edit")
def event_edit(id):
    return flask.render_template(
        "event_edit_form.html.j2", event=db.get(db.Event, id)
    )


@app.get("/events/<string:event_id>/upload")
def upload_form(event_id):
    event = db.get(db.Event, event_id)
    submission_id = flask.request.args.get("submission_id")
    submission = {}
    if submission_id:
        submission = db.get(db.Submission, submission_id)
    # submission = {
    #     "file": {
    #         "updated_at": datetime.utcnow(),
    #     }
    # }
    return flask.render_template(
        "upload.html.j2", event=event, submission=submission
    )


@app.post("/events/<string:event_id>/upload")
def upload(event_id, submission_id=None):
    event = db.get(db.Event, event_id)
    file: FileStorage = flask.request.files.get("file")
    extraction = archive.extract(file, config.UPLOAD_DIR)
    submission = db.Submission(
        event=event,
        draft=True,
    )
    with db.session() as s:
        s.add(submission)
    return flask.redirect(
        flask.url_for(
            "submission_edit", event_id=event_id, submission_id=submission.id
        )
    )
    return {
        "file": str(file),
        "extraction": extraction,
    }


@app.get("/events/<string:event_id>/submissions/<int:submission_id>/edit")
def submission_edit(event_id, submission_id):
    event = db.get(db.Event, event_id)
    submission = db.get(db.Submission, submission_id)
    return flask.render_template(
        "submission_edit.html.j2", event=event, submission=submission
    )
