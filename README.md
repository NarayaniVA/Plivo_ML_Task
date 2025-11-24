# PII Entity Recognition for Noisy STT Transcripts

## Project Overview
This repository contains the implementation of a token-level Named Entity Recognition (NER) model to detect Personally Identifiable Information (PII) entities from noisy Speech-to-Text (STT) transcripts. The model identifies sensitive entities (credit card numbers, phone numbers, emails, person names, dates) and location-related ones, prioritizing high PII precision for safe data handling.

This is the submission codebase for the IIT Madras PII NER challenge 2025.

## Pretrained Model Download
The trained model checkpoint files are too large to upload to this repository. Please download the model folder from the following Google Drive link:
https://drive.google.com/drive/folders/1oR-u7hROSrn8K2oKrAwsML6V_2998j8Q?usp=drive_link

## Dataset and Noise
- Training and dev datasets use realistic noise to simulate real STT transcripts.

- Noise includes fillers like "uh", "um", and word replacements for digits and symbols in PII entities.

- Entities have phonetic misspellings, spelled-out dates, and symbol verbalizations.

- Noise is applied both within entities and in surrounding context.

- Entity spans are carefully recalculated to keep annotations accurate despite noise.

- Sentence templates mix multiple entity types naturally with noise, making the dataset challenging and realistic.

Dataset files:
- `data/train2.jsonl`: Training dataset (550 examples)
- `data/dev2.jsonl`: Development dataset (150 examples)

Entities are annotated as character spans with labels and PII flags, in noisy, lowercased, filler-rich STT-like transcription.

## Model
- DistilBERT transformer fine-tuned for token classification.
- BIO tagging scheme for token-level entity annotation.
- Custom code for entity span extraction, PII flagging, and noisy data handling.
- All supporting scripts (`src/dataset.py`, `src/labels.py`, `src/model.py`) included.

## Hyperparameters
The key Hyperparameters used are -
- Epochs: 3
- Batch size: 8
- Learning rate: 5e-5

## Code Structure
- `src/train.py`: Train the token classifier on noisy PII data.
- `src/predict.py`: Run inference to get predicted entities from transcripts.
- `src/eval_span_f1.py`: Evaluate per-entity and macro F1 scores.
- `src/measure_latency.py`: Script to measure p50/p95 inference latency of the model.
- `src/data_utils.py`: Helper functions and templates for synthetic dataset generation with noise injection.
- `scripts/generate_dataset.py`: Main script to generate noisy training and dev datasets using data_utils.py.

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

**Latency over 50 runs (batch_size=1):**

- p50 latency: 46.59 ms
- p95 latency: 107.65 ms

The relatively high latency compared to the target reflects the use of a transformer-based model on CPU without optimization. There is opportunity to optimize inference speed to meet stricter latency budgets.

## Dataset Generation

The training and development datasets are synthetically generated using the scripts in `scripts/generate_dataset.py` combined with helper functions in `src/data_utils.py`.

- The generator uses realistic templates with noisy PII and context fillers to simulate real STT transcripts.
- Data generation uses realistic templates, injections of conversational fillers, lowercasing, and robust entity tracking post-noise addition.
- Contextual noise and fillers are applied holistically to both train and dev datasets, ensuring robustness.
- Entity spans are recalculated post-noise to maintain annotation accuracy.
- Run the following command to generate the datasets locally:

python scripts/generate_dataset.py

- This script creates the noisy datasets (`data/train2.jsonl` and `data/dev2.jsonl`) with annotated entities.


## Limitations and Future Work

- Hyperparameter tuning and larger-scale experimentation were limited due to time constraints.
- The training dataset size was moderate (550 training, 150 dev examples), constrained by assignment deadlines.
- The highly noisy and realistic nature of the datasets introduced significant challenges for entity detection.
- There remains considerable scope for improving performance through expanded datasets, data augmentation, advanced modeling techniques, and careful hyperparameter optimization.


*All instructions and dataset/code files needed to reproduce, train, evaluate, and measure your model as per assignment are included. Please see scripts and documentation for details.*

