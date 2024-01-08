# Importation des modules nécessaires
from dash.dependencies import Input, Output, State
from dash import html, dcc
from dash import Dash
import pandas as pd
from app_classes import AppLayout  # Importation d'une classe personnalisée pour la mise en page de l'application

# Création d'une instance de la classe AppLayout pour définir la mise en page de l'application
app_layout = AppLayout()

# Création d'une application Dash avec une feuille de style externe
app = Dash(__name__, external_stylesheets=['assets/styles.css'])

# Définition de la mise en page de l'application en utilisant la classe AppLayout
app.layout = app_layout.get_layout()

# Callback pour mettre à jour la sortie (output-container) en fonction des interactions utilisateur
@app.callback(
    Output('output-container', 'children'),  # La sortie est la section 'output-container' de la mise en page
    [Input('search-button', 'n_clicks')],  # L'entrée est le nombre de clics sur le bouton de recherche
    [State('input-box', 'value')]  # L'état représente la valeur actuelle dans la boîte de saisie
)
def update_output(n_clicks, value):
    if value and n_clicks != 0:  # Vérification que la valeur n'est pas vide et que le bouton de recherche a été cliqué
        data = app_layout.get_data_handler()  # Obtention d'un gestionnaire de données personnalisé depuis la classe AppLayout
        dataframe = pd.DataFrame(data.filter_data(value))  # Filtrage des données en fonction de la valeur de la boîte de saisie

        # Création d'un tableau HTML pour afficher les résultats
        result_table = html.Table(
            # Header du tableau
            [html.Tr([html.Th('Titre'), html.Th('URL'), html.Th('Body')])] +
            # Lignes de données
            [html.Tr([html.Td(dataframe.iloc[i]['title']),
                      html.Td(dcc.Link(dataframe.iloc[i]['url'], href=dataframe.iloc[i]['url'], target='_blank')),
                      html.Td(dataframe.iloc[i]['body'])]) for i in range(len(dataframe))]
        )
        return result_table  # Retourne le tableau résultant pour affichage dans 'output-container'

# Exécution de l'application en mode débogage
if __name__ == '__main__':
    app.run_server(debug=True)
