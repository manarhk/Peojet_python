import abc
from datetime import datetime
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import os

# Supposons que vos fichiers CSV soient dans le même répertoire que votre script
reddit_csv_file_path = 'Python_reddit_posts.csv'
arxiv_csv_file_path = 'arxiv_data.csv'

# Classe abstraite pour la création des documents
class DocumentFactory(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def create_instance(row):
        pass

# Classe de base pour tous les types de documents
class Document:
    type = "Document" 

    def __init__(self, title, url, created_date, body, doc_id):
        self.title = title
        self.url = url
        self.created_date = created_date
        self.body = body
        self.doc_id = doc_id

    @staticmethod
    def create_instance(row):
        return Document(
            title=row['title'],
            url=row['url'],
            created_date=row['created_date'],
            body=row['body'],
            doc_id=row['id']
        )

# Classe pour les documents Reddit héritant de la classe Document
class RedditDocument(Document):
    type = "Reddit Document"

    def __init__(self, title, url, created_date, body, doc_id, num_comments, author):
        super().__init__(title, url, created_date, body, doc_id)
        self.num_comments = num_comments
        self.author = author

    @staticmethod
    def create_instance(row):
        return RedditDocument(
            title=row['title'],
            url=row['url'],
            created_date=row['created_date'],
            body=row['body'],
            doc_id=row['id'],
            num_comments=row['num_comments'],
            author=row['author']
        )

# Classe pour les documents ArXiv héritant de la classe Document
class ArxivDocument(Document):
    type = "ArXiv Document"

    def __init__(self, title, url, created_date, body, doc_id, author):
        super().__init__(title, url, created_date, body, doc_id)
        self.author = author

    @staticmethod
    def create_instance(row):
        return ArxivDocument(
            title=row['title'],
            url=row['url'],
            created_date=row['created_date'],
            body=row['body'],
            doc_id=row['id'],
            author=row['author']
        )

# Classe pour stocker les documents pertinents
class Corpus:
    def __init__(self):
        self.docs = []

    def add_document(self, document):
        self.docs.append(document)

    def get_docs_list(self):
        return self.docs

# Initialiser l'application Dash
app = dash.Dash(__name__)

# Définir la mise en page de l'application
app.layout = html.Div([
    html.H1("Recherche de Documents"),
    
    # Entrée pour le mot-clé de recherche
    dcc.Input(id='search-input', type='text', placeholder='Entrez votre recherche', className='input-box'),

    # Options de filtre
    dcc.RadioItems(
        id='filter-type',
        options=[
            {'label': 'Reddit', 'value': 'reddit'},
            {'label': 'ArXiv', 'value': 'arxiv'},
            {'label': 'Les deux', 'value': 'both'},
        ],
        value='both',  # Valeur par défaut
        labelStyle={'display': 'block'}
    ),

    dcc.Input(id='author-input', type='text', placeholder="Entrez l'auteur", className='input-box'),

    dcc.Input(id='date-input', type='text', placeholder="Entrez la date (format YYYY-MM-DD)", className='input-box'),

    # Bouton pour lancer la recherche
    html.Button('Rechercher', id='search-button', className='search-button', n_clicks=0),
    # Un élément pour afficher le nombre de résultats
    html.Div(id='result-count'),
    # Zone pour afficher les résultats
    html.Div(id='search-results')
])
#search_and_add_documents est Proposée par CHATGPT
def search_and_add_documents(search_query, dataframe, document_factory, author_query=None, date_query=None): 
    relevant_docs = []
    
    # Filtrer les lignes du DataFrame qui correspondent à la recherche
    relevant_rows = dataframe[dataframe['title'].str.contains(search_query, case=False) | dataframe['body'].str.contains(search_query, case=False)]

    # Appliquer le filtre d'auteur si spécifié
    if author_query:
        relevant_rows = relevant_rows[relevant_rows['author'].str.contains(author_query, case=False)]
    
    # Appliquer le filtre de date si spécifié
    if date_query:
        # Convertir la date entrée par l'utilisateur en objet datetime
        user_date = datetime.strptime(date_query, '%Y-%m-%d')

        # Filtrer les lignes avec des dates inférieures ou égales à la date entrée
        relevant_rows = relevant_rows[relevant_rows['created_date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ' if 'T' in x else '%Y-%m-%d %H:%M:%S') <= user_date)]

    # Créer une instance pour chaque ligne pertinente
    for _, row in relevant_rows.iterrows():
        doc_instance = document_factory.create_instance(row)
        relevant_docs.append(doc_instance)

    return relevant_docs

def count_keyword_occurrences(doc, keyword):
    return str(doc.title).lower().count(keyword.lower()) + str(doc.body).lower().count(keyword.lower())

def count_words_in_body(doc):
    # Utiliser split pour diviser le texte en mots et compter le nombre de mots
    return len(str(doc.body).split())

# Callback pour mettre à jour les résultats de la recherche
@app.callback(
    [Output('search-results', 'children'),
     Output('result-count', 'children')],
    [Input('search-button', 'n_clicks')],
    [State('search-input', 'value'),
     State('filter-type', 'value'),
     State('author-input', 'value'),
     State('date-input', 'value')]
)
def update_search_results(n_clicks, search_query, filter_type, author_query, date_query):
    # Instancier la classe Corpus pour stocker les documents pertinents
    corpus = Corpus()
    if search_query and n_clicks != 0:
        # Charger les données Reddit et ArXiv
        reddit_df = pd.read_csv(reddit_csv_file_path)
        arxiv_df = pd.read_csv(arxiv_csv_file_path)
        arxiv_df.rename(columns={'ID': 'id','Title':'title','Published':'created_date','Summary':'body','Author':'author','URL':'url'}, inplace=True)


        # Effectuer la recherche et obtenir les documents pertinents en fonction des filtres
        if filter_type == 'reddit':
            relevant_docs = search_and_add_documents(search_query, reddit_df, RedditDocument, author_query, date_query)
        elif filter_type == 'arxiv':
            relevant_docs = search_and_add_documents(search_query, arxiv_df, ArxivDocument, author_query, date_query)
        else:
            relevant_reddit_docs = search_and_add_documents(search_query, reddit_df, RedditDocument, author_query, date_query)
            relevant_arxiv_docs = search_and_add_documents(search_query, arxiv_df, ArxivDocument, author_query, date_query)
            relevant_docs = relevant_reddit_docs + relevant_arxiv_docs

        # Trier les documents en fonction du nombre d'apparitions du mot-clé
        relevant_docs.sort(key=lambda doc: count_keyword_occurrences(doc, search_query), reverse=True)

        # Ajouter les documents pertinents à l'instance de Corpus
        for doc in relevant_docs:
            corpus.add_document(doc)
        
        # Afficher les résultats
        if corpus.get_docs_list():
            result_text = [html.H3("Résultats de la recherche :")]
            for i, doc in enumerate(corpus.get_docs_list()):
                # Structurer l'affichage des résultats avec séparateurs
                result_text.extend([
                    html.Div([
                        html.P([
                            html.Strong("Titre: "), doc.title, html.Br(),
                            html.Strong("Type: "), doc.type, html.Br(),
                            html.Strong("Date: "), doc.created_date, html.Br(),
                            html.Strong("Auteur: "), doc.author, html.Br(),
                            html.Strong("URL: "), html.A(doc.url, href=doc.url, target='_blank'), html.Br(),
                            html.Strong("Texte: "), doc.body,
                        ]),
                        html.P(f"Nombre de mots dans le corps: {count_words_in_body(doc)}"),
                        html.P(f"Nombre d'apparitions du mot-clé: {count_keyword_occurrences(doc, search_query)}"),
                        html.Hr() if i < len(corpus.get_docs_list()) - 1 else None  # Ajouter le séparateur sauf pour le dernier document
                    ], className='result-item')
                ])

            # Mettre à jour le nombre de résultats trouvés
            result_count_text = f"Nombre de résultats trouvés : {len(corpus.get_docs_list())}"
            return result_text, result_count_text
        else:
            return html.P("Aucun résultat trouvé pour votre requête."), html.P("Nombre de résultats trouvés : 0")
    else:
        return html.P("Veuillez entrer un mot-clé de recherche et cliquer sur le bouton."), html.P("Nombre de résultats trouvés : 0")

# Exécuter l'application
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))  # Use port 8080 if no PORT environment variable is set
    app.run_server(debug=False, host='0.0.0.0', port=port)
