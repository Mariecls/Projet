"""
ANALYSE QUALITATIVE - Jour 5
Comparer traductions directes vs pivot
Identifier types d'erreurs
Pour rapport final
"""

import json
from pathlib import Path
import pandas as pd

# ============================================================================
# CONFIG
# ============================================================================

OUTPUT_DIR = Path("outputs")

# ============================================================================
# CHARGER RÉSULTATS
# ============================================================================

print("="*70)
print("📊 ANALYSE QUALITATIVE - TRADUCTIONS")
print("="*70)
print()

# Charger tous les résultats
with open(OUTPUT_DIR / "translation_direct_results.json", 'r', encoding='utf-8') as f:
    direct_trans = json.load(f)

with open(OUTPUT_DIR / "translation_pivot_results.json", 'r', encoding='utf-8') as f:
    pivot_trans = json.load(f)

with open(OUTPUT_DIR / "cascade_error_analysis.json", 'r', encoding='utf-8') as f:
    cascade_data = json.load(f)

print(f"✓ {len(direct_trans)} vidéos chargées")
print(f"✓ Traductions directes: EN, ES")
print(f"✓ Traductions pivot: IT, RU (via EN)\n")

# ============================================================================
# EXEMPLE 1: COMPARER SEGMENT PAR SEGMENT
# ============================================================================

print("="*70)
print("1. EXEMPLES DE TRADUCTIONS (10 segments)")
print("="*70)
print()

# Prendre première vidéo
first_video = list(direct_trans.keys())[0]
direct_segs = direct_trans[first_video]
pivot_segs = pivot_trans[first_video]
cascade_segs = cascade_data[first_video]

comparison_data = []

for seg_idx in list(direct_segs.keys())[:10]:
    seg_fr = direct_segs[seg_idx]['fr']
    
    row = {
        'Segment': seg_idx,
        'Français': seg_fr[:60] + '...' if len(seg_fr) > 60 else seg_fr,
        'EN (Direct)': direct_segs[seg_idx]['translations'].get('en', 'N/A')[:50],
        'ES (Direct)': direct_segs[seg_idx]['translations'].get('es', 'N/A')[:50],
        'IT (Pivot)': pivot_segs[seg_idx]['translations'].get('it', 'N/A')[:50],
        'RU (Pivot)': pivot_segs[seg_idx]['translations'].get('ru', 'N/A')[:50],
    }
    comparison_data.append(row)

# Afficher tableau
df_comparison = pd.DataFrame(comparison_data)
print(df_comparison.to_string(index=False))

# ============================================================================
# EXEMPLE 2: ANALYSE CASCADE ERRORS (INTERMÉDIAIRES)
# ============================================================================

print("\n" + "="*70)
print("2. ANALYSE CASCADE ERRORS - INTERMÉDIAIRES EN")
print("="*70)
print()

print("Exemple: Comment les erreurs propagent FR → EN → IT/RU")
print()

seg_idx = list(cascade_segs.keys())[0]
seg_fr = cascade_segs[seg_idx]['fr']

print(f"ORIGINAL (FR): {seg_fr}")
print()

# Intermédiaire EN
en_it = cascade_segs[seg_idx]['en_intermediate'].get('it', 'N/A')
en_ru = cascade_segs[seg_idx]['en_intermediate'].get('ru', 'N/A')

print(f"INTERMÉDIAIRE EN (pour IT): {en_it}")
print(f"INTERMÉDIAIRE EN (pour RU): {en_ru}")
print()

# Finaux
final_it = cascade_segs[seg_idx]['final'].get('it', 'N/A')
final_ru = cascade_segs[seg_idx]['final'].get('ru', 'N/A')

print(f"FINAL IT: {final_it}")
print(f"FINAL RU: {final_ru}")
print()

print("💡 Analyse: Observe-t-on des différences EN→IT vs EN→RU?")
print("   → Différences d'intermédiaires? Erreurs propagées?")
print()

# ============================================================================
# EXEMPLE 3: LONGUEUR DES TRADUCTIONS
# ============================================================================

print("="*70)
print("3. ANALYSE: LONGUEUR DES TRADUCTIONS")
print("="*70)
print()

lengths = {
    'FR': [],
    'EN_Direct': [],
    'ES_Direct': [],
    'IT_Pivot': [],
    'RU_Pivot': [],
}

for video_name in list(direct_trans.keys())[:5]:  # 5 vidéos
    for seg_idx in list(direct_trans[video_name].keys())[:10]:
        seg_fr = direct_trans[video_name][seg_idx]['fr']
        lengths['FR'].append(len(seg_fr))
        lengths['EN_Direct'].append(len(direct_trans[video_name][seg_idx]['translations'].get('en', '')))
        lengths['ES_Direct'].append(len(direct_trans[video_name][seg_idx]['translations'].get('es', '')))
        lengths['IT_Pivot'].append(len(pivot_trans[video_name][seg_idx]['translations'].get('it', '')))
        lengths['RU_Pivot'].append(len(pivot_trans[video_name][seg_idx]['translations'].get('ru', '')))

import statistics

for lang, vals in lengths.items():
    if vals:
        avg = statistics.mean(vals)
        print(f"{lang:15} → Longueur moyenne: {avg:.0f} caractères")

print()
print("💡 Observation: Quelle langue est la plus concise/développée?")
print()

# ============================================================================
# EXEMPLE 4: TYPES D'ERREURS À CHERCHER
# ============================================================================

print("="*70)
print("4. TYPES D'ERREURS À ANALYSER")
print("="*70)
print()

error_types = {
    'Contresens': 'Sens complètement opposé (ex: "oui" → "non")',
    'Omissions': 'Mots/segments oubliés (ex: "le chat noir" → "chat")',
    'Hallucinations': 'Mots ajoutés qui n\'existaient pas',
    'Termes propres': 'Noms, lieux mal traduits/conservés',
    'Accords': 'Accord genre/nombre incorrect',
    'Ponctuation': 'Ponctuation manquante/ajoutée',
    'Cascade errors': 'Erreurs FR→EN qui se propagent EN→IT/RU',
}

for error_type, description in error_types.items():
    print(f"✓ {error_type:20} : {description}")

print()
print("👉 À FAIRE: Parcourez les traductions et identifiez ces erreurs!")
print()

# ============================================================================
# EXEMPLE 5: COMPARAISON DIRECT vs PIVOT
# ============================================================================

print("="*70)
print("5. COMPARAISON: DIRECT vs PIVOT")
print("="*70)
print()

# Pour IT: Pas de modèle direct, seulement pivot
# Mais on peut comparer ES (direct) avec IT (pivot pour voir pattern)

print("Stratégies:")
print("  • DIRECT (EN, ES):  FR → EN, FR → ES (1 modèle)")
print("  • PIVOT (IT, RU):   FR → EN → IT, FR → EN → RU (2 modèles cascade)")
print()

print("Questions d'analyse:")
print("  1. Pivot perd-il de l'information? (EN intermédiaire vs direct)")
print("  2. Quelle est la perte qualité du double-hop?")
print("  3. Erreurs en cascade = E1 (FR→EN) + E2 (EN→IT)?")
print("  4. IT est-il moins bon que EN/ES?")
print()

# ============================================================================
# RÉSUMÉ
# ============================================================================

print("="*70)
print("📋 RÉSUMÉ: À INCLURE DANS VOTRE RAPPORT")
print("="*70)
print()

print("""
1. TABLEAU COMPARATIF: 10 segments exemple
   → Montrer côte à côte les traductions FR, EN, ES, IT, RU

2. ANALYSE CASCADE ERRORS:
   → Montrer FR → EN → IT avec commentaires sur propagation d'erreurs

3. TYPES D'ERREURS IDENTIFIÉES:
   → Lister les erreurs trouvées par type
   → Exemples concrets

4. STATISTIQUES:
   → Longueur moyenne par langue
   → Pourcentage de couverture (traductions réussies)

5. DISCUSSION:
   → Pourquoi pivot moins bon que direct?
   → Impact du double modèle?
   → Quand utiliser pivot vs direct?

6. FIGURES/GRAPHIQUES (optionnel):
   → Bar chart: Longueur par langue
   → Heatmap: Similitude EN vs IT/RU intermédiaires
""")

print("="*70)
print("✅ Analyse qualitative générée!")
print("="*70)

# Sauvegarder résumé
with open(OUTPUT_DIR / "qualitative_analysis_summary.txt", 'w', encoding='utf-8') as f:
    f.write("ANALYSE QUALITATIVE - RÉSUMÉ\n")
    f.write("="*70 + "\n\n")
    f.write(f"Vidéos analysées: {len(direct_trans)}\n")
    f.write(f"Segments par vidéo: 10\n")
    f.write(f"Total segments: {sum(len(v) for v in direct_trans.values())}\n\n")
    f.write(str(df_comparison))

print(f"\n✓ Résumé sauvegardé: {OUTPUT_DIR / 'qualitative_analysis_summary.txt'}")

