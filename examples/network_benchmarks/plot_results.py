import pandas as pa
import pylab as pl

df = pa.DataFrame()

logs = ["server_benchmark_log.json", "client_benchmark_log.json"]

test_parameters = ["direction","symbol_size", "symbols"]

for log in logs:
    df = df.append(pa.read_json(log))

pl.rcParams.update({
        'figure.autolayout': True,
        # 'lines.marker': "o",
        'lines.linewidth': 0,
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

pl.close("all")

gg.pivot_table(index="decode_delay", columns=["direction"], values=["goodput"]).plot(logy=True)
pl.savefig("delay_vs_goodput.eps")

gg.pivot_table(index="decode_delay", columns=["direction"], values=["overhead"]).plot()
pl.savefig("delay_vs_overhead.eps")

gg.pivot_table(index="goodput", columns=["direction"], values=["overhead"]).plot(logx=True)
pl.savefig("goodput_vs_overhead.eps")
