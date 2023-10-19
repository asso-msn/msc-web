import flask


def get_body_arguments(*args):
    return {k: v for k, v in flask.request.form.items() if k in args}
