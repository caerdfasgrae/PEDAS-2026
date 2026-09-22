import json
import requests

PROMPT = """You are a competitive machine learning grandmaster and senior cybersecurity data scientist specializing in national data competitions.

CONTEXT & PROBLEM:
We are competing in PeDaS 2026 (Pesta Data Nasional), organized by PANDI (the official .id Internet Domain Name Registry of Indonesia) and APTIKOM.
The competition task is to classify .id domain threats into 9 canonical IDADX classes:
['online gambling', 'phishing', 'other', 'spam', 'malware', 'brand', 'fakeshop', 'violence', 'piiexposure']

OFFICIAL EVALUATION CODE (from scripts/evaluate_official.py):
```python
# Kelas tanpa contoh di ground truth tidak masuk rata-rata.
scoring_classes = sorted(set(y_true))
score = f1_score(y_true, y_pred, labels=scoring_classes,
                 average="macro", zero_division=0)
```

DATASET METRICS:
1. Training set (official/training.csv): 8,400 rows:
   - online gambling: 5,447 (64.85%)
   - phishing: 2,253 (26.82%)
   - other: 284 (3.38%)
   - spam: 185 (2.20%)
   - malware: 179 (2.13%)
   - brand: 45 (0.54%)
   - fakeshop: 5 (0.06%)
   - violence: 1 (0.01%) - URL: "https://********.id/gedung-eks-bioskop-liberty-kembali-disoal-kelurahan-jembatan-besi-gelar-audensi/"
   - piiexposure: 1 (0.01%) - URL: "https://www.******.co.id/tag/gedung-eks-bioskop-liberty/"
2. Test set (official/predict.csv): exactly 1,500 rows.

OFFICIAL LIVE SCOREBOARD (Current Standings):
1. Kusut Kusut Reborn: 0.834969292 (Submitted twice with exact identical score!)
2. Stargazer: 0.834554025
3. AiAvenger: 0.809461086
4. The Datapuff Girls: 0.80850684
5. IF ELSE: 0.806411964
6. Princess Theory: 0.766672619
7. BDCA: 0.76599388
8. TIFIS TIFIS (Our Team - Submission 1): 0.744171684
9. Oryphem: 0.74209154
10. datascape: 0.733013992
11. EDA EDA Aja: 0.69784045
12. Syntax Error: 0.640556563

OUR SUBMISSION 1 FORENSICS:
In Submission 1, our predictions had:
- online gambling: 980
- phishing: 397
- other: 47
- spam: 31
- malware: 27
- brand: 15
- fakeshop: 1 (Row 1347: https://www.******.co.id/professionals/online-shop-in-jakarta-yakarta-indonesia, registrar PT Jagat Informasi Solusi)
- violence: 1 (Row 12: https://***********.id/trapstar-borsello-95693/ - FP!)
- piiexposure: 1 (Row 578: http://www.*****.co.id/ - FP!)
Additionally, we had 33 noisy overrides from aggressive IP matching that flipped gambling to spam and phishing (e.g. 1xbetcash -> phishing, daftar-tempur777 -> spam).

We have 2 submission quotas left (Submission 2 and Submission 3).
Our goal is to reach RANK 1 (>0.835 up to 0.93).

QUESTIONS FOR YOU:
1. Deconstruct the mathematics: Why did Kusut Kusut Reborn get 0.834969292? What is the exact denominator K in `scoring_classes = sorted(set(y_true))`? Is K=8 or K=9?
2. What happened in our Submission 1 (0.744171684)? Why is Princess Theory at 0.7666?
3. How should we configure our Submission 2 and Submission 3 to maximize score (>0.835)? What are the concrete decision rules for:
   - Restoring major class precision (gambling, phishing, other, spam, malware)
   - Brand (how many samples, what indicators?)
   - Fakeshop (which candidates in predict.csv?)
   - Violence and PIIExposure (should we predict them, or are they 0 in test set?)
Be rigorous, mathematical, and actionable.
"""

def main():
    payload = {
        "model": "kr/claude-sonnet-4.5-thinking-agentic",
        "messages": [{"role": "user", "content": PROMPT}],
        "temperature": 0.2,
        "max_tokens": 4096
    }
    
    print("[*] Querying 9Router (kr/claude-sonnet-4.5-thinking-agentic)...")
    try:
        res = requests.post("http://localhost:20128/v1/chat/completions", json=payload, timeout=90)
        res.raise_for_status()
        data = res.json()
        content = data["choices"][0]["message"]["content"]
        
        with open("docs/EXPERT_CONSULTATION_SCOREBOARD_OPTIMIZATION.md", "w", encoding="utf-8") as f:
            f.write("# EXPERT CONSULTATION: SCOREBOARD REVERSE ENGINEERING & SUBMISSION 2/3 STRATEGY\n\n")
            f.write(content)
            
        print("[OK] Expert advice saved to docs/EXPERT_CONSULTATION_SCOREBOARD_OPTIMIZATION.md")
        print("\n--- SUMMARY OF EXPERT ADVICE ---")
        print(content[:1500])
    except Exception as e:
        print("[ERROR] Failed to query 9Router:", e)

if __name__ == "__main__":
    main()
