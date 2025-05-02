import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.spatial.distance import pdist, squareform
from skbio.stats.distance import DistanceMatrix, anosim
import io

st.set_page_config(page_title="PCoA GUI", layout="wide")
st.title("🧬 PCoA GUI 🧬")

uploaded_sample = st.file_uploader("上傳 sample coordinate (.tsv or .csv)", type=["tsv", "csv"])
uploaded_proportion = st.file_uploader("上傳 proportion explained (.tsv or .csv)", type=["tsv", "csv"])
uploaded_metadata = st.file_uploader("上傳 metadata (.xlsx or .csv)", type=["xlsx", "csv"])

if uploaded_sample and uploaded_proportion and uploaded_metadata:
    try:
        df_sample = pd.read_csv(uploaded_sample, sep=None, engine="python")
        df_proportion = pd.read_csv(uploaded_proportion, sep=None, engine="python")

        if uploaded_metadata.name.endswith(".xlsx"):
            df_meta = pd.read_excel(uploaded_metadata, engine="openpyxl", dtype=str)
        else:
            df_meta = pd.read_csv(uploaded_metadata, dtype=str)

        df_sample.rename(columns={df_sample.columns[0]: "SampleID"}, inplace=True)
        df_meta.rename(columns={df_meta.columns[0]: "SampleID"}, inplace=True)
        df_merged = pd.merge(df_sample, df_meta, on="SampleID", how="inner")

        pc_cols = [col for col in df_sample.columns if col.startswith('PC')]
        x_axis = st.selectbox("選擇X軸", pc_cols, index=0)
        y_axis = st.selectbox("選擇Y軸", pc_cols, index=1)

        meta_cols = [col for col in df_meta.columns if col != "SampleID"]
        st.subheader("🧩 分類變因設定")
        color_var = st.selectbox("選擇上色變數", meta_cols)

        mode = st.radio("📌 請選擇該變數型態", ["自動偵測", "類別變因型", "連續變因型"], index=0)

        df_merged = df_merged[df_merged[color_var].notna() & (df_merged[color_var].str.strip() != "")]
        if df_merged.empty:
            st.error(f"🛑 變數「{color_var}」無有效資料。請確認 metadata 或改選其他變數。")
            st.stop()

        if mode == "類別變因型" or (mode == "自動偵測" and df_merged[color_var].nunique() <= 10):
            df_merged[color_var] = df_merged[color_var].astype(str)
            palette = st.selectbox("🎨 選擇色盤 (類別變因型)", ["Set1", "Set2", "tab10", "Dark2"])
            plot_kind = "categorical"
        else:
            palette = st.selectbox("🎨 選擇色盤 (連續變因型)", ["viridis", "plasma", "cividis"])
            plot_kind = "continuous"

        fig, ax = plt.subplots(figsize=(8, 6))
        if plot_kind == "categorical":
            sns.scatterplot(data=df_merged, x=x_axis, y=y_axis, hue=color_var,
                            palette=palette, s=60, edgecolor="black", ax=ax)
            ax.legend(title=color_var, bbox_to_anchor=(1.05, 1), loc='upper left')
        else:
            sc = ax.scatter(df_merged[x_axis], df_merged[y_axis],
                            c=pd.to_numeric(df_merged[color_var], errors="coerce"),
                            cmap=palette, s=60, edgecolors="black")
            cbar = plt.colorbar(sc, ax=ax)
            cbar.set_label(color_var)

        prop_x = df_proportion[df_proportion.iloc[:, 0] == x_axis].iloc[:, 1].values[0] * 100
        prop_y = df_proportion[df_proportion.iloc[:, 0] == y_axis].iloc[:, 1].values[0] * 100
        ax.set_xlabel(f"{x_axis} ({prop_x:.1f}%)")
        ax.set_ylabel(f"{y_axis} ({prop_y:.1f}%)")
        ax.set_title(f"PCoA colored by {color_var}")
        sns.despine()
        st.pyplot(fig)

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=300)
        st.download_button("💾 下載圖檔 (PNG)", data=buf.getvalue(),
                           file_name=f"{color_var}_PCoA.png", mime="image/png")

        st.subheader("📊 ANOSIM 統計結果")
        perm_count = st.number_input("Permutation 次數 (建議 ≥ 999)", min_value=10, step=100, value=999)

        try:
            matrix = squareform(pdist(df_merged[[x_axis, y_axis]], metric="euclidean"))
            valid_ids = df_merged["SampleID"]
            group_series = df_merged.set_index("SampleID").loc[valid_ids, color_var]
            distance_matrix = DistanceMatrix(matrix, ids=valid_ids)

            anosim_result = anosim(distance_matrix, group_series, permutations=perm_count)
            st.success(f"ANOSIM R = {anosim_result['test statistic']:.4f}, p-value = {anosim_result['p-value']:.4g}")
            st.caption(f"📌 比較組別（N = {group_series.nunique()}）: {', '.join(group_series.unique())}")
        except Exception as e:
            st.warning(f"⚠️ ANOSIM 分析失敗: {e}")

    except Exception as e:
        st.error(f"❗ 發生錯誤：{e}")
else:
    st.info("📥 請依序上傳 sample coordinate、proportion explained 與 metadata 檔案。")
