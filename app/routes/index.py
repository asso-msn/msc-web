import flask
from flask import current_app as app


@app.route("/")
def index():
    return flask.redirect(
        flask.url_for("events_list"),
    )
