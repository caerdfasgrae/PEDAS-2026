import pandas as pd

pred = pd.read_csv("official/predict.csv")

news_keywords = ["kelurahan", "audensi", "kasus", "sidang", "sengketa", "warga", "ricuh", "demo", "bentrok", "polisi", "hukum", "pengadilan", "kejaksaan", "berita", "korban", "tewas", "laka", "kriminal", "polda", "polres", "bupati", "kantor"]

for kw in news_keywords:
    m = pred[pred["url"].str.contains(kw, case=False, na=False)]
    if len(m) > 0:
        print(f"\n=== Keyword: {kw} ({len(m)} matches) ===")
        for _, r in m.head(10).iterrows():
            print(f"  ID: {r['id']} | URL: {r['url']}")
