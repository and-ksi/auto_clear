import pandas as pd
import mysql.connector
from sqlalchemy import create_engine

mysql_url = "192.168.116.128"
# 创建 SQLAlchemy 引擎
engine = create_engine(f'mysql+mysqlconnector://root:and123456@{mysql_url}/zzwork_database')

# 查询数据
query = "SELECT * FROM zzData"  # 替换为你的查询语句
data_frame = pd.read_sql(query, engine)

# 导出数据到 Excel 文件
data_frame.to_excel('output.xlsx', index=False)

