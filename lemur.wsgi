# activate our virtualenv
activate_this = "/home/lemur/lemur/venv/bin/activate_this.py"
execfile(activate_this, dict(__file__=activate_this))

# prepend our path
import sys
sys.path.insert(0, "/home/lemur/lemur")

# wsgi hook
from lemur import app as application