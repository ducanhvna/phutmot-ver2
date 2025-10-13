import os
import pandas as pd
from datetime import datetime

df_orders = pd.read_parquet('data/Product/DmH.parquet')
df_orders.to_csv('data/Product/DmH.xlsx', index=False)

# Read backend\data\Product\DmNMM.parquet
df_orders = pd.read_parquet('data/Product/DmNMM.parquet')
df_orders.to_csv('data/Product/DmNMM.xlsx', index=False)

# read backend\data\Product\DmQTTG.parquet
df_orders = pd.read_parquet('data/Product/DmQTTG.parquet')
df_orders.to_csv('data/Product/DmQTTG.xlsx', index=False)

# read backend\data\Product\DmVbMM.parquet
df_orders = pd.read_parquet('data/Product/DmVbMM.parquet')        
df_orders.to_csv('data/Product/DmVbMM.xlsx', index=False)
print(df_orders.head())