import pandas as pa
import pylab as pl

df = pa.DataFrame()

logs = ["server_benchmark_log.json", "client_benchmark_log.json"]

for log in logs:
    df = df.append(pa.read_json(log))

df["data_decode"] = df["packets_decode"]*df["symbol_size"]
df["goodput"] = df["packets_decode"] / (df["time_end"] - df["time_decode"])

g = df.groupby(by=["direction","symbol_size", "symbols"])
gg = g.mean()["goodput"].reset_index()
gg.pivot_table('goodput', index = "symbols", columns=["symbol_size", "direction"]).plot()


pl.rcParams.update({
        'figure.autolayout': True,
        'lines.marker': "x",
        })

pl.savefig("test.eps")
