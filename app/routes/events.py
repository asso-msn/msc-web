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
    return flask.render_template(
        "event.html.j2", event=db.get(db.Event, id, load="submissions")
    )


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
def upload(event_id):
    # TODO get logged user
    user_id = 1
    event = db.get(db.Event, event_id)
    with db.session() as s:
        submission_id = s.query(db.Submission).count() + 1
    file: FileStorage = flask.request.files.get("file")
    submission = db.Submission(
        id=submission_id,
        author_id=user_id,
        event=event,
        name="New submission",
        draft=True,
    )
    extraction = archive.extract(file, submission.path)
    attributes = extraction["extended_attributes"]
    submission.illustration = attributes.get("illustration")
    if attributes.get("title") and attributes.get("artist"):
        submission.name = submission.get_default_name(
            attributes["title"], attributes["artist"]
        )
    with db.session() as s:
        s.add(submission)
    return flask.redirect(
        flask.url_for(
            "submission_edit",
            event_id=event_id,
            submission_id=submission.id,
            extraction=extraction,
        )
    )


@app.get("/events/<string:event_id>/submissions/<int:submission_id>/edit")
def submission_edit(event_id, submission_id):
    event = db.get(db.Event, event_id)
    submission = db.get(
        db.Submission, submission_id, event_id, load=db.Submission.author
    )
    if not submission:
        raise Exception("Not found")
    return flask.render_template(
        "submission_edit.html.j2", event=event, submission=submission
    )


@app.get("/events/<string:event_id>/submissions/<int:submission_id>/files")
def submission_file(event_id, submission_id):
    submission = db.get(db.Submission, submission_id, event_id, load="author")
    if not submission:
        raise Exception("Not found")
    requested_file = flask.request.args.get("path")
    file = submission.path / requested_file
    if not file.exists():
        raise Exception("Not found")
    return flask.send_file(file.resolve())
