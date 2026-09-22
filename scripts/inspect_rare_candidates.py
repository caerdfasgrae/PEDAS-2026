import pandas as pd

df = pd.read_csv("official/predict.csv")
print("Total rows:", len(df))

keywords_violence = ["bunuh", "mati", "tembak", "senjata", "bom", "teror", "perang", "aniaya", "racun", "darah", "pedang", "pisau", "ancam", "eksekusi", "korban", "trap"]
print("\n=== POTENTIAL VIOLENCE MATCHES ===")
for kw in keywords_violence:
    matches = df[df["url"].str.contains(kw, case=False, na=False)]
    if len(matches) > 0:
        print(f"Keyword '{kw}': {len(matches)} matches")
        for _, r in matches.iterrows():
            print(f"   ID: {r['id']} | URL: {r['url']}")

keywords_pii = ["ktp", "nik", "kk", "bpjs", "paspor", "sim", "keluarga", "kependudukan", "dukcapil", "data-pribadi", "leak", "bocor"]
print("\n=== POTENTIAL PII MATCHES ===")
for kw in keywords_pii:
    matches = df[df["url"].str.contains(kw, case=False, na=False)]
    if len(matches) > 0:
        print(f"Keyword '{kw}': {len(matches)} matches")
        for _, r in matches.iterrows():
            print(f"   ID: {r['id']} | URL: {r['url']}")

keywords_fakeshop = ["shop", "toko", "store", "beli", "jual", "order", "diskon", "promo", "katalog", "belanja", "murah", "resmi"]
print("\n=== POTENTIAL FAKESHOP MATCHES ===")
for kw in keywords_fakeshop:
    matches = df[df["url"].str.contains(kw, case=False, na=False)]
    if len(matches) > 0:
        print(f"Keyword '{kw}': {len(matches)} matches")
        for _, r in matches.head(5).iterrows():
            print(f"   ID: {r['id']} | URL: {r['url']}")
