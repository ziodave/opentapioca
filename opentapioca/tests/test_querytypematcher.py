import re
import unittest

import requests_mock

from opentapioca.typematcher.querytypematcher import QueryTypeMatcher


class TestQueryTypeMatcher(unittest.TestCase):

    def test__(self):
        tm = QueryTypeMatcher()
        self.assertTrue(tm.is_subclass('Q1047113', 'Q35120'))

        tm_1 = QueryTypeMatcher('P1234')
        self.assertFalse(tm_1.is_subclass('Q1047113', 'Q35120'))

        # Mock the next request to check that we're using the cached data.
        with requests_mock.Mocker(real_http=True) as mocker:
            mocker.get(re.compile('.*'), status_code=500)
            self.assertTrue(tm.is_subclass('Q1047113', 'Q35120'))
