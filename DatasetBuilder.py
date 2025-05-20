import re
import random
import csv
import os
import sys
from langdetect import detect, DetectorFactory
import pandas as pd
import argparse
from pathlib import Path

# Assurer des résultats cohérents pour langdetect
DetectorFactory.seed = 0

def parse_arguments():
    """Analyser les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(description='Extraction de messages non-français/anglais depuis différentes sources.')
    parser.add_argument('--input', '-i', required=True, help='Fichier d\'entrée (txt, csv, xlsx, xls)')
    parser.add_argument('--output', '-o', default='wolof_dataset.csv', help='Fichier de sortie CSV (défaut: wolof_dataset.csv)')
    parser.add_argument('--languages', '-l', default='fr,en', help='Langues à exclure, séparées par des virgules (défaut: fr,en)')
    parser.add_argument('--column', '-c', help='Nom de la colonne à utiliser (pour CSV/Excel)')
    parser.add_argument('--append', '-a', action='store_true', help='Ajouter au fichier existant au lieu de l\'écraser')
    parser.add_argument('--threshold', '-t', type=float, default=0.8, 
                        help='Seuil de détection pour les messages multilingues (0-1, défaut: 0.8)')
    return parser.parse_args()

# 📦 Liste des noms/prénoms à supprimer (mettre tout en minuscule)
def charger_noms_senegalais():
    """Charge la liste des noms sénégalais."""
    noms_senegalais = {
        "Niass", "Niasse", "Pouye Seck", "Sock", "Taye", "Thiam", "Thiongane", "Wade", "Badji", "Badiatte", "Biagui", "Bassene", "Bodian", "Coly", "Diamacoune", "Diatta","Diadhiou", "Diedhiou", "Deme", "Dieme", "Djiba", "Coly", "Ehemba", "Goudiaby",
        "Himbane", "Mane", "Manga", "Sagna", "Sambou", "Sane", "Sonko", "Tamba", "Tendeng", "Badji", "Gomis", "Vieira", "Carvalho", "Mendy", "Preira", "Correa", "Basse", "Sylva", "Fernandez", "Da Costa", "Bakhoum", "Diop", "Diagne", "Gaye", "Gueye", "Ndoye", "Ndiour", "Samb", "Baloucoune", "Bandiacky", "Boissy", "Diompy",
        "Dupa", "Kabely", "Kaly", "Kantoussan", "Kassoka", "Kayounga", "Keny", "Malack", "Malèle", "Malomar", "Malou", "Mandika", "Mandiouban", "Mancabou", "Mantanne", "Mbampassy", "Médou", "Minkette", "Nabaline", "Nadiack", "Napel", "Ndecky", "Ndeye", "Niouky", "Ntab", "Nzale", "Panduppy", "Samy", "Boubane", "Bonang", "Bianquinch", "Bindian",
        "Bendian", "Bangonine", "Bapinye", "Bidiar", "Bangar", "Sadio", "Vieira", "Lopez", "Marques", "Preira", "Ndiaye", "Diouf", "Ndong", "Dioh", "Senghor", "Faye", "Dior", "Dione", "Seye", "Diongue", "Sene", "Dieye", "Sarr", "Seck", "Diaher", "Bop", "Kitane", "Kital", "Acc", "Aïdara", "Athie", "Aw", "Ba", "Baby", "Balde", "Barro", "Barry", "Bathily",
        "Bousso", "Camara", "Cisse", "Dia", "Diamanka", "Diallo", "Diao", "Diaw", "Fassa", "Fofana", "Gadio", "Galadio", "Ka", "Kane", "Maal", "Mbow", "Lo", "Ly", "Sall", "Seydi", "Sow", "Sy", "Sylla", "Tall", "Thiam", "Wane", "Wone", "Yock", "Amar", "Babou", "Diagne", "Diakhoumpa", "Goumbala", "Saady", "Sabara", "Sougou", "Sougoufara", "Tandini", "Tandine", "Toure", "Diakite", "Diakho",
        "Diandy", "Aidara", "Bathily", "Camara", "Cisse", "Cissoko", "Coulibaly", "Diawara", "Djimera", "Dabo", "Doumbia", "Doumbia", "Diabang", "Diakhate", "Diabira", "Dansokho", "Diarra", "Drame",
        "Doucoure", "Fadiga", "Fofana", "Gakou", "Gakou", "Gandega", "Kante", "Kanoute", "Keita", "Koita", "Konate", "Sadio", "Sakho", "Sakho", "Samassa", "Sawane", "Sidibe", "Sissoko", "Soumare", "Tandjigora",
        "Timera", "Traore", "Toure", "Wague", "Yatera", "Boye", "Demba", "Diack", "Diarra", "Dieng", "Diop", "Fall", "Gningue", "Hanne", "Kane", "Kasse", "Leye", "Loum", "Marone", "Mbathie", "mbaye", "mbengue",
        "mbodj", "mboup", "mbow", "ndao", "nder", "ndiaye", "ndour", "niane", "niang","Abibatou", "Aby", "Absa", "Adama", "Adiouma", "Adji", "Adja", "Aïcha", "Aïda", "Aïssatou",
        "Akinumelob", "Alima", "Alimatou", "Alinesiitowe", "Aloendisso", "Altine", "Ama", "Aminata", "Aminta", "Amy", "Amina", "Anta",
        "Arame", "Assa", "Assietou", "Astou", "Ata", "Atia", "Awa", "Awentorébé", "Ayimpen", "Banel", "Batouly", "Bigué", "Billé",
        "Binta", "Bineta", "Binette", "Binta", "Bintou", "Borika", "Bougouma", "Boury", "Bousso", "Ciramadi", "Codou", "Combé",
         "Coudouution", "Coumba", "Coumboye", "Coura", "Daba", "Dado", "Daka", "Debbo", "Défa", "Dewel", "Dewene", "Diakher", "Diakhou",
         "Dialikatou", "Dianké", "Diariatou", "Diarra", "Diary", "Dibor", "Dieourou", "Dior", "Diouma", "Djaly", "Djébou", "Djeynaba",
         "Dkikel", "Djilane", "Enfadima", "Fabala", "Fabinta", "Fadima", "Fakane", "Fama", "Fanta", "Farmata", "Fatima", "Fatou", "Fatoumatou",
         "Fily", "Garmi", "Gnagna", "Gnilane", "Gnima", "Gouya", "Guignane", "Guissaly", "Haby", "Hawa", "Heinda", "Holèl", "Issate",
         "Kankou", "Karimatou", "Kenbougoul", "Kéwé", "Kadiali", "Khadija", "Khadijatou", "Khady", "Khar", "Khary", "Khayfatte", "Khoudia",
         "Khoudjedji", "Khoumbaré", "Kiné", "Korka", "Laf", "Lama", "Léna", "Lika", "Lissah", "Liwane", "Mada", "Madior", "Madjiguène",
         "Maguette", "Mahawa", "Mame", "Mamina", "Manthita", "Marème", "Mariama", "Mamassa", "Mane", "Maty", "Mayatta", "Maymouna", "Mbarou",
         "Mbayeng", "Mbissine", "Mbossé", "Mingue", "Mintou", "Mouskéba", "Nafi", "Nbieumbet", "Ndella", "Ndeye", "Ndiarenioul", "Ndiasse",
         "Ndiaty", "Ndiémé", "Ndioba", "Ndiolé", "Ndioro", "Ndombo", "Néné", "Neyba", "Ngoné", "Ngosse", "Nguenar", "Nguissaly",
         "Niakuhufosso", "Niali", "Nialine", "Ningou", "Nini", "Niouma", "Oulèye", "Ouly", "Oulimata", "Oumou", "Oumy", "Oureye", "Penda",
         "Raby", "Raki", "Rama", "Ramatoulaye", "Ramata", "Rokhaya", "Roubba", "Roughy", "Sadio", "Safiétou", "Safi", "Sagar", "Sahaba",
         "Salimata", "Salamata", "Sanakha", "Sarratou", "Saoudatou", "Sawdiatou", "Selbé", "Sell", "Seynabou", "Seyni", "Sibett", "Siga",
         "Sira", "Sirabiry", "Soda", "Sofiatou", "Sofietou", "Sokhna", "Souadou", "Soukeye", "Soukeyna", "Tabara", "Tacko", "Taki", "Tening",
         "Téwa", "Tiné", "Thiomba", "Thiony", "Thioro", "Thioumbane", "Tocka", "Tokoselle", "Toly", "Walty", "Yadicone", "Yacine", "Yandé",
         "Yaye","Abba", "Abdallah", "Abdou", "Abdoulatif", "Abdoulaye", "Abdourahmane", "Ablaye", "Abou", "Adama",
        "Agouloubene", "Aïnina", "Aladji", "Alassane", "Albouri", "Alfa", "Alfousseyni", "Aliou", "Alioune", "Allé", "Almamy", "Amadou",
        "Amara", "Amath", "Amidou", "Ansoumane", "Anta", "Arfang", "Arona", "Assane", "Ass", "Aziz", "Baaba", "Babacar", "Babou", "Badara",
        "Badou", "Bacar", "Baïdi", "Baila", "Bakari", "Ballago", "Balla", "Bamba", "Banta", "Bara", "Bassirou", "Bathie", "Bayo", "Becaye",
        "Bilal", "Biram", "Birane", "Birima", "Biry", "Bocar", "Bodiel", "Bolikoro", "Boubacar", "Boubou", "Bougouma", "Bouly", "Bouna",
        "Bourkhane", "Bransan", "Cheikh", "Chérif", "Ciré", "Daly", "Dame", "Daouda", "Daour", "Demba", "Dényanké", "Diakhou", "Dial",
        "Dialamba", "Dialegueye", "Dianco", "Dicory", "Diégane", "Diène", "Dierry", "Diokel", "Diokine", "Diomaye", "Djibo", "Djibril",
        "Djiby", "Doudou", "Dramane", "ElHadj", "Elimane", "Facourou", "Fadel", "Falilou", "Fallou", "Famara", "Farba", "Fatel", "Fodé",
        "Fodey", "Fodié", "Foulah", "Galaye", "Gaoussou", "Gora", "Gorgui", "Goumbo", "Goundo", "Guidado", "Habib", "Hadiya", "Hady",
        "Hamidou", "Hammel", "Hatab", "Iba", "Ibrahima", "Ibou", "Idrissa", "Insa", "Ismaïl", "Ismaïla", "Issa", "Isshaga", "Jankebay",
        "Jamuyon", "Kader", "Kainack", "Kalidou", "Kalilou", "Kambia", "Kao", "Kaourou", "Karamo", "Kéba", "Khadim", "Khadir", "Khalifa",
        "Khamby", "Khary", "Khoudia", "Khoule", "Kor", "Koutoubo", "Lamine", "Lamp", "Landing", "Lat", "Latif", "Latsouck", "Latyr", "Lémou",
        "Léou", "Leyti", "Libasse", "Limane", "Loumboul", "Maba", "Macky", "Macodou", "Madia", "Madické", "Mady", "Mactar", "Maffal",
        "Maguette", "Mahécor", "Makan", "Malal", "Malamine", "Malang", "Malaw", "Malick", "Mallé", "Mamadou", "Mamour", "Mansour", "Maodo",
        "Mapaté", "Mar", "Massamba", "Massar", "Masseck", "Mbagnick", "Mbakhane", "Mbamoussa", "Mbar", "Mbaye", "Mébok", "Médoune", "Meïssa",
        "Modou", "Moktar", "Momar", "Mor", "Mountaga", "Moussa", "Moustapha", "Namori", "Ndane", "Ndiack", "Ndiaga", "Ndiankou", "Ndiaw",
        "Ndiawar", "Ndiaya", "Ndiogou", "Ndiouga", "Ndongo", "Ngagne", "Ngor", "Nguénar", "Niakar", "Niankou", "Niokhor", "Nouh", "Nouha",
        "Npaly", "Ogo", "Omar", "Opa", "Oumar", "Oury", "Ousmane", "Ousseynou", "Papa", "Pape", "Papis", "Pathé", "Racine", "Sadibou",
        "Sacoura", "Saër", "Sahaba", "Saïdou", "Sakhir", "Salam", "Salif", "Saliou", "Saloum", "Samba", "Samori", "Samsidine", "Sandigui",
        "Sankoun", "Sanokho", "Sécouba", "Sédar", "Sékou", "Semou", "Senghane", "Serigne", "Seyba", "Seydina", "Seydou", "Sibiloumbaye",
        "Sidate", "Sidy", "Siéka", "Sihalébé", "Sihounke", "Silly", "Socé", "Sogui", "Soireba", "Solal", "Sonar", "Souleymane", "Soundjata",
        "Sounkarou", "Souty", "Tafsir", "Talla", "Tamsir", "Tanor", "Tayfor", "Tekheye", "Tété", "Thiawlo", "Thierno", "Thione", "Tijane",
        "Tidjane", "Toumani", "Vieux", "Wagane", "Waly", "Wandifing", "Wasis", "Woula", "Woury", "Yacouba", "Yafaye", "Yakou", "Yankhoba",
        "Yerim", "Yero", "Yoro", "Yougo", "Younouss", "Youssou", "Yussu", "Youssoufa"
    }
    return set(nom.lower() for nom in noms_senegalais)

def est_non_langue_exclue(message, langues_exclues, threshold=0.8):
    """
    Vérifie si le message n'est pas dans les langues exclues.
    
    Args:
        message: Texte à analyser
        langues_exclues: Liste des langues à exclure
        threshold: Seuil de fiabilité pour la détection
        
    Returns:
        Boolean: True si le message n'est pas dans les langues exclues
    """
    if not message or len(message.strip()) < 5:
        return False
    
    try:
        langue = detect(message)
        return langue not in langues_exclues
    except Exception as e:
        print(f"Erreur de détection pour: '{message[:30]}...' - {str(e)}")
        return False

def nettoyer_contenu(message, noms_senegalais):
    """
    Nettoie le contenu en supprimant les numéros, mentions, liens, balises et noms.
    
    Args:
        message: Texte à nettoyer
        noms_senegalais: Ensemble des noms à supprimer
        
    Returns:
        str: Message nettoyé
    """
    if not isinstance(message, str):
        if pd.isna(message):
            return ""
        message = str(message)
        
    # Nettoyage de base
    message = re.sub(r'\+?\d{2,3}[\s\-]?\d{2,3}[\s\-]?\d{2,3}[\s\-]?\d{2,3}', '', message)  # numéros
    message = re.sub(r'@\w+', '', message)                                                  # mentions
    message = re.sub(r'https?://\S+|www\.\S+', '', message)                                 # liens
    message = re.sub(r'<[^>]+>', '', message)                                               # balises HTML
    
    # Suppression des métadonnées WhatsApp et caractères spéciaux
    message = re.sub(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U000024C2-\U0001F251]+', '', message)  # emojis
    
    # Suppression des noms sénégalais
    mots = message.split()
    mots_nettoyes = [mot for mot in mots if mot.lower() not in noms_senegalais]
    
    return ' '.join(mots_nettoyes).strip()

def extraire_messages_whatsapp(fichier_entree, noms_senegalais, langues_exclues, threshold=0.8):
    """Extrait les messages à partir d'un fichier d'exportation WhatsApp."""
    messages_utiles = []
    
    with open(fichier_entree, "r", encoding="utf-8", errors="ignore") as fichier:
        lignes = fichier.readlines()
        
        for ligne in lignes:
            # Ignorer les messages système WhatsApp
            if re.search(r'chiffrés de bout en bout|a créé le groupe|vous a ajouté|a ajouté|a changé le sujet|a modifié l\'icône|épingle un message|<Médias omis>|<Ce message a été modifié>|activé l\'approbation|changé de numéro', ligne, re.IGNORECASE):
                continue
                
            # Format de message WhatsApp: date, heure - nom: message
            match = re.match(r'\d{2}[/.-]\d{2}[/.-]\d{2,4},?\s*\d{1,2}:\d{2}(?:\s*(?:AM|PM))?\s*-\s*[^:]+:\s*(.+)', ligne)
            if match:
                message = match.group(1).strip()
                message_nettoye = nettoyer_contenu(message, noms_senegalais)
                if message_nettoye and est_non_langue_exclue(message_nettoye, langues_exclues, threshold):
                    messages_utiles.append(message_nettoye)
            # Essayer le format alternatif (sans tiret)
            elif "[" in ligne and "]" in ligne:
                match = re.match(r'\[.*?\]\s*([^:]+):\s*(.+)', ligne)
                if match:
                    message = match.group(2).strip()
                    message_nettoye = nettoyer_contenu(message, noms_senegalais)
                    if message_nettoye and est_non_langue_exclue(message_nettoye, langues_exclues, threshold):
                        messages_utiles.append(message_nettoye)
    
    return messages_utiles

def detecter_colonnes_message(df):
    """Détecte automatiquement les colonnes contenant des messages."""
    colonnes_potentielles = ['message', 'messages', 'text', 'texts', 'contenu', 'texte', 'sentence', 'sentences', 'tweet','tweets']
    
    # Rechercher par nom exact (insensible à la casse)
    for col in colonnes_potentielles:
        cols_match = [c for c in df.columns if c.lower() == col]
        if cols_match:
            return cols_match[0]
    
    # Rechercher par nom partiel
    for col in colonnes_potentielles:
        cols_match = [c for c in df.columns if col in c.lower()]
        if cols_match:
            return cols_match[0]
    
    # Si une seule colonne est présente, la retourner
    if len(df.columns) == 1:
        return df.columns[0]
    
    return None

def extraire_messages_tabular(fichier_entree, noms_senegalais, langues_exclues, nom_colonne=None, threshold=0.8):
    """Extrait les messages à partir d'un fichier CSV ou Excel."""
    messages_utiles = []
    extension = Path(fichier_entree).suffix.lower()
    
    try:
        # Charger les données selon le format
        if extension == '.csv':
            # Essayer d'abord avec l'encodage UTF-8
            try:
                df = pd.read_csv(fichier_entree, encoding='utf-8')
            except UnicodeDecodeError:
                # Si échec, essayer avec Latin-1
                df = pd.read_csv(fichier_entree, encoding='latin1')
        elif extension in ['.xlsx', '.xls']:
            df = pd.read_excel(fichier_entree)
        else:
            print(f"Format de fichier non pris en charge: {extension}")
            return []
            
        # Détecter automatiquement la colonne contenant les messages
        if not nom_colonne:
            nom_colonne = detecter_colonnes_message(df)
            if not nom_colonne:
                print("Aucune colonne pertinente trouvée. Utilisation de la première colonne.")
                nom_colonne = df.columns[0]
                
        print(f"Utilisation de la colonne '{nom_colonne}' pour l'extraction")
            
        # Extraire et nettoyer les messages
        for message in df[nom_colonne]:
            message_nettoye = nettoyer_contenu(message, noms_senegalais)
            if message_nettoye and est_non_langue_exclue(message_nettoye, langues_exclues, threshold):
                messages_utiles.append(message_nettoye)
                
    except Exception as e:
        print(f"Erreur lors de l'extraction du fichier {fichier_entree}: {str(e)}")
        
    return messages_utiles

def enregistrer_resultats(messages, fichier_sortie, mode="w"):
    """Enregistre les messages dans un fichier CSV."""
    # Créer le répertoire de sortie si nécessaire
    os.makedirs(os.path.dirname(os.path.abspath(fichier_sortie)), exist_ok=True)
    
    with open(fichier_sortie, mode, encoding="utf-8", newline='') as f_out:
        writer = csv.writer(f_out)
        
        # Écrire l'en-tête uniquement en mode écriture
        if mode == "w":
            writer.writerow(["texte"])
            
        # Écrire les messages
        for message in messages:
            writer.writerow([message])
            
    print(f"✅ {len(messages)} messages ont été {'ajoutés à' if mode == 'a' else 'écrits dans'} '{fichier_sortie}'")

def main():
    """Fonction principale."""
    args = parse_arguments()
    
    # Paramètres
    fichier_entree = args.input
    fichier_sortie = args.output
    langues_exclues = args.languages.split(',')
    nom_colonne = args.column
    mode = "a" if args.append else "w"
    threshold = args.threshold
    
    print(f"🔍 Analyse du fichier '{fichier_entree}'")
    print(f"🚫 Langues exclues: {', '.join(langues_exclues)}")
    
    # Charger les noms sénégalais
    noms_senegalais = charger_noms_senegalais()
    
    # Extraire les messages selon le type de fichier
    messages_utiles = []
    extension = Path(fichier_entree).suffix.lower()
    
    if extension == '.txt':
        # Essayer d'abord le format WhatsApp
        messages_utiles = extraire_messages_whatsapp(fichier_entree, noms_senegalais, langues_exclues, threshold)
        
        # Si très peu de messages extraits, essayer comme fichier texte normal
        if len(messages_utiles) < 5:
            print("Format WhatsApp non détecté, traitement comme fichier texte brut...")
            with open(fichier_entree, 'r', encoding='utf-8', errors='ignore') as f:
                lignes = f.readlines()
                for ligne in lignes:
                    message_nettoye = nettoyer_contenu(ligne.strip(), noms_senegalais)
                    if message_nettoye and est_non_langue_exclue(message_nettoye, langues_exclues, threshold):
                        messages_utiles.append(message_nettoye)
    
    elif extension in ['.csv', '.xlsx', '.xls']:
        messages_utiles = extraire_messages_tabular(fichier_entree, noms_senegalais, langues_exclues, nom_colonne, threshold)
    
    else:
        print(f"❌ Format de fichier '{extension}' non pris en charge.")
        sys.exit(1)
    
    # Mélanger les messages pour une meilleure diversité
    random.shuffle(messages_utiles)
    
    # Enregistrer les résultats
    enregistrer_resultats(messages_utiles, fichier_sortie, mode)

if __name__ == "__main__":
    main()

