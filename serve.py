#!/usr/bin/env python3
import os

os.environ.setdefault('ENV', 'local')

from restriccion.wsgi import app


app.run(debug=True, host='0.0.0.0')
