"""
PIPELINE TRADUCTION PIVOT - Jour 4
FR → EN → IT/RU (approche cascade)
Pour Marie (Windows)
Stratégie scientifique: analyse cascade errors
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

PIVOT_CONFIGS = {
    'it': {
        'fr_en': 'Helsinki-NLP/Opus-MT-fr-en',
        'en_x': 'Helsinki-NLP/Opus-MT-en-it',
        'final_lang': 'it'
    },
    'ru': {
        'fr_en': 'Helsinki-NLP/Opus-MT-fr-en',
        'en_x': 'Helsinki-NLP/Opus-MT-en-ru',
        'final_lang': 'ru'
    }
}

# ============================================================================
# TRADUCTION PIVOT
# ============================================================================

class PivotTranslator:
    """Traduction en cascade: FR → EN → lang"""
    
    def __init__(self):
        self.models = {}
    
    def translate_pivot(self, text_fr, target_lang):
        """
        Traduction pivot: FR → EN → target_lang
        Retourne intermédiaire + final pour analyser cascade errors
        """
        
        config = PIVOT_CONFIGS[target_lang]
        
        # ÉTAPE 1: FR → EN
        if 'fr_en' not in self.models:
            print(f"   Chargement FR→EN (pivot)...")
            tok = MarianTokenizer.from_pretrained(config['fr_en'])
            mdl = MarianMTModel.from_pretrained(config['fr_en']).to(DEVICE)
            self.models['fr_en'] = (tok, mdl)
        
        tok_fr_en, mdl_fr_en = self.models['fr_en']
        inp_en = tok_fr_en(text_fr, return_tensors="pt", truncation=True, max_length=512).to(DEVICE)
        
        with torch.no_grad():
            out_en = mdl_fr_en.generate(**inp_en, max_length=512, num_beams=4)
        
        text_en = tok_fr_en.decode(out_en[0], skip_special_tokens=True)
        
        # ÉTAPE 2: EN → target_lang
        model_key = f"en_{target_lang}"
        if model_key not in self.models:
            print(f"   Chargement EN→{target_lang.upper()}...")
            tok = MarianTokenizer.from_pretrained(config['en_x'])
            mdl = MarianMTModel.from_pretrained(config['en_x']).to(DEVICE)
            self.models[model_key] = (tok, mdl)
        
        tok_en_x, mdl_en_x = self.models[model_key]
        inp_x = tok_en_x(text_en, return_tensors="pt", truncation=True, max_length=512).to(DEVICE)
        
        with torch.no_grad():
            out_x = mdl_en_x.generate(**inp_x, max_length=512, num_beams=4)
        
        text_x = tok_en_x.decode(out_x[0], skip_special_tokens=True)
        
        # Retourner intermédiaire + final pour analyser cascade
        return {
            'intermediate_en': text_en,
            'final': text_x
        }

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("="*70)
    print("🌐 PIPELINE TRADUCTION PIVOT - JOUR 4")
    print("="*70)
    print()
    
    # Charger résultats ASR
    asr_results_file = OUTPUT_DIR / "asr_results.json"
    
    if not asr_results_file.exists():
        print(f"❌ ERREUR: {asr_results_file} non trouvé")
        return
    
    with open(asr_results_file, 'r', encoding='utf-8') as f:
        asr_results = json.load(f)
    
    print(f"✓ {len(asr_results)} résultats ASR chargés\n")
    
    # Initialiser traducteur pivot
    translator = PivotTranslator()
    
    # Traductions stockées
    all_translations = {}
    cascade_errors = {}
    
    # Traiter chaque vidéo
    for video_name, asr_data in asr_results.items():
        print(f"[{video_name}]")
        
        all_translations[video_name] = {}
        cascade_errors[video_name] = {}
        segments = asr_data['segments']
        
        # Traiter chaque segment
        for seg_idx, segment in enumerate(segments[:10]):
            text_fr = segment['text'].strip()
            
            if not text_fr or len(text_fr) < 3:
                continue
            
            all_translations[video_name][seg_idx] = {
                'fr': text_fr,
                'time': f"{segment['start']:.1f}-{segment['end']:.1f}s",
                'translations': {}
            }
            
            cascade_errors[video_name][seg_idx] = {
                'fr': text_fr,
                'en_intermediate': {},
                'final': {}
            }
            
            print(f"  Segment {seg_idx}: {text_fr[:40]}...")
            
            # Traduire vers IT et RU via EN
            for lang in ['it', 'ru']:
                try:
                    result = translator.translate_pivot(text_fr, lang)
                    
                    all_translations[video_name][seg_idx]['translations'][lang] = result['final']
                    
                    cascade_errors[video_name][seg_idx]['en_intermediate'][lang] = result['intermediate_en']
                    cascade_errors[video_name][seg_idx]['final'][lang] = result['final']
                    
                    print(f"    {lang.upper()}: ✓ (via EN)")
                except Exception as e:
                    print(f"    {lang.upper()}: ❌ {e}")
            
            print()
        
        print()
    
    # Générer fichiers SRT traduits PIVOT
    print("="*70)
    print("Génération fichiers SRT (traductions pivot)...")
    print("="*70)
    print()
    
    for video_name, video_translations in all_translations.items():
        for lang in ['it', 'ru']:
            subs = pysrt.SubRipFile()
            
            for seg_idx, seg_data in video_translations.items():
                if lang not in seg_data['translations']:
                    continue
                
                orig_seg = asr_results[video_name]['segments'][seg_idx]
                trans_text = seg_data['translations'][lang]
                
                sub = pysrt.SubRipItem()
                sub.index = seg_idx + 1
                sub.start = pysrt.SubRipTime(milliseconds=int(orig_seg['start'] * 1000))
                sub.end = pysrt.SubRipTime(milliseconds=int(orig_seg['end'] * 1000))
                sub.content = trans_text
                subs.append(sub)
            
            if len(subs) > 0:
                srt_path = SRT_DIR / f"{video_name}_{lang}_pivot.srt"
                subs.save(str(srt_path))
                print(f"✓ {srt_path.name}")
    
    # Sauvegarder résultats PIVOT
    results_file = OUTPUT_DIR / "translation_pivot_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(all_translations, f, indent=2, ensure_ascii=False)
    
    # Sauvegarder ANALYSE cascade errors (important pour rapport!)
    cascade_file = OUTPUT_DIR / "cascade_error_analysis.json"
    with open(cascade_file, 'w', encoding='utf-8') as f:
        json.dump(cascade_errors, f, indent=2, ensure_ascii=False)
    
    print()
    print("="*70)
    print("✅ TRADUCTIONS PIVOT COMPLÈTES!")
    print("="*70)
    print(f"\n📊 Cascade Error Analysis sauvegardée:")
    print(f"   {cascade_file}")
    print(f"\n✓ Prêt pour Jour 5 (Analyse)!")

if __name__ == "__main__":
    main()
