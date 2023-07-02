# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     custom_cell_magics: kql
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.2
#   kernelspec:
#     display_name: qreps
#     language: python
#     name: python3
# ---

# %%
"""Python Script Template."""
import pandas as pd
import matplotlib.pyplot as plt
from exps.plotting import plot_df_key, set_figure_params
from exps.environments.utilities import get_color, get_linestyle


# %%
import numpy as np
np.__version__

# %%
df.train_return

# %%
df.columns


# %%
def check(x):
    if type(x)==float:
        return -x
    else:
        return 0



# %%
# -(df.train_return).plot()

# # %%
# df

# # %%
# df.train_return.apply(check).plot()

# %%
df = pd.read_pickle("/home/djtom/bse/term3/reinforcement/termpaper/qreps/exps/environments/cart_pole/cart_pole_results.pkl")
df = df[df.time < 25]
# set_figure_params(serif=True)
fig, axes = plt.subplots(ncols=1, nrows=1)
plot_df_key(
    df=df,
    axes=axes,
    key="train_return",
    get_color=get_color,
    get_linestyle=get_linestyle,
)
plt.xlabel("Episode")
plt.ylabel("Reward")
plt.title(f"Cart-Pole")
# plt.legend(loc="best", frameon=False)
# plt.legend(bbox_to_anchor=(0.7, 0.32), loc="lower left", frameon=False)
# plt.savefig("cart_pole_results.pdf", bbox_inches="tight")
plt.show()

# %%
df.train_return=-df.train_return
min_val = df['train_return'].min()
max_val = df['train_return'].max()

# Normalize the column between 0 and 1
df['normalized_column'] = (df['train_return'] - min_val) / (max_val - min_val)

plt.plot(-df.normalized_column)

# %%
