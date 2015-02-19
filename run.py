#!/usr/bin/env python
import os
from app import app

app.config.from_pyfile('app.cfg', silent=True)
app.run(debug=True,host="0.0.0.0",port=8080)  