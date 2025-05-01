import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.spatial.distance import pdist, squareform
from skbio.stats.distance import DistanceMatrix, anosim
import io

st.set_page_config(page_title="PCoA GUI v25", layout="wide")
st.title("🧬 PCoA GUI v25 (分類修正+ANOSIM)")

uploaded_sample = st.file_uploader("上傳 sample coordinate (.tsv or .csv)", type=["tsv", "csv"])
uploaded_proportion = st.file_uploader("上傳 proportion explained (.tsv or .csv)", type=["tsv", "csv"])
uploaded_metadata = st.file_uploader("上傳 metadata (.xlsx or .csv)", type=["xlsx", "csv"])

if uploaded_sample and uploaded_proportion and uploaded_metadata:
    try:
        df_sample = pd.read_csv(uploaded_sample, sep=None, engine="python")
        df_proportion = pd.read_csv(uploaded_proportion, sep=None, engine="python")

        if uploaded_metadata.name.endswith(".xlsx"):
            df_meta = pd.read_excel(uploaded_metadata, engine="openpyxl")
        else:
            df_meta = pd.read_csv(uploaded_metadata)

        df_sample.rename(columns={df_sample.columns[0]: "SampleID"}, inplace=True)
        df_meta.rename(columns={df_meta.columns[0]: "SampleID"}, inplace=True)
        df_merged = pd.merge(df_sample, df_meta, on="SampleID", how="inner")

        pc_cols = [col for col in df_sample.columns if col.startswith('PC')]
        x_axis = st.selectbox("選擇X軸", pc_cols, index=0)
        y_axis = st.selectbox("選擇Y軸", pc_cols, index=1)

        meta_cols = [col for col in df_meta.columns if col != "SampleID"]
        st.subheader("🧩 分類變因型態設定")
        categorical_vars = st.multiselect("請選擇類別型變因 (例如 Criteria、010、011)", options=meta_cols)

        color_var = st.selectbox("選擇上色變數", meta_cols)

        if color_var in categorical_vars:
            df_merged[color_var] = df_merged[color_var].astype(str)
            palette = st.selectbox("選擇色盤 (類別型)", ["Set1", "Set2", "tab10", "Dark2"])
            plot_kind = "categorical"
        else:
            palette = st.selectbox("選擇色盤 (連續型)", ["viridis", "plasma", "cividis"])
            plot_kind = "continuous"

        fig, ax = plt.subplots(figsize=(8,6))

        if plot_kind == "categorical":
            sns.scatterplot(data=df_merged, x=x_axis, y=y_axis, hue=color_var, palette=palette, s=60, edgecolor="black", ax=ax)
            ax.legend(title=color_var, bbox_to_anchor=(1.05, 1), loc='upper left')
        else:
            sc = ax.scatter(df_merged[x_axis], df_merged[y_axis], c=df_merged[color_var], cmap=palette, s=60, edgecolors="black")
            cbar = plt.colorbar(sc, ax=ax)
            cbar.set_label(color_var)

        prop_x = df_proportion[df_proportion.iloc[:,0] == x_axis].iloc[:,1].values[0] * 100
        prop_y = df_proportion[df_proportion.iloc[:,0] == y_axis].iloc[:,1].values[0] * 100

        ax.set_xlabel(f"{x_axis} ({prop_x:.1f}%)")
        ax.set_ylabel(f"{y_axis} ({prop_y:.1f}%)")
        ax.set_title(f"PCoA colored by {color_var}")
        sns.despine()
        st.pyplot(fig)

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=300)
        st.download_button("💾 下載圖檔 (PNG)", data=buf.getvalue(), file_name=f"{color_var}_PCoA.png", mime="image/png")

        st.subheader("📊 ANOSIM 統計結果")
        try:
            matrix = squareform(pdist(df_merged[[x_axis, y_axis]], metric="euclidean"))
            distance_matrix = DistanceMatrix(matrix, ids=df_merged["SampleID"])
            anosim_result = anosim(distance_matrix, df_merged[color_var], permutations=999)
            st.success(f"ANOSIM R = {anosim_result.statistic:.4f}, p-value = {anosim_result.p_value:.4g}")
        except Exception as e:
            st.warning(f"⚠️ ANOSIM 分析失敗: {e}")

    except Exception as e:
        st.error(f"❗ 讀取或處理失敗：{e}")
else:
    st.info("請依序上傳 sample coordinate、proportion explained 與 metadata 檔案。")
