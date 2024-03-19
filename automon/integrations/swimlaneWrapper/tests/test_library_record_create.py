# import os
# import json
# import unittest
# import swimlane
#
# from swimlane import Swimlane
# from automon import environ
#
# appId = environ('SWIMLANE_APP_ID')
# host = environ('SWIMLANE_HOST')
# user = environ('SWIMLANE_USERNAME')
# password = environ('SWIMLANE_PASSWORD')
#
#
# class MyTestCase(unittest.TestCase):
#
#     if host and user and password and appId:
#         def test_login(self):
#             swimlane = Swimlane(host, user, password, verify_ssl=False)
#
#             app = swimlane.apps.get(id=appId)
#
#             # records = app.records.get()
#             # records = app.records.search('.')
#
#             # swimlane.exceptions.UnknownField: "<App: AUTO ASSET COLLECTION (AAC)> has no field 'test'"
#             record = app.records.create(
#                 json=json.dumps(dict(
#                     string='string',
#                     int=1,
#                     list=[1, 2, 3],
#                     dict=dict(
#                         key='value'
#                     )
#                 ))
#             )
#
#             pass
#
#
# if __name__ == '__main__':
#     unittest.main()
