<thinking_mode>enabled</thinking_mode>

**1. Benar/salah pandangan user?**
Salah. Climber strategy submit 1 konservatif (0.76) justru BENAR untuk menetapkan baseline dan mengkalibrasi sistem scoring. Ini mengurangi risiko suboptimal submit 2 & 3 karena sudah punya anchor. Kuota bukan untuk setiap submit "maksimal", tapi untuk eksplorasi strategis. Dengan leaderboard top 3 semua ~0.835, climber yang mencapai sama pada submit 3 optimal (penggunaan ke-3 kuota tepat mencapai ceiling kompetisi).

**2. Strategi 3x submit paling optimal:**
- Submit 1: Baseline konservatif dengan model simple + validasi data drift (bukan submission "buta")
- Submit 2: Model utama dengan tuning moderat + ensembling ringan
- Submit 3: Full-ensemble dengan kalibrasi threshold optimal (learn dari gap submit 1→2 dan leaderboard public)

**3. Rekomendasi konkret sekarang:**
- Freeze semua eksperimen, fix seed
- Buat 3 checkpoint model dengan diversity: 1) LightGBM default, 2) CatBoost + feature engineering, 3) Stacking ensemble keduanya
- Submit sequence: checkpoint 1 → checkpoint 2 → stacking ensemble dengan threshold tuning berdasarkan leaderboard gap
- Jangan sentuh apa-apa setelah submit 3