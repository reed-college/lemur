from flask import Flask

app = Flask(__name__)
# For now we're manually turning on `debug`; we like this for a few
# reasons. Chief among them: much better logging; "hot reloading," in which
# changes to our code will show up without having to stop and restart the
# server.
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://zzy:mypassword@localhost/lemur'
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

from views import *

if __name__ == '__main__':
    app.run()



