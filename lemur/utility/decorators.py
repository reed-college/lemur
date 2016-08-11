# This file consists of all the customized decorators
import sys
sys.path.append('..')
# Libraries
# Standard library
from functools import wraps
import linecache

# Third-party libraries
from flask import render_template, jsonify, redirect, url_for
from flask.ext.login import current_user

# Local
from lemur import (app, db)
ds = db.session


# --- Decorators ---
# This handler has not been added to view functions.
# This is a decorator used to handle exceptions
# It will not be activated if the app is in debug mode
# since debug mode can generate more detailed error feedback
# already
def db_exception_handler(request_type, msg="Unknown bug. "):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if app.debug is True:
                ret = f(*args, **kwargs)
                return ret
            else:
                try:
                    ret = f(*args, **kwargs)
                    return ret
                except Exception:
                    db.session.rollback()
                    exc_type, exc_obj, tb = sys.exc_info()
                    frame = tb.tb_frame
                    lineno = tb.tb_lineno
                    filename = frame.f_code.co_filename
                    linecache.checkcache(filename)
                    line = linecache.getline(filename, lineno, frame.f_globals)
                    err_msg = 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno,
                                                                           line.strip(), exc_obj)
                    if request_type == 'POST':
                        return jsonify(success=False, data=err_msg)
                    else:
                        return render_template('error_400.html',
                                               err_msg=err_msg), 400
        return wrapped
    return decorator


# A decorator used to check the user's permission to access the current page
# If the user doesn't have access, redirect to the login page
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# A decorator that avoids the function to raise an exception but return
# a None instead
def failure_handler(f):
    def f_try(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except:
            return None
    return f_try
