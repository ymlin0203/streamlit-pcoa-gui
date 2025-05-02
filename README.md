# 🧬 PCoA GUI v25.9

此應用為互動式 PCoA 視覺化工具，支援類別與連續型變因上色、ANOSIM 統計分析、自動與手動類型辨識與 permutation 設定。

## 使用方法

1. 安裝環境：

```
pip install -r requirements.txt
```

2. 執行應用：

```
streamlit run app.py
```

## 功能特色

- 顯示 PCoA 並依 metadata 變因上色
- 支援類別型與連續型色盤
- 排除缺失資料 NaN
- 支援 ANOSIM 統計測試（可自定 permutation 次數）
- 自動顯示比較組別名稱

## 檔案上傳需求

- `sample coordinate`：.tsv 或 .csv
- `proportion explained`：.tsv 或 .csv
- `metadata`：.xlsx 或 .csv（含 SampleID 欄）