# Synchrolog

## Installation
`pip install git+https://github.com/synchrolog/synchrolog-flask.git@master`

## Usage

Add access token to your application config

```python
app.config['SYNCHROLOG_ACCESS_TOKEN'] = '1234'
```

Call function `init` from `synchrolog_flask` module
```python
synchrolog_flask.init(app, use_queue=True, level=logging.INFO)
```

Full example
```python
import logging
import synchrolog_flask

from flask import Flask

app = Flask(__name__)
app.config['SYNCHROLOG_ACCESS_TOKEN'] = '123456'

synchrolog_flask.init(app, use_queue=True)

logger = app.logger

@app.route('/')
def hello():
    logger.info('HELLO')
    logger.error('ALOHA',)
    raise ValueError('EXCEPTION!!!')
```

## Configuration
 * use_queue: bool (default true and recommended) - if value is true than all logs to Synchrolog 
 will send in another thread with queue without blocking current request.
 if values is false, than every logger calls will block current request and will wait outcoming 
 request tp Synchrolog
 * level: int (default logging.root.level) - level of all logs in system.

## Note
if `FLASK_DEBUG` is `true` any exceptions will be handled by flask and 
converted to page with stacktrace and status equal to 200, so this library doesn't 
catch request exception in debug mode, so recommended way is to use this library only 
in production mode.

## For runtting tests
```bash
python3 -m unittest test/test.py
```