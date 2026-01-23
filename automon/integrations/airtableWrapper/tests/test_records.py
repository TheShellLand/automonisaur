import unittest
import json
import pandas
import numpy

from automon.integrations.airtableWrapper import AirtableClient


class MyTestCase(unittest.TestCase):
    def test_userinfo(self):
        test = AirtableClient()
        if test.is_ready():
            base = test.bases_get('Vendor Data')
            base_id = base.id

            agencies = open('automon/integrations/airtableWrapper/tests/records.json', 'r').read()
            agencies = json.loads(agencies)

            df = pandas.DataFrame(agencies['agencies'])
            df['services'] = df['services'].apply(lambda x: json.dumps(x))
            cols = df.columns.to_list()

            new_table = 'clutch.co'

            table_fields = []
            for col in cols:
                col_type = type(df[col][0])

                type_str = test._api.TableFieldType.str
                type_int = test._api.TableFieldType.int
                type_float = test._api.TableFieldType.float

                options_number = test._api.TableOptions.number

                if col_type == str:
                    table_fields.append(test._api.TableField(name=col, type=type_str))
                    continue

                if col_type == numpy.float64:
                    table_fields.append(test._api.TableField(name=col, type=type_float, options=options_number))
                    continue

                if col_type == numpy.int64:
                    table_fields.append(test._api.TableField(name=col, type=type_int, options=options_number))
                    continue

                table_fields.append(test._api.TableField(name=col))

                pass

            if not test.tables_list(base.id).table_get(new_table):
                self.assertTrue(
                    test.tables_create(baseId=base.id, name=new_table, fields=table_fields, description=''))

            records = test.records_list(base_id, new_table)

            records = []
            for index, series in df.iterrows():
                records.append(
                    test._api.Record(series.to_dict())
                )

            for record in records:
                test.records_create(baseId=base.id, records=[record], tableName=new_table)

            if __name__ == '__main__':
                unittest.main()
