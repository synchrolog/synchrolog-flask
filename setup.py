from setuptools import setup

setup(
    name='synchrolog-flask',
    version='0.0.1',
    packages=['synchrolog_flask'],
    url='',
    license='',
    author='',
    author_email='',
    description='Flask middleware library for sending logs to Synchrolog ',
    install_requires=[
        'certifi',
        'chardet',
        'Click',
        'Flask',
        'idna',
        'itsdangerous',
        'Jinja2',
        'MarkupSafe',
        'requests',
        'urllib3',
        'Werkzeug',
    ],
)
