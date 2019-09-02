import logging
import unittest
from unittest import mock

from flask import Flask
from werkzeug.exceptions import abort

import synchrolog_flask


class Object:
    pass


def mocked_request_post(*args, **kwargs):
    obj = Object()
    obj.status_code = 200
    return obj


def mocked_extract_tb(tb, limit=None):
    obj = Object()
    obj.filename = __file__
    obj.lineno = '1'
    return [obj]


def mocked_format_tb(tb):
    return 'TRACEBACK'


class MiddlewareTestCase(unittest.TestCase):

    @staticmethod
    def create_app(level, use_queue):
        app = Flask(__name__)
        app.config['SYNCHROLOG_ACCESS_TOKEN'] = '123'

        synchrolog_flask.init(app, level=level, use_queue=use_queue)
        return app

    def setUp(self) -> None:
        app = self.create_app(logging.DEBUG, use_queue=False)

        self.app = app
        self.client = app.test_client()

    def test_get_time(self):
        @self.app.route('/synchrolog-time')
        def view():
            return None

        response = self.client.get('/synchrolog-time')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'time': mock.ANY})

    @mock.patch('requests.post', side_effect=mocked_request_post)
    def test_abort_error(self, post_mock):
        @self.app.route('/')
        def view():
            abort(404)

        response = self.client.get('/')
        self.assertEqual(response.status_code, 404)
        post_mock.assert_called()

    @mock.patch('requests.post', side_effect=mocked_request_post)
    def test_abort_use_queue(self, post_mock):
        app = self.create_app(logging.DEBUG, use_queue=True)
        client = app.test_client()

        @app.route('/')
        def view():
            abort(404)

        response = client.get('/')
        self.assertEqual(response.status_code, 404)
        post_mock.assert_called()

    @mock.patch('requests.post', side_effect=mocked_request_post)
    def test_above_level(self, post_mock):
        app = self.create_app(logging.ERROR, use_queue=True)
        client = app.test_client()

        @app.route('/')
        def view():
            app.logger.info('SOME MSG')
            return {}, 200

        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        post_mock.assert_not_called()

    @mock.patch('requests.post', side_effect=mocked_request_post)
    def test_info_level(self, post_mock):
        app = self.create_app(logging.INFO, use_queue=True)
        client = app.test_client()

        @app.route('/')
        def view():
            app.logger.info('SOME MSG')
            return {}, 200

        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        post_mock.assert_called()

    @mock.patch('requests.post', side_effect=mocked_request_post)
    def test_log_json_without_header(self, post_mock):
        app = self.create_app(logging.INFO, use_queue=True)
        client = app.test_client()

        @app.route('/')
        def view():
            app.logger.info('SOME MSG')
            return {}, 200

        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        post_mock.assert_called()
        post_mock.assert_called_with(
            headers={'Authorization': 'Basic 123'},
            json={
                'event_type': 'log', 'timestamp': mock.ANY,
                'anonymous_id': mock.ANY, 'user_id': mock.ANY,
                'source': 'backend',
                'log': {'timestamp': mock.ANY, 'message': 'SOME MSG'},
            },
            url='https://input.synchrolog.com/v1/track-backend',
        )
        self.assertIsNotNone(post_mock.call_args[1]['json']['anonymous_id'])

    @mock.patch('requests.post', side_effect=mocked_request_post)
    def test_log_json_with_headers(self, post_mock):
        app = self.create_app(logging.INFO, use_queue=True)
        client = app.test_client()

        @app.route('/')
        def view():
            app.logger.info('SOME MSG')
            return {}, 200

        client.set_cookie('/',  'synchrolog_user_id', '1')
        client.set_cookie('/',  'synchrolog_anonymous_id', '2')
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        post_mock.assert_called()
        post_mock.assert_called_with(
            headers={'Authorization': 'Basic 123'},
            json={
                'event_type': 'log', 'timestamp': mock.ANY,
                'anonymous_id': '2', 'user_id': '1',
                'source': 'backend',
                'log': {'timestamp': mock.ANY, 'message': 'SOME MSG'},
            },
            url='https://input.synchrolog.com/v1/track-backend',
        )
        self.assertIsNotNone(post_mock.call_args[1]['json']['anonymous_id'])

    @mock.patch('traceback.format_tb', side_effect=mocked_format_tb)
    @mock.patch('traceback.extract_tb', side_effect=mocked_extract_tb)
    @mock.patch('requests.post', side_effect=mocked_request_post)
    def test_log_traceback(self, post_mock, mocked_format_tb, mocked_extract_tb):
        app = self.create_app(logging.INFO, use_queue=False)
        client = app.test_client()
        print('CLIENT')
        @app.route('/')
        def view():
            try:
                raise ValueError('ERR')
            except ValueError:
                app.logger.exception('SOME MSG', exc_info=True)

            return {}, 200

        client.set_cookie('/', 'synchrolog_user_id', '1')
        client.set_cookie('/', 'synchrolog_anonymous_id', '2')
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        post_mock.assert_called()

        post_mock.assert_called_with(
            headers={'Authorization': 'Basic 123'},
            json={
                'event_type': 'log',
                'timestamp': mock.ANY,
                'anonymous_id': '2', 'user_id': '1',
                'source': 'backend',
                'error': {
                    'status': '500', 'description': 'SOME MSG', 'backtrace': 'TRACEBACK', 'ip_address': '127.0.0.1',
                    'user_agent': 'werkzeug/0.15.5', 'file_name': __file__, 'line_number': '1', 'file': mock.ANY
                },
            },
            url='https://input.synchrolog.com/v1/track-backend-error',
        ),

        self.assertIsNotNone(post_mock.call_args[1]['json']['anonymous_id'])
