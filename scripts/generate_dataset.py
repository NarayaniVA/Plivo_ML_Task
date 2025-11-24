import json
import random
import os
import re
from src.data_utils import get_pools, noisify_pii, FILLERS, DIGIT_MAP, SYMBOL_MAP, inject_fillers_to_tokens, apply_contextual_noise

# Configuration
TRAIN_COUNT = 550
DEV_COUNT = 150
OUTPUT_DIR = "data"
TRAIN_FILE = "train2.jsonl"
DEV_FILE = "dev2.jsonl"


def create_example(uid, mode: str):
    entities, templates = get_pools(mode)
    template, entity_keys = random.choice(templates)

    entity_values = {key: random.choice(entities[key]) for key in entity_keys}

    base_text = template.format(**entity_values)

    clean_entities_with_spans = []
    for key, clean_value in entity_values.items():
        for match in re.finditer(re.escape(clean_value), base_text):
            clean_entities_with_spans.append({
                "start": match.start(),
                "end": match.end(),
                "clean_value": clean_value,
                "label": key
            })

    clean_entities_with_spans.sort(key=lambda x: x['start'])

    current_text = base_text
    context_noise_data = []

    for entity in clean_entities_with_spans:
        noisy_value = noisify_pii(entity["clean_value"], entity["label"])

        start_index_in_current = current_text.find(entity["clean_value"])
        if start_index_in_current != -1:
            context_noise_data.append({
                "start": start_index_in_current,
                "end": start_index_in_current + len(entity["clean_value"]),
                "noisy_value": noisy_value,
                "label": entity["label"]
            })
            current_text = current_text.replace(entity["clean_value"], noisy_value, 1)

    final_text, final_labeled_entities = apply_contextual_noise(current_text, context_noise_data)

    return {"id": f"utt_{uid:04d}", "text": final_text, "entities": final_labeled_entities}


def generate_dataset(count: int, filename: str, mode: str):
    print(f"Generating {count} examples for {filename} ({mode} set)...")

    data = []
    random.seed(42 if mode == "TRAIN" else 100)

    uid_offset = 0 if mode == "TRAIN" else 1000

    i = 0
    while len(data) < count:
        uid = i + 1 + uid_offset
        example = create_example(uid, mode)
        if example["entities"] and example["text"]:
            data.append(example)
        i += 1
        if i > count * 3:
            print(f"Warning: Failed to generate all {count} examples after {i} attempts. Stopping.")
            break

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file_path = os.path.join(OUTPUT_DIR, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item) + "\n")

    print(f"Successfully wrote {len(data)} examples to {file_path}")
    print("-" * 30)


if __name__ == "__main__":
    generate_dataset(TRAIN_COUNT, TRAIN_FILE, "TRAIN")
    generate_dataset(DEV_COUNT, DEV_FILE, "DEV")
