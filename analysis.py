"""Share of dogs and cats leaving the shelter that went home, by year, 2014-2024.

Reads austin_outcomes.csv from the same folder as this script, cleans it step by
step (printing how many rows are left after each step), and saves two charts
next to the script: dogs_went_home.png and cats_went_home.png.

Run it with:  python analysis.py
Needs pandas and matplotlib.
"""
from pathlib import Path
import textwrap

import matplotlib
matplotlib.use("Agg")                      # draw to files only, no window
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent     # the folder this script lives in
CSV = HERE / "austin_outcomes.csv"

if not CSV.exists():
    raise SystemExit(f"Could not find {CSV.name} next to analysis.py (looked in {HERE})")

# --- 1. read the file ---------------------------------------------------------
df = pd.read_csv(CSV)
print(f"Rows in the file:                                   {len(df):>8,}")

# --- 2. cleaning rules (each one prints the rows left) ------------------------

# Rule 1: drop rows with no Outcome Type, because we can't tell where those animals went.
df = df[df["Outcome Type"].notna()]
print(f"After removing rows with a blank Outcome Type:      {len(df):>8,}")

# Rule 2: keep only dogs and cats, so birds, livestock and wildlife ("Other") don't dilute the shares.
df = df[df["Animal Type"].isin(["Dog", "Cat"])]
print(f"After keeping only dogs and cats:                   {len(df):>8,}")

# Rule 3: add a True/False column that counts both Return to Owner and Rto-Adopt as "went home".
# (Adds a column only, so the row count does not change.)
df["went_home"] = df["Outcome Type"].isin(["Return to Owner", "Rto-Adopt"])
print(f"After adding the went_home column:                  {len(df):>8,}")

# Rule 4: add a year column from the first four characters of DateTime (works for both date formats in the file).
# (Adds a column only, so the row count does not change.)
df["year"] = df["DateTime"].str[:4].astype(int)
print(f"After adding the year column:                       {len(df):>8,}")

# Rule 5: keep only the full years 2014-2024; the file starts in Oct 2013 and ends in early May 2025.
df = df[df["year"].between(2014, 2024)]
print(f"After keeping only the full years 2014-2024:        {len(df):>8,}")

# --- 3. charts ----------------------------------------------------------------
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRID, AXIS, LINE = "#e1e0d9", "#c3c2b7", "#2a78d6"
plt.rcParams["font.family"] = "DejaVu Sans"


def make_chart(animal, title, ylim, yticks, first_label_dy, outfile):
    """Line chart of the share of `animal` outcome rows that went home, by year."""
    rows = df[df["Animal Type"] == animal]
    share = rows.groupby("year")["went_home"].mean() * 100
    print(f"\n{animal} share that went home, by year:")
    print(share.round(1).to_string(header=False))

    fig, ax = plt.subplots(figsize=(10, 5.8), dpi=200, facecolor=SURFACE)
    fig.subplots_adjust(left=0.085, right=0.95, top=0.76, bottom=0.17)
    ax.set_facecolor(SURFACE)

    ax.plot(share.index, share.values, color=LINE, linewidth=2,
            solid_capstyle="round", solid_joinstyle="round", zorder=3)
    ax.scatter(share.index, share.values, s=8**2, color=LINE,
               edgecolors=SURFACE, linewidths=2, zorder=4)

    ax.set_ylim(0, ylim)                   # percentage axis starts at zero
    ax.set_xlim(2013.6, 2024.4)
    ax.set_xticks(range(2014, 2025))
    ax.set_yticks(yticks)
    ax.set_yticklabels([f"{t}%" for t in yticks])
    ax.grid(axis="y", color=GRID, linewidth=1, linestyle="-")
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(AXIS)
    ax.spines["bottom"].set_linewidth(1)
    ax.tick_params(axis="both", length=0, labelsize=10, labelcolor=MUTED, pad=8)

    def label(x, dy):                      # label only the first year, the peak and the last year
        y = share[x]
        ax.annotate(f"{y:.1f}%", (x, y), xytext=(0, dy), textcoords="offset points",
                    ha="center", va="bottom" if dy > 0 else "top",
                    fontsize=11, color=INK, fontweight="bold")
    label(2014, first_label_dy)
    label(share.idxmax(), 11)
    label(2024, 11)

    fig.text(0.085, 0.93, title, ha="left", va="top", fontsize=17,
             color=INK, fontweight="bold", linespacing=1.25)
    fig.text(0.085, 0.045,
             f"Share of {animal.lower()} outcome rows that were Return to Owner or Rto-Adopt, "
             "by year of outcome, full years 2014–2024. Rows with a blank outcome removed.",
             ha="left", va="bottom", fontsize=8.5, color=INK2)

    fig.savefig(HERE / outfile, facecolor=SURFACE)
    plt.close(fig)
    print(f"Saved {outfile}")


make_chart(
    "Dog",
    "\n".join(textwrap.wrap(
        "The share of dogs leaving the shelter that went home fell from about 28% in 2014 to about 15% in 2024", 62)),
    ylim=35, yticks=[0, 10, 20, 30], first_label_dy=-14, outfile="dogs_went_home.png")

make_chart(
    "Cat",
    "Few cats leaving the shelter went home:\n4.9% in 2014, 2.9% in 2024",
    ylim=7, yticks=[0, 2, 4, 6], first_label_dy=11, outfile="cats_went_home.png")
