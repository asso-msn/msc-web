import urllib.parse
import flask
from flask import current_app as app


@app.route("/login")
def login():
    dest = flask.url_for("login_discord")
    return flask.redirect(dest)


@app.route("/login/discord")
def login_discord():
    client_id = 826148612949147678
    discord_url = "https://discord.com/api/oauth2/authorize"
    callback_url = flask.url_for("login_discord_callback", _external=True)
    params = urllib.parse.urlencode(
        {
            "client_id": client_id,
            "redirect_uri": callback_url,
            "response_type": "code",
            "scope": "identify",
        }
    )
    return flask.redirect(f"{discord_url}?{params}")


@app.route("/login/discord/callback")
def login_discord_callback():
    code = flask.request.args.get("code")
    return {
        "code": code,
    }
