# Importation des bibliothèques nécessaires
import praw  # Bibliothèque d'accès à l'API Reddit
import pandas as pd  # Bibliothèque pour la manipulation de données en Python

# Configuration de l'accès à l'API Reddit
reddit = praw.Reddit(
    client_id='sq1EANIMnUKWuqceKXTYEA',  # Identifiant client pour l'application Reddit
    client_secret='2AJg8V4sHB2EzusCjpaaoZFelo7q2w',  # Clé secrète pour l'application Reddit
    user_agent='Myapp'  # Nom de l'agent utilisateur pour l'application Reddit
)

# Initialisation d'une liste pour stocker les données des publications Reddit
posts = []

# Accès aux publications dans la catégorie 'python'
ml_subreddit = reddit.subreddit('python')

# Récupération des 100 premières publications populaires
for post in ml_subreddit.hot(limit=100):
    posts.append([
        post.title,
        post.score,
        post.id,
        post.subreddit,
        post.url,
        post.num_comments,
        post.selftext,
        post.created
    ])

# Création d'un DataFrame pandas à partir des données collectées
posts = pd.DataFrame(
    posts,
    columns=['title', 'score', 'id', 'subreddit', 'url', 'num_comments', 'body', 'created']
)

# Affichage du DataFrame
print(posts)

# Enregistrement des données dans un fichier CSV
posts.to_csv('Python_reddit_posts.csv', index=False, columns=['title', 'score', 'id', 'subreddit', 'url', 'num_comments', 'body', 'created'])

# Fonction pour charger les données à partir d'un fichier CSV
def load_data(file_path):
    return pd.read_csv(file_path)

# Fonction pour rechercher une requête dans la colonne 'title' du jeu de données
def search_query(query, data):
    # Recherche d'une correspondance insensible à la casse dans la colonne 'title'
    results = data[data['title'].str.contains(query, case=False, na=False)]
    return results

# Fonction principale de l'application
def app():
    file_path = 'Python_reddit_posts.csv'  # Chemin vers le fichier de données (à adapter)
    data = load_data(file_path)
    
    query = input("Entrez votre requête de recherche : ")
    results = search_query(query, data)
    
    if not results.empty:
        print("Résultats de la recherche :")
        print(results)
    else:
        print("Aucun résultat trouvé pour votre requête.")

# Exécution de l'application
app()
