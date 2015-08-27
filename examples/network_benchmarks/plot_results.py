import pandas as pa

df_server = pa.read_json("server_benchmark_log.json")
df_client = pa.read_json("client_benchmark_log.json")
