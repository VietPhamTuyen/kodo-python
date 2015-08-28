import pandas as pa
import pylab as pl

df = pa.DataFrame()

logs = ["server_benchmark_log.json", "client_benchmark_log.json"]

test_parameters = ["direction","symbol_size", "symbols"]

for log in logs:
    df = df.append(pa.read_json(log))

pl.rcParams.update({
        'figure.autolayout': True,
        'lines.marker': "x",
        "legend.fontsize": "xx-small",
        })

# only look at download measurements
df = df.query("role == 'client' and direction == 'server_to_client' or role == 'server' and direction == 'client_to_server'")

df["data_decode"] = df["packets_decode"]*df["symbol_size"]
df["decode_delay"] = df["time_end"] - df["time_decode"]
df["goodput"] = df["data_decode"] / df["decode_delay"]
df["overhead"] = (df["packets_total"] - df["packets_decode"]) / df["packets_decode"]

g = df.groupby(by=test_parameters)
gg = g.mean().reset_index()

gg.pivot_table(values='goodput', index="decode_delay", columns=["direction"]).plot(logy=True)
pl.ylabel("goodput")
pl.savefig("test.eps")

gg.pivot_table(values='overhead', index="decode_delay", columns=["direction"]).plot()
pl.ylabel("overhead")
pl.savefig("test2.eps")

gg.pivot_table(values='overhead', index="goodput", columns=["direction"]).plot(logx=True)
pl.ylabel("overhead")
pl.savefig("test3.eps")
