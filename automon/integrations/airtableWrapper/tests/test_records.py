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

            cols = {
                'name': str,
                'location': str,
                'rating': float,
                'reviews_count': float,
                'pricing_min': str,
                'hourly_rate': str,
                'company_size': str,
                'company_size_min': str,
                'company_size_max': str,
                'services': str,
                'verification': str,
                'budget_min': str,
                'hourly_rate_min': float,
                'hourly_rate_max': float,
                'employees': str,
                'employees_min': float,
                'employees_max': float,
                'employee_count': str,
                'min_project_size': str,

            }

            df = pandas.DataFrame(agencies)

            for col, col_type in cols.items():
                if col_type == str:
                    df[col] = df[col].apply(lambda x: str(x) if x else None)
                    continue

                if col_type == float:
                    df[col] = df[col].apply(lambda x: float(x) if x else None)
                    continue

                pass

            new_table = 'clutch.co'

            table_fields = []
            for col, col_type in cols.items():
                if col not in df.columns.to_list():
                    raise

                type_str = test._api.TableFieldType.str
                type_int = test._api.TableFieldType.int
                type_float = test._api.TableFieldType.float

                options_number = test._api.TableOptions.number

                if col_type == str:
                    table_fields.append(test._api.TableField(name=col, type=type_str))
                    continue

                if col_type == int or col_type == float:
                    table_fields.append(test._api.TableField(name=col, type=type_int, options=options_number))
                    continue

                pass

            if not test.tables_list(base.id).table_get(new_table):
                self.assertTrue(
                    test.tables_create(baseId=base.id, name=new_table, fields=table_fields, description=''))

            records = test.records_list(base_id, new_table)

            records = []
            for index, series in df.iterrows():
                series = series.dropna()
                records.append(
                    test._api.Record(series.to_dict())
                )

            for i in range(0, len(records), 10):
                chunk = records[i:i + 10]
                test.records_create(baseId=base.id, records=chunk, tableName=new_table)

            if __name__ == '__main__':
                unittest.main()
