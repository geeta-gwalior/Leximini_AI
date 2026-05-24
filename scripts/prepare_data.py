"""
LexiMini AI - Legal Data Preparation Script
CSV → JSONL with Data Augmentation
Generates: base QA pairs + augmented reasoning pairs
Target: 2000+ training samples from 400 CSV rows
"""

import pandas as pd
import json
import random
import re
from pathlib import Path

# ─── Config ───────────────────────────────────────────────────────────────────
INPUT_CSV   = "data/indian_laws_2026.csv"
OUTPUT_DIR  = Path("leximini_data")
TRAIN_FILE  = OUTPUT_DIR / "train.jsonl"
EVAL_FILE   = OUTPUT_DIR / "eval.jsonl"
EVAL_RATIO  = 0.1   # 10% for eval
RANDOM_SEED = 42

random.seed(RANDOM_SEED)
OUTPUT_DIR.mkdir(exist_ok=True)

# ─── Load CSV ─────────────────────────────────────────────────────────────────
df = pd.read_csv(INPUT_CSV).fillna("")
print(f"✅ Loaded {len(df)} rows from {INPUT_CSV}")

# ─── Question Templates (Hindi + English mixed) ───────────────────────────────

# Template sets: each takes (law_name, section, summary, authority, applies_to)
QA_TEMPLATES = [

    # English templates
    lambda r: {
        "instruction": f"What is {r['Law Name']} under {r['Section/Act Reference']}?",
        "input": "",
        "output": (
            f"{r['Law Name']} ({r['Section/Act Reference']}) is part of {r['Full Act Name']} "
            f"enacted in {r['Year Enacted/Amended']}.\n\n"
            f"Key Provisions: {r['Key Provisions Summary']}\n\n"
            f"Applies to: {r['Who It Applies To']}\n"
            f"Enforcement: {r['Enforcement Authority']}"
        )
    },
    lambda r: {
        "instruction": f"Explain the legal provisions of {r['Law Name']} in simple terms.",
        "input": "",
        "output": (
            f"Under {r['Full Act Name']} ({r['Section/Act Reference']}), {r['Key Provisions Summary']}. "
            f"This law applies to {r['Who It Applies To']} and is enforced by {r['Enforcement Authority']}. "
            f"Current status: {r['Current Status']}."
        )
    },
    lambda r: {
        "instruction": f"Who enforces {r['Law Name']} in India?",
        "input": "",
        "output": (
            f"{r['Law Name']} under {r['Section/Act Reference']} is enforced by {r['Enforcement Authority']}. "
            f"This applies to {r['Who It Applies To']}. "
            f"The law falls under {r['Full Act Name']} and its current status is: {r['Current Status']}."
        )
    },
    lambda r: {
        "instruction": f"What are my rights under {r['Section/Act Reference']}?",
        "input": "",
        "output": (
            f"Under {r['Section/Act Reference']} of {r['Full Act Name']}: {r['Key Provisions Summary']}. "
            f"This provision applies to {r['Who It Applies To']}. "
            f"If you need to enforce these rights, approach {r['Enforcement Authority']}."
        )
    },

    # Hindi templates
    lambda r: {
        "instruction": f"{r['Law Name']} kya hai? Samjhaiye.",
        "input": "",
        "output": (
            f"{r['Law Name']} ({r['Section/Act Reference']}) {r['Full Act Name']} ka hissa hai, "
            f"jo {r['Year Enacted/Amended']} mein lagu hua.\n\n"
            f"Mukhya pravadhaan: {r['Key Provisions Summary']}\n\n"
            f"Yeh kaanoon {r['Who It Applies To']} par laagu hota hai. "
            f"Enforcement authority: {r['Enforcement Authority']}."
        )
    },
    lambda r: {
        "instruction": f"{r['Section/Act Reference']} ke tahat kya adhikar milte hain?",
        "input": "",
        "output": (
            f"{r['Full Act Name']} ke {r['Section/Act Reference']} ke antargat: {r['Key Provisions Summary']}. "
            f"Yeh {r['Who It Applies To']} ke liye laagu hai. "
            f"Apne adhikar ke liye {r['Enforcement Authority']} se sampark karein."
        )
    },
    lambda r: {
        "instruction": f"Agar {r['Who It Applies To']} ko {r['Law Name']} se sambandhit samasya ho toh kya karein?",
        "input": "",
        "output": (
            f"{r['Law Name']} ({r['Section/Act Reference']}) ke antargat aapke paas yeh adhikar hain: "
            f"{r['Key Provisions Summary']}. "
            f"Is mamle mein {r['Enforcement Authority']} se sampark karein. "
            f"Yeh kaanoon {r['Full Act Name']} ka hissa hai jo {r['Current Status']} hai."
        )
    },

    # Reasoning / Chain-of-thought templates
    lambda r: {
        "instruction": (
            f"A person is facing an issue related to {r['Category']}. "
            f"They want to know about {r['Law Name']}. Provide step-by-step legal guidance."
        ),
        "input": "",
        "output": (
            f"Step 1 - Identify the applicable law:\n"
            f"{r['Law Name']} under {r['Section/Act Reference']} of {r['Full Act Name']} applies here.\n\n"
            f"Step 2 - Understand your rights:\n"
            f"{r['Key Provisions Summary']}\n\n"
            f"Step 3 - Know who this applies to:\n"
            f"This provision covers {r['Who It Applies To']}.\n\n"
            f"Step 4 - Take action:\n"
            f"Approach {r['Enforcement Authority']} to enforce your rights. "
            f"The law's current status is {r['Current Status']}."
        )
    },
    lambda r: {
        "instruction": (
            f"{r['Category']} se related ek vyakti {r['Law Name']} ke baare mein jaanna chahta hai. "
            f"Kadam-dar-kadam margdarshan dijiye."
        ),
        "input": "",
        "output": (
            f"Kadam 1 - Laagu kaanoon pehchaanein:\n"
            f"{r['Law Name']} ({r['Section/Act Reference']}, {r['Full Act Name']}) yahan laagu hota hai.\n\n"
            f"Kadam 2 - Apne adhikar samjhein:\n"
            f"{r['Key Provisions Summary']}\n\n"
            f"Kadam 3 - Yah kaanoon kiske liye hai:\n"
            f"Yeh {r['Who It Applies To']} par laagu hota hai.\n\n"
            f"Kadam 4 - Karyavaahi karein:\n"
            f"{r['Enforcement Authority']} se sampark karein. "
            f"Is kaanoon ki sthiti: {r['Current Status']}."
        )
    },
]

# ─── Cross-category comparison template ───────────────────────────────────────
def make_comparison_pair(r1, r2):
    """Generate a comparison QA pair from two laws in same category."""
    return {
        "instruction": (
            f"What is the difference between {r1['Law Name']} and {r2['Law Name']} "
            f"under {r1['Category']}?"
        ),
        "input": "",
        "output": (
            f"{r1['Law Name']} ({r1['Section/Act Reference']}):\n"
            f"{r1['Key Provisions Summary']}\n"
            f"Applies to: {r1['Who It Applies To']} | Authority: {r1['Enforcement Authority']}\n\n"
            f"{r2['Law Name']} ({r2['Section/Act Reference']}):\n"
            f"{r2['Key Provisions Summary']}\n"
            f"Applies to: {r2['Who It Applies To']} | Authority: {r2['Enforcement Authority']}"
        )
    }

# ─── Generate base pairs ───────────────────────────────────────────────────────
all_pairs = []

for _, row in df.iterrows():
    r = row.to_dict()
    if not r['Key Provisions Summary']:
        continue
    for template in QA_TEMPLATES:
        try:
            pair = template(r)
            # Wrap in Gemma chat format
            all_pairs.append({
                "text": (
                    f"<start_of_turn>user\n{pair['instruction']}"
                    + (f"\n{pair['input']}" if pair['input'] else "")
                    + f"<end_of_turn>\n"
                    f"<start_of_turn>model\n{pair['output']}<end_of_turn>"
                )
            })
        except Exception as e:
            pass

print(f"✅ Base pairs generated: {len(all_pairs)}")

# ─── Generate comparison pairs ────────────────────────────────────────────────
comparison_count = 0
for category, group in df.groupby("Category"):
    rows = group.to_dict("records")
    if len(rows) >= 2:
        pairs_to_make = min(len(rows) - 1, 5)  # max 5 comparisons per category
        for i in range(pairs_to_make):
            r1, r2 = rows[i], rows[i + 1]
            if r1['Key Provisions Summary'] and r2['Key Provisions Summary']:
                pair = make_comparison_pair(r1, r2)
                all_pairs.append({
                    "text": (
                        f"<start_of_turn>user\n{pair['instruction']}<end_of_turn>\n"
                        f"<start_of_turn>model\n{pair['output']}<end_of_turn>"
                    )
                })
                comparison_count += 1

print(f"✅ Comparison pairs generated: {comparison_count}")
print(f"✅ Total pairs: {len(all_pairs)}")

# ─── Shuffle and split ────────────────────────────────────────────────────────
random.shuffle(all_pairs)
split_idx  = int(len(all_pairs) * (1 - EVAL_RATIO))
train_data = all_pairs[:split_idx]
eval_data  = all_pairs[split_idx:]

# ─── Write JSONL files ────────────────────────────────────────────────────────
def write_jsonl(data, path):
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

write_jsonl(train_data, TRAIN_FILE)
write_jsonl(eval_data,  EVAL_FILE)

print(f"\n📁 Output saved to: {OUTPUT_DIR}/")
print(f"   train.jsonl → {len(train_data)} samples")
print(f"   eval.jsonl  → {len(eval_data)} samples")
print(f"\n📋 Sample entry:")
print(json.dumps(train_data[0], ensure_ascii=False, indent=2)[:600])