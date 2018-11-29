from .app import app
from .auth import *
from .index import *
from .thumb import *

if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host="0.0.0.0", debug=True, port=80)
