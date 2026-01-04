import unittest

from automon.integrations.airtableWrapper import AirtableClient


class MyTestCase(unittest.TestCase):
    def test_userinfo(self):
        test = AirtableClient()
        if test.is_ready():
            self.assertTrue(test.user_info())
            self.assertTrue(test.bases_list())
            self.assertTrue(test.bases_get('Vendor Data'))

            base = test.bases_get('Vendor Data')

            fields = [
                test._api.table_field(
                    name="Name",
                )
            ]

            new_table = 'clutch.co'

            self.assertTrue(test.tables_list(base.id))

            if not test.tables_list(base.id).table_get(new_table):
                self.assertTrue(test.tables_create(baseId=base.id, name=new_table, fields=fields, description=''))


if __name__ == '__main__':
    unittest.main()
