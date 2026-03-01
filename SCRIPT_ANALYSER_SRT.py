"""
SCRIPT: Analyser les SRT et générer résultats de traduction
À exécuter sur Windows pour extraire les résultats
"""

import json
from pathlib import Path
from collections import defaultdict

print("\n" + "="*120)
print("📊 ANALYSE DES RÉSULTATS DE TRADUCTION (SRT)")
print("="*120)

# Ton chemin
SRT_DIR = Path(r"C:\Users\marie\Documents\Deeplearning\Projet\outputs\srt")
OUTPUT_DIR = Path(r"C:\Users\marie\Documents\Deeplearning\Projet\outputs")

print(f"\n📁 Dossier SRT: {SRT_DIR}\n")

if not SRT_DIR.exists():
    print(f"❌ ERREUR: Dossier non trouvé!")
    print(f"Vérifie le chemin: {SRT_DIR}")
    exit(1)

# Lister tous les fichiers SRT
srt_files = sorted(list(SRT_DIR.glob('*.srt')))

print(f"✅ Trouvé {len(srt_files)} fichiers SRT\n")

# Grouper par vidéo et langue
videos_data = defaultdict(lambda: {})

for srt_file in srt_files:
    filename = srt_file.name
    
    # Parser: video_LANG.srt
    parts = filename.replace('.srt', '').split('_')
    
    if len(parts) >= 2:
        lang = parts[-1]
        video = '_'.join(parts[:-1])
        
        # Lire le fichier SRT
        with open(srt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        videos_data[video][lang] = {
            'file': str(srt_file),
            'num_lines': len(content.split('\n')),
            'content_preview': content[:200]  # Premier 200 chars
        }

print(f"📋 VIDÉOS AVEC TRADUCTIONS: {len(videos_data)}\n")

for i, (video, langs) in enumerate(sorted(videos_data.items()), 1):
    print(f"   {i:2d}. {video:40s} → {list(langs.keys())}")

# Créer un fichier JSON avec les résultats
translation_results = {
    'total_videos': len(videos_data),
    'videos': {}
}

for video, langs_data in videos_data.items():
    translation_results['videos'][video] = {
        'languages': list(langs_data.keys()),
        'files': {lang: data['file'] for lang, data in langs_data.items()}
    }

# Sauvegarder
results_file = OUTPUT_DIR / "translation_results_summary.json"
with open(results_file, 'w', encoding='utf-8') as f:
    json.dump(translation_results, f, indent=2, ensure_ascii=False)

print(f"\n✅ RÉSULTATS SAUVEGARDÉS: {results_file}")

print(f"\n" + "="*120)
print(f"✅ PROCHAINE ÉTAPE:")
print(f"="*120)
print(f"""
Fichier créé: translation_results_summary.json

Ce fichier contient:
   • {len(videos_data)} vidéos avec traductions
   • Les langues disponibles pour chaque vidéo
   • Les chemins des fichiers SRT

🎯 Envoie-moi ce fichier et je vais:
   1. Analyser les traductions
   2. Calculer la qualité
   3. Extraire des exemples
   4. Ajouter tout au notebook!
""")

print("="*120 + "\n")