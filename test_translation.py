import torch
from transformers import MarianMTModel, MarianTokenizer

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"[TEST] Device: {DEVICE}\n")

print("[TEST] Loading MarianMT FR→EN...")
model_name = 'Helsinki-NLP/Opus-MT-fr-en'
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name).to(DEVICE)
print("✓ MarianMT loaded!\n")

# Test translation
text_fr = "Bonjour, comment allez-vous?"
inputs = tokenizer(text_fr, return_tensors="pt").to(DEVICE)

with torch.no_grad():
    output = model.generate(**inputs, num_beams=4)

text_en = tokenizer.decode(output[0], skip_special_tokens=True)

print(f"FR: {text_fr}")
print(f"EN: {text_en}")
print("\n✓ Translation works!")
