# DatasetBuilder
# 🧠 Wolof Sentiment Annotation Pipeline

Ce projet propose un pipeline complet d'extraction, de nettoyage et d'annotation automatique de textes en wolof pour l'analyse de sentiments.

## 📦 Contenu du dépôt

- `DatasetBuilder.py` : Script Python pour extraire, filtrer et nettoyer les messages depuis des fichiers `.txt`, `.csv` ou `.xlsx`.
- `dataset.csv` : Fichier de sortie contenant les textes en wolof nettoyés, prêts à être annotés.
- `notebook_kaggle.ipynb` : Notebook exécuté sur Kaggle avec GPU pour l’annotation automatique.

## ⚙️ Fonctionnement du Pipeline

### 1. Prétraitement avec `DatasetBuilder.py`

Le script :
- Supprime les messages en français et en anglais.
- Nettoie les messages (numéros, balises HTML, emojis, noms sénégalais...).
- Gère plusieurs formats d'entrée (WhatsApp `.txt`, `.csv`, `.xlsx`).
- Produit un fichier `dataset.csv` avec une colonne `texte`.

### 2. Annotation Automatique sur Kaggle

Le notebook :
- Utilise deux modèles Hugging Face :
  - `nlptown/bert-base-multilingual-uncased-sentiment`
  - `cardiffnlp/twitter-xlm-roberta-base-sentiment`
- Chaque texte est traité 3 fois par modèle (variation originale, ponctuée, majuscule).
- Résultats stockés dans 6 colonnes `annotation1` à `annotation6`.
- Vote majoritaire pour déterminer le sentiment final.

### 🔢 Répartition des sentiments finaux

| Sentiment | Nombre | Pourcentage |
|-----------|--------|-------------|
| Négatif   | 67 834 | 73.6 %      |
| Positif   | 15 129 | 16.4 %      |
| Neutre    | 9 223  | 10.0 %      |

## 📁 Données & Résultats

- 🔗 Google Drive (CSV & sorties) : [Accéder au dossier](https://drive.google.com/drive/folders/13OLdW_qJRCdWMlp_6guLtzLb4ywwJj1m?usp=sharing)
- 📊 Kaggle Notebook : [Voir sur Kaggle](https://www.kaggle.com/code/massina0/fork-of-wolof-sentiment-classification)

## 📜 Licence

Ce projet est proposé à des fins académiques et expérimentales.

---

**Contact** : [Massina sur Kaggle](https://www.kaggle.com/code/massina0)
