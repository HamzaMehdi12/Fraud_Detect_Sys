from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment

env = StreamExecutionEnvironment.get_execution_environment()
t_env = StreamTableEnvironment.create(env)

t_env.execute_sql("""
  CREATE TABLE Transactions (
    transaction_id STRING,
    amount DOUBLE,
    ...
  ) WITH (
    'connector' = 'kafka',
    'topic' = 'transactions',
    'properties.bootstrap.servers' = 'kafka:9092',
    'format' = 'json'
  )
""")

result = t_env.sql_query("""
  SELECT transaction_id, 
         amount,
         CASE WHEN amount > 10000 THEN 1 ELSE 0 END AS high_value
  FROM Transactions
""")

result.execute().print()