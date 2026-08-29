"""
Generates a small set of polished, LinkedIn-ready figures summarizing the
water reservoir trophic-state analysis (Sentinel-2 + Random Forest).

Run inside the `embalses` conda env:
    conda activate embalses
    python scripts/linkedin_figures.py
"""
import warnings
warnings.filterwarnings("ignore")

import os
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from rasterio.plot import plotting_extent
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Patch
from matplotlib.colors import LinearSegmentedColormap
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score, cohen_kappa_score

from funciones import nequalize

# ---------------------------------------------------------------------------
# Palette (from the org data-viz palette: references/palette.md)
# ---------------------------------------------------------------------------
INK = "#0b0b0b"
INK_SECOND = "#52514e"
INK_MUTED = "#898781"
GRID = "#e1e0d9"
SURFACE = "#fcfcfb"
PAGE = "#f9f9f7"

BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
YELLOW = "#eda100"
MAGENTA = "#e87ba4"
GREEN = "#008300"
VIOLET = "#4a3aa7"
RED = "#e34948"

CLASS_COLORS = {  # trophic-state classes, ordered clear -> dense algae
    "Agua Clara": BLUE,
    "Alga Difusa": YELLOW,
    "Alga Densa": RED,
}

OUT_DIR = "assets/linkedin"
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Arial", "DejaVu Sans"],
    "text.color": INK,
    "axes.edgecolor": GRID,
    "axes.labelcolor": INK_SECOND,
    "xtick.color": INK_MUTED,
    "ytick.color": INK_MUTED,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
})

CREDIT = "Sentinel-2 L2A  ·  Embalses de Córdoba, Argentina  ·  J. Arellana"


def add_credit(fig, y=0.015):
    fig.text(0.5, y, CREDIT, ha="center", va="bottom",
              fontsize=10.5, color=INK_MUTED)


# ---------------------------------------------------------------------------
# FIGURE 1 — Study area hero map (Norte + Sur true color, reservoirs labeled)
# ---------------------------------------------------------------------------
def figure_study_area():
    poly_all = gpd.read_file("Poligonos/Embalses_unificado.shp")
    poly_all = poly_all.drop(columns=["path", "objeto", "entidad", "layer"])

    norte_names = ["Cruz del Eje", "San Roque", "El Cajon"]
    sur_names = ["Cerro Pelado", "Los Molinos", "Rio Tercero", "La ViÃ±a",
                 "Usina 3", "Piedra Mora", "Arroyo Corto"]

    label_fix = {"La ViÃ±a": "La Viña"}

    fig, axes = plt.subplots(1, 2, figsize=(12, 7.2), constrained_layout=True)
    fig.patch.set_facecolor(SURFACE)

    for ax, tif, names, title in [
        (axes[0], "ImagenesSentinel/Norte_20mTODOS.tif", norte_names, "Zona Norte"),
        (axes[1], "ImagenesSentinel/Sur_20mTODOS.tif", sur_names, "Zona Sur"),
    ]:
        with rasterio.open(tif) as src:
            bands = src.read()
        extent = plotting_extent(src)
        rgb = nequalize(bands[[3, 2, 1]], p=3, nodata=None)
        rgb = rgb ** 0.85  # mild gamma lift, closer to a natural true-color look
        rgb = np.einsum("kij->ijk", rgb)

        ax.imshow(rgb, extent=extent)
        sub = poly_all[poly_all["fna"].isin(names)]
        sub.boundary.plot(ax=ax, edgecolor=YELLOW, linewidth=1.6)

        for _, row in sub.iterrows():
            c = row.geometry.centroid
            name = label_fix.get(row["fna"], row["fna"])
            ax.annotate(name, (c.x, c.y), color="white", fontsize=9.5,
                        weight="bold", ha="center", va="center",
                        path_effects=[
                            matplotlib.patheffects.withStroke(linewidth=2.5, foreground="black")
                        ])

        ax.set_title(title, fontsize=15, weight="bold", color=INK, pad=10)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

    fig.suptitle("Reservoirs of Córdoba, Argentina — Sentinel-2 True Color",
                  fontsize=19, weight="bold", color=INK, y=1.06)
    add_credit(fig, y=-0.03)
    fig.savefig(f"{OUT_DIR}/01_study_area.png", dpi=220, bbox_inches="tight")
    plt.close(fig)
    print("saved 01_study_area.png")


# ---------------------------------------------------------------------------
# Shared: train Random Forest on Los Molinos ROIs
# ---------------------------------------------------------------------------
def train_rf():
    path = "ImagenesSentinel/StackRecortado_Molinos_B1a8_11_12.tif"
    radiosM = gpd.read_file("Poligonos/Entrenamiento_2022/TrainingMolinosPoligonos.shp")
    names = list(set(radiosM["MC_name"]))
    pols = radiosM.query("MC_name in @names").copy()
    pols["CLASE"] = pols["MC_name"]

    clases = sorted(set(pols["CLASE"]))
    clase_dict = {c: i for i, c in enumerate(clases)}

    with rasterio.open(path) as src:
        d = src.count
        X = np.zeros([0, d], dtype=np.float32)
        Y = np.zeros([0], dtype=int)
        for _, row in pols.iterrows():
            clip, _ = mask(src, [row["geometry"]], crop=True, nodata=None)
            dd, x, y = clip.shape
            pix = list(clip.reshape([dd, x * y]).T)
            pix = [p for p in pix if not (p == None).prod()]  # noqa: E711
            DX = np.array(pix)
            DY = np.repeat(clase_dict[row["CLASE"]], len(pix))
            X = np.concatenate((X, DX))
            Y = np.concatenate((Y, DY))

    X_train, X_test, Y_train, Y_test = train_test_split(
        X, Y, stratify=Y, test_size=0.25, random_state=7)

    clf = RandomForestClassifier(n_estimators=200, max_depth=12, random_state=7)
    clf.fit(X_train, Y_train)
    Y_pred = clf.predict(X_test)

    acc = accuracy_score(Y_test, Y_pred)
    kappa = cohen_kappa_score(Y_test, Y_pred)
    M = confusion_matrix(Y_test, Y_pred)

    with rasterio.open(path) as src:
        full = src.read()
    poly_molinos_area = pols.unary_union.envelope
    s2_clip, clip_transform = mask(dataset=rasterio.open(path), shapes=[poly_molinos_area], crop=True)
    d2, x2, y2 = s2_clip.shape
    Y_full_pred = clf.predict(s2_clip.reshape([d2, x2 * y2]).T)
    classified = Y_full_pred.reshape([x2, y2]).astype("float64")

    valid_mask = s2_clip[0] != 0
    classified[~valid_mask] = np.nan

    rgb = np.einsum("kij->ijk", nequalize(s2_clip[[3, 2, 1]], p=2, nodata=None))

    bandas = ["Band 1", "Blue", "Green", "Red", "Band 5", "Band 6", "Band 7", "NIR", "SWIR1", "SWIR2"]

    return dict(clases=clases, acc=acc, kappa=kappa, M=M, clf=clf,
                rgb=rgb, classified=classified, bandas=bandas,
                pixels_por_clase={c: int((Y == clase_dict[c]).sum()) for c in clases})


# ---------------------------------------------------------------------------
# FIGURE 2 — RGB vs Random Forest classification map (Los Molinos)
# ---------------------------------------------------------------------------
def figure_classification(res):
    clases = res["clases"]
    h, w = res["rgb"].shape[:2]
    ax_w = 4.6
    fig_w = ax_w * 2 * 1.05
    fig_h = fig_w * (h / (2 * w)) * 0.55 + 1.6
    fig_h = float(np.clip(fig_h, 6.5, 9.5))

    fig, axes = plt.subplots(1, 2, figsize=(fig_w, fig_h))
    fig.patch.set_facecolor(SURFACE)

    axes[0].imshow(res["rgb"])
    axes[0].set_title("Sentinel-2 True Color", fontsize=13.5, weight="bold", color=INK, pad=8)

    cmap = LinearSegmentedColormap.from_list(
        "trophic", [CLASS_COLORS[c] for c in clases], N=len(clases))
    axes[1].imshow(res["classified"], cmap=cmap, vmin=-0.5, vmax=len(clases) - 0.5)
    axes[1].set_title("Random Forest Classification", fontsize=13.5, weight="bold", color=INK, pad=8)

    for ax in axes:
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

    handles = [Patch(facecolor=CLASS_COLORS[c], label=c) for c in clases]
    fig.legend(handles=handles, loc="lower center", ncol=len(clases),
               frameon=False, bbox_to_anchor=(0.5, 0.045), fontsize=11.5)

    fig.subplots_adjust(top=0.80, bottom=0.14, left=0.03, right=0.97, wspace=0.06)

    fig.text(0.5, 0.965, "Los Molinos Reservoir — Algal Bloom Classification",
              ha="center", va="top", fontsize=18, weight="bold", color=INK)
    fig.text(0.5, 0.905,
              f"Random Forest · overall accuracy {res['acc']*100:.0f}%  ·  Cohen's κ {res['kappa']:.2f}",
              ha="center", va="top", fontsize=12, color=INK_SECOND)

    add_credit(fig, y=0.02)
    fig.savefig(f"{OUT_DIR}/02_classification.png", dpi=220)
    plt.close(fig)
    print("saved 02_classification.png")


# ---------------------------------------------------------------------------
# FIGURE 3 — Model performance panel: confusion matrix + feature importance
# ---------------------------------------------------------------------------
def figure_model_panel(res):
    clases = res["clases"]
    M = res["M"]
    M_norm = M / M.sum(axis=1, keepdims=True)

    fig, axes = plt.subplots(1, 2, figsize=(12, 6.6))
    fig.patch.set_facecolor(SURFACE)

    # --- confusion matrix ---
    ax = axes[0]
    im = ax.imshow(M_norm, cmap=LinearSegmentedColormap.from_list("seq", ["#cde2fb", BLUE, "#0d366b"]),
                    vmin=0, vmax=1)
    ax.set_xticks(range(len(clases)))
    ax.set_yticks(range(len(clases)))
    ax.set_xticklabels(clases, rotation=20, ha="right", fontsize=10)
    ax.set_yticklabels(clases, fontsize=10)
    ax.set_xlabel("Predicted", fontsize=11)
    ax.set_ylabel("Actual", fontsize=11)
    for i in range(len(clases)):
        for j in range(len(clases)):
            val = M_norm[i, j]
            txt_color = "white" if val > 0.55 else INK
            ax.text(j, i, f"{val*100:.0f}%", ha="center", va="center",
                     fontsize=12, weight="bold", color=txt_color)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title("Confusion Matrix (test set)", fontsize=13.5, weight="bold", color=INK, pad=12)

    # --- feature importance ---
    ax2 = axes[1]
    importances = res["clf"].feature_importances_
    order = np.argsort(importances)
    bandas_sorted = [res["bandas"][i] for i in order]
    vals_sorted = importances[order]
    colors = [BLUE if v == vals_sorted.max() else "#9ec5f4" for v in vals_sorted]
    ax2.barh(bandas_sorted, vals_sorted, color=colors, height=0.62)
    ax2.set_xlabel("Feature importance", fontsize=11)
    ax2.set_title("Which Sentinel-2 bands matter most", fontsize=13.5, weight="bold", color=INK, pad=12)
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.grid(axis="x", color=GRID, linewidth=0.8, zorder=0)
    ax2.set_axisbelow(True)

    fig.subplots_adjust(top=0.78, bottom=0.13, left=0.11, right=0.97, wspace=0.35)

    fig.text(0.5, 0.965, "Random Forest Model Diagnostics",
              ha="center", va="top", fontsize=18, weight="bold", color=INK)
    fig.text(0.5, 0.905,
              f"Overall accuracy {res['acc']*100:.0f}%  ·  Cohen's κ {res['kappa']:.2f}  ·  "
              f"{sum(res['pixels_por_clase'].values())} labeled pixels across {len(clases)} classes",
              ha="center", va="top", fontsize=11.5, color=INK_SECOND)

    add_credit(fig, y=0.015)
    fig.savefig(f"{OUT_DIR}/03_model_diagnostics.png", dpi=220)
    plt.close(fig)
    print("saved 03_model_diagnostics.png")


if __name__ == "__main__":
    import matplotlib.patheffects  # noqa: E402

    figure_study_area()
    res = train_rf()
    figure_classification(res)
    figure_model_panel(res)
    print("\nAll figures written to", OUT_DIR)
