# PII Entity Recognition for Noisy STT Transcripts

## Project Overview
This repository contains the implementation of a token-level Named Entity Recognition (NER) model to detect Personally Identifiable Information (PII) entities from noisy Speech-to-Text (STT) transcripts. The model identifies sensitive entities (credit card numbers, phone numbers, emails, person names, dates) and location-related ones, prioritizing high PII precision for safe data handling.

This is the submission codebase for the IIT Madras PII NER challenge 2025.


## Dataset and Noise
- Training and dev datasets use realistic noise to simulate real STT transcripts.

- Noise includes fillers like "uh", "um", and word replacements for digits and symbols in PII entities.

- Entities have phonetic misspellings, spelled-out dates, and symbol verbalizations.

- Noise is applied both within entities and in surrounding context.

- Entity spans are carefully recalculated to keep annotations accurate despite noise.

- Sentence templates mix multiple entity types naturally with noise, making the dataset challenging and realistic.

Dataset files:
- `data/train2.jsonl`: Training dataset (550 examples)
- `data/dev2.jsonl`: Development/Validation dataset (150 examples)
- `data/test.jsonl`: Test dataset for final evaluation

Entities are annotated as character spans with labels and PII flags, in noisy, lowercased, filler-rich STT-like transcription.

## Model
- DistilBERT transformer fine-tuned for token classification.
- BIO tagging scheme for token-level entity annotation.
- Custom code for entity span extraction, PII flagging, and noisy data handling.
- All supporting scripts (`src/dataset.py`, `src/labels.py`, `src/model.py`) included.

## Code Structure
- `src/train.py`: Train the token classifier on noisy PII data.
- `src/predict.py`: Run inference to get predicted entities from transcripts.
- `src/eval_span_f1.py`: Evaluate per-entity and macro F1 scores.
- `src/measure_latency.py`: Script to measure p50/p95 inference latency of the model.
- Dataset generation scripts and utilities included.

## Usage

### Installation
pip install -r requirements.txt


### Training
python src/train.py --model_name distilbert-base-uncased --train data/train2.jsonl --dev data/dev2.jsonl --out_dir out2 --epochs 3 --batch_size 8 --lr 5e-5

### Prediction
python src/predict.py --model_dir out2 --input data/test.jsonl --output out2/testpred.json


### Evaluation
python src/eval_span_f1.py --gold data/dev2.jsonl --pred out2/devpred1.json


### Latency Measurement
python src/measure_latency.py --model_dir out2 --input data/dev2.jsonl --runs 50


## Results

**Per-entity metrics on dev2.jsonl:**

| Entity       | Precision | Recall | F1     |
|--------------|-----------|--------|--------|
| DATE         |    0.746  | 0.847  | 0.794  |
| PERSON_NAME  |    0.655  | 0.594  | 0.623  |
| CITY         |    0.280  | 0.636  | 0.389  |
| EMAIL        |    0.391  | 0.391  | 0.391  |
| PHONE        |    0.373  | 0.413  | 0.392  |
| CREDIT_CARD  |    0.194  | 0.333  | 0.246  |
| LOCATION     |    0.027  | 0.023  | 0.025  |

---

- **Macro-F1:** 0.408

**PII-only metrics:**
- Precision: 0.510
- Recall: 0.584
- F1: 0.544

**Non-PII metrics:**
- Precision: 0.212
- Recall: 0.330
- F1: 0.258

The somewhat moderate scores reflect the challenge and realism of highly noisy STT-style transcription and entity disturbance in both context and value segments.

## Data Generation Details

- Data generation uses realistic templates, injections of conversational fillers, lowercasing, and robust entity tracking post-noise addition.
- Contextual noise and fillers are applied holistically to both train and dev datasets, ensuring robustness.
- Entity spans are recalculated post-noise to maintain annotation accuracy.
- Full code for dataset construction and noise application is provided.

## Limitations and Future Work

- Hyperparameter tuning and larger-scale experimentation were limited due to time constraints.
- The training dataset size was moderate (550 training, 150 dev examples), constrained by assignment deadlines.
- The highly noisy and realistic nature of the datasets introduced significant challenges for entity detection.
- There remains considerable scope for improving performance through expanded datasets, data augmentation, advanced modeling techniques, and careful hyperparameter optimization.


*All instructions and dataset/code files needed to reproduce, train, evaluate, and measure your model as per assignment are included. Please see scripts and documentation for details.*

