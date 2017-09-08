from influxdb import DataFrameClient
from pidas.settings import DATABASE

client = DataFrameClient(DATABASE['HOST'], DATABASE['PORT'], DATABASE['USER'], DATABASE['PASSWORD'], DATABASE['NAME'])


result_set = client.query('select * from temperatures;')

if not result_set:
    print("Serie is empty or doesn't exist")
else:
    print(result_set)
