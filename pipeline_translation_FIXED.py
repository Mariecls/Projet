"""
PIPELINE TRADUCTION - Jour 3
Texte français → 2 langues (EN, ES)
Approche directe (non-pivot)
Pour Marie (Windows)

NOTE: PT sera fait en PIVOT (Jour 4)
"""

import torch
from transformers import MarianMTModel, MarianTokenizer
import pysrt
import json
from pathlib import Path

# ============================================================================
# CONFIG
# ============================================================================

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"🖥️  Device: {DEVICE}\n")

OUTPUT_DIR = Path("outputs")
SRT_DIR = OUTPUT_DIR / "srt"

TARGET_LANGS = ['en', 'es']  # ✅ SANS PT (sera fait en PIVOT)

TRANSLATION_PAIRS = {
    'en': 'Helsinki-NLP/Opus-MT-fr-en',
    'es': 'Helsinki-NLP/Opus-MT-fr-es',
}

# ============================================================================
# TRADUCTION
# ============================================================================

class DirectTranslator:
    """Traduction directe FR → langue"""
    
    def __init__(self):
        self.models = {}
    
    def translate(self, text, lang):
        """Traduire FR → lang"""
        
        if lang not in self.models:
            print(f"   Chargement modèle FR→{lang.upper()}...")
            tok = MarianTokenizer.from_pretrained(TRANSLATION_PAIRS[lang])
            mdl = MarianMTModel.from_pretrained(TRANSLATION_PAIRS[lang]).to(DEVICE)
            self.models[lang] = (tok, mdl)
        
        tok, mdl = self.models[lang]
        
        inp = tok(text, return_tensors="pt", truncation=True, max_length=512).to(DEVICE)
        
        with torch.no_grad():
            out = mdl.generate(**inp, max_length=512, num_beams=4, early_stopping=True)
        
        translation = tok.decode(out[0], skip_special_tokens=True)
        return translation

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("="*70)
    print("🌐 PIPELINE TRADUCTION DIRECTE - JOUR 3")
    print("="*70)
    print()
    
    # Charger résultats ASR
    asr_results_file = OUTPUT_DIR / "asr_results.json"
    
    if not asr_results_file.exists():
        print(f"❌ ERREUR: {asr_results_file} non trouvé")
        print("   Assurez-vous d'avoir exécuté pipeline_asr.py d'abord!")
        return
    
    with open(asr_results_file, 'r', encoding='utf-8') as f:
        asr_results = json.load(f)
    
    print(f"✓ {len(asr_results)} résultats ASR chargés")
    print(f"✓ Traduction vers: {', '.join(TARGET_LANGS).upper()}\n")
    
    # Initialiser traducteur
    translator = DirectTranslator()
    
    # Traductions stockées
    all_translations = {}
    
    # Traiter chaque vidéo
    for video_name, asr_data in asr_results.items():
        print(f"\n[{video_name}]")
        
        all_translations[video_name] = {}
        segments = asr_data['segments']
        
        # Traiter chaque segment (limiter à 10 pour démo)
        for seg_idx, segment in enumerate(segments[:10]):
            text_fr = segment['text'].strip()
            
            if not text_fr or len(text_fr) < 3:
                continue
            
            all_translations[video_name][seg_idx] = {
                'fr': text_fr,
                'time': f"{segment['start']:.1f}-{segment['end']:.1f}s",
                'translations': {}
            }
            
            print(f"  Segment {seg_idx}: {text_fr[:50]}...")
            
            # Traduire vers chaque langue
            for lang in TARGET_LANGS:
                try:
                    trans = translator.translate(text_fr, lang)
                    all_translations[video_name][seg_idx]['translations'][lang] = trans
                    print(f"    {lang.upper()}: ✓")
                except Exception as e:
                    print(f"    {lang.upper()}: ❌ {e}")
    
    # Générer fichiers SRT traduits
    print("\n" + "="*70)
    print("Génération fichiers SRT traduits...")
    print("="*70)
    print()
    
    srt_count = 0
    for video_name, video_translations in all_translations.items():
        for lang in TARGET_LANGS:
            subs = pysrt.SubRipFile()
            
            for seg_idx, seg_data in video_translations.items():
                if lang not in seg_data['translations']:
                    continue
                
                orig_seg = asr_results[video_name]['segments'][seg_idx]
                trans_text = seg_data['translations'][lang]
                
                sub = pysrt.SubRipItem()  # ✅ Correction pysrt
                sub.index = seg_idx + 1
                sub.start = pysrt.SubRipTime(milliseconds=int(orig_seg['start'] * 1000))
                sub.end = pysrt.SubRipTime(milliseconds=int(orig_seg['end'] * 1000))
                sub.content = trans_text
                subs.append(sub)
            
            if len(subs) > 0:
                srt_path = SRT_DIR / f"{video_name}_{lang}_direct.srt"
                subs.save(str(srt_path))
                print(f"✓ {srt_path.name}")
                srt_count += 1
    
    # Sauvegarder résultats détaillés
    results_file = OUTPUT_DIR / "translation_direct_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(all_translations, f, indent=2, ensure_ascii=False)
    
    print()
    print("="*70)
    print("✅ TRADUCTIONS DIRECTES COMPLÈTES!")
    print("="*70)
    print(f"\n📊 Résultats:")
    print(f"  • Langues directes: {', '.join(TARGET_LANGS).upper()}")
    print(f"  • Fichiers SRT générés: {srt_count}")
    print(f"\n✓ Prêt pour Jour 4 (Traductions Pivot - PT via EN)!")

if __name__ == "__main__":
    main()
