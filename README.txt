PCoA GUI v28 說明文件
-----------------------

本應用提供以下功能：
- 自動讀取 sample coordinate, proportion explained, metadata 檔案
- 自動上色並區分類別/連續型變因
- 可切換主成分 (PC1, PC2...)
- 自選色盤樣式
- 執行 ANOSIM 統計分析，顯示 R 值與 p-value
- 自動排除含 NaN 的資料點
- 將類別變因統一為字串顯示（避免顯示小數）

使用方式：
1. 安裝 Python（建議 Python 3.9+）
2. 安裝必要套件：
   pip install -r requirements.txt
3. 雙擊 `start_app.bat` 或執行：
   streamlit run pcoa_streamlit_gui.py
