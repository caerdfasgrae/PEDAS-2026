import urllib.request
import json
import sys

session_id = "ses_f3d83f616ffekLI23i6nQAaPw3"
url = f"http://localhost:4096/session/{session_id}/prompt_async"

briefing_text = """[PERSETUJUAN: BUAT DOKUMEN REVIEW SENIOR ML ENGINEER]

Rekan Agent di OpenCode,
Analisis Anda tentang strategi Submisi 3 (adaptif terhadap feedback Sub-02) dan persiapan review Senior ML Engineer ini SANGAT SEMPURNA, CERDAS, DAN DEWASA! 

Silakan buatkan berkas `docs/REVIEW_SENIOR_ML_ENGINEER.md` yang memuat:
1. 15 Tanya-Jawab Kritis (Architecture, Zero-Leakage CV, Bayes Threshold, GroupKFold vs Stratified, ECE Platt, Imbalance Handling).
2. Diagram alur data & arsitektur hybrid stacking.
3. Strategi evaluasi adaptif Submisi 3 pasca-hasil Submisi 2.
4. Lembar contek (*cheat-sheet*) istilah teknis untuk Abyan saat berbicara dengan seniornya.

Terima kasih banyak atas kolaborasi hebat ini!"""

payload = {
    "parts": [
        {
            "type": "text",
            "text": briefing_text
        }
    ]
}

req = urllib.request.Request(
    url, 
    data=json.dumps(payload).encode('utf-8'), 
    headers={'Content-Type': 'application/json'}, 
    method='POST'
)

try:
    with urllib.request.urlopen(req) as resp:
        print("Status:", resp.status)
except Exception as e:
    print(f"Failed: {e}")
    sys.exit(1)
