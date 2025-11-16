#!/usr/bin/env python3
"""
Dia TTS CPU-only voice test
---------------------------
Generates a short sample with the official non-verbal tags only.
Expected output: 'female_dia_cpu_test.mp3'
"""

import torch
from transformers import AutoProcessor, DiaForConditionalGeneration
import soundfile as sf

# ----------------------------
# CONFIG
# ----------------------------
device = "cpu"
print("Running on:", device)

model_id = "nari-labs/Dia-1.6B-0626"

# Load processor + model on CPU
print("Loading model...")
processor = AutoProcessor.from_pretrained(model_id)
model = DiaForConditionalGeneration.from_pretrained(model_id).to(device)

# ----------------------------
# TEXT PROMPT (official tags only)
# ----------------------------
text = [
    "[S1] (smiles) Hi, welcome to NRTIV AI. (inhales) The most revolutionary online risk forecaster on the market. (pauses) What country do you want to analyse today?"
]

# ----------------------------
# GENERATE
# ----------------------------
print("Generating audio...")
inputs = processor(text=text, return_tensors="pt").to(device)

with torch.inference_mode():
    outputs = model.generate(
        **inputs,
        do_sample=True,
        max_new_tokens=2048,
        temperature=0.8,   # low for clarity
        top_p=0.9,
        guidance_scale=2.5
    )

# ----------------------------
# SAVE OUTPUT
# ----------------------------
decoded = processor.batch_decode(outputs)
output_path = "female_dia_cpu_test.mp3"
processor.save_audio(decoded, output_path)

print(f"✅ Audio saved to {output_path}")
