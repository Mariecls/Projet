"""
PIPELINE ASR COMPLET - Jour 2
Vidéo → Audio → Texte français → SRT
Pour Marie (Windows)
Fichiers audio: .flac, .wav, .mp4

VERSION: Test avec 10 vidéos
CORRECTION: pysrt.SubRip → pysrt.SubRipItem
"""

import whisper
import pysrt
from pathlib import Path
from tqdm import tqdm
import json

# ============================================================================
# CONFIG
# ============================================================================

VIDEOS_DIR = Path("mtedx_fr/videos")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

SRT_DIR = OUTPUT_DIR / "srt"
SRT_DIR.mkdir(exist_ok=True)

WHISPER_MODEL = "base"
LANGUAGE = "fr"

# ============================================================================
# ASR PROCESSOR
# ============================================================================

class ASRProcessor:
    """Extraction texte depuis vidéo avec Whisper"""
    
    def __init__(self, model_size="base"):
        print(f"[ASR] Chargement Whisper-{model_size}...")
        self.model = whisper.load_model(model_size)
        print(f"✓ Whisper chargé!\n")
    
    def transcribe(self, audio_path):
        """Transcrire audio avec Whisper"""
        result = self.model.transcribe(str(audio_path), language=LANGUAGE)
        return result
    
    def save_srt(self, segments, output_path):
        """Générer fichier SRT"""
        subs = pysrt.SubRipFile()
        
        for i, seg in enumerate(segments):
            sub = pysrt.SubRipItem()  # ✅ CORRECTION: SubRipItem au lieu de SubRip
            sub.index = i + 1
            sub.start = pysrt.SubRipTime(milliseconds=int(seg['start'] * 1000))
            sub.end = pysrt.SubRipTime(milliseconds=int(seg['end'] * 1000))
            sub.content = seg['text'].strip()
            subs.append(sub)
        
        subs.save(str(output_path))
        return output_path

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("="*70)
    print("🎙️  PIPELINE ASR - TEST")
    print("="*70)
    print()
    
    if not VIDEOS_DIR.exists():
        print(f"❌ ERREUR: Dossier non trouvé: {VIDEOS_DIR}")
        return
    
    videos = list(VIDEOS_DIR.glob("*.flac")) + list(VIDEOS_DIR.glob("*.wav")) + list(VIDEOS_DIR.glob("*.mp4"))
    
    if not videos:
        print(f"❌ ERREUR: Aucune vidéo trouvée!")
        return
    
    print(f"✓ {len(videos)} vidéo(s) trouvée(s)")
    
    # Limiter à 10 vidéos
    videos = sorted(videos)[:10]
    print(f"✓ Test avec {len(videos)} vidéo(s)\n")
    
    asr = ASRProcessor(model_size=WHISPER_MODEL)
    
    asr_results = {}
    
    for idx, video_path in enumerate(videos, 1):
        video_name = video_path.stem
        print(f"\n[{idx}/{len(videos)}] {video_name}")
        
        try:
            print(f"  Transcription...")
            result = asr.transcribe(video_path)
            
            srt_path = SRT_DIR / f"{video_name}_fr.srt"
            asr.save_srt(result['segments'], srt_path)
            
            asr_results[video_name] = {
                'segments': result['segments'],
                'full_text': result['text'],
                'srt_path': str(srt_path),
                'num_segments': len(result['segments'])
            }
            
            print(f"  ✅ {len(result['segments'])} segments")
            
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
            continue
    
    results_file = OUTPUT_DIR / "asr_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(asr_results, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*70)
    print("✅ PIPELINE ASR TERMINÉ!")
    print("="*70)
    print(f"\n📊 Résultats:")
    print(f"  • Vidéos traitées: {len(asr_results)}")
    total_segments = sum(v['num_segments'] for v in asr_results.values())
    print(f"  • Segments totaux: {total_segments}")
    print(f"  • SRT générés: {len(list(SRT_DIR.glob('*_fr.srt')))}")
    print(f"\n📁 Fichiers dans: {SRT_DIR}")
    print(f"\n✓ Prêt pour Jour 3 (Traduction)!")

if __name__ == "__main__":
    main()
