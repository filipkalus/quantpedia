import investpy
from datetime import datetime
import pandas as pd

today = datetime.today().date()
# print(investpy.get_stock_countries())
# indecies = [x for x in investpy.indices.get_indices_list() if 'S&P' in x]
# print(indecies)
# index = investpy.indices.search_indices('name', 'S&P GSCI Commodity TR')
# print(index)
# bond_df = investpy.get_index_historical_data(index='S&P GSCI Commodity TR', country='world', from_date='01/01/1980',  to_date=today.strftime("%d/%m/%Y"))
# bond_df.rename(columns = {'Close':'close'}, inplace = True)
# bond_df.rename(columns = {'Date':'date'}, inplace = True)
# # print(bond_df.tail())

# output_path = "SPGSCITR.csv"
# bond_df.to_csv(output_path, columns = ['close'], index_label='date')

# print(investpy.bonds.get_bonds_list())

bonds = {
'AU10YT' :'australia',
'CA10YT' :'canada',
'DE10YT' :'germany',
'GB10YT' :'u.k.',
'IT10YT' :'italy',
'JP10YT' :'japan',
'US10YT' :'u.s.',
'CH10YT' :'switzerland',
'NZ10YT' :'new zealand'

}

yield_df = None
for country in bonds:
    bond = bonds[country]

    bond_df = investpy.get_bond_historical_data(bond=f'{bond} 10Y', from_date='01/01/1980',  to_date=today.strftime("%d/%m/%Y"))
    bond_df.rename(columns = {'Close':'yield'}, inplace = True)

    output_path = f"{country}.csv"
    bond_df.to_csv(output_path, columns = ['yield'], index_label='date')