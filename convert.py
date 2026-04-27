import csv
import json
import random
import os

def build_qa_pairs(csv_path):
    rows = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    pairs = []
    for row in rows:
        name = row["Law Name"]
        ref = row["Section/Act Reference"]
        act = row["Full Act Name"]
        year = row["Year Enacted/Amended"]
        status = row["Current Status"]
        summary = row["Key Provisions Summary"]
        applies = row["Who It Applies To"]
        authority = row["Enforcement Authority"]

        # Template 1: Direct question
        pairs.append({"text": f"<start_of_turn>user\n{name} kya hai?<end_of_turn>\n<start_of_turn>model\n{name} ({ref}) {act} ke under aata hai jo {year} mein enacted hua. Status: {status}. Yeh {applies} par apply hota hai. Key provisions: {summary}. Authority: {authority}.<end_of_turn>"})

        # Template 2: Rights question
        pairs.append({"text": f"<start_of_turn>user\n{applies} ke kya adhikar hain {name} ke tahat?<end_of_turn>\n<start_of_turn>model\n{act} ke tahat {applies} ke adhikar: {summary}. Kisi bhi problem ke liye {authority} se sampark karein.<end_of_turn>"})

        # Template 3: English
        pairs.append({"text": f"<start_of_turn>user\nWhat is {name} under Indian law?<end_of_turn>\n<start_of_turn>model\n{name} falls under {act} ({ref}), enacted in {year}. Status: {status}. Applies to: {applies}. Key provisions: {summary}. Enforced by: {authority}.<end_of_turn>"})

        # Template 4: Legal advice
        pairs.append({"text": f"<start_of_turn>user\nMujhe {name} ke baare mein legal advice chahiye.<end_of_turn>\n<start_of_turn>model\n{name} ke baare mein zaroori jaankari: Yeh {applies} par laagu hota hai. {summary}. Koi bhi issue hone par {authority} se sampark karein. Reference: {ref} - {act}.<end_of_turn>"})

    return pairs

def save_splits(pairs, output_dir="data"):
    os.makedirs(output_dir, exist_ok=True)
    random.seed(42)
    random.shuffle(pairs)

    n = len(pairs)
    train_end = int(n * 0.85)
    val_end = int(n * 0.92)

    splits = {
        "train": pairs[:train_end],
        "validation": pairs[train_end:val_end],
        "test": pairs[val_end:]
    }

    for name, data in splits.items():
        path = f"{output_dir}/{name}.jsonl"
        with open(path, "w", encoding="utf-8") as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(f"{name}: {len(data)} examples → {path}")

    print(f"\nTotal pairs: {n}")

if __name__ == "__main__":
    pairs = build_qa_pairs("indian_laws_2026.csv")
    save_splits(pairs)