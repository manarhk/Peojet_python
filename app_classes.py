from dash import html, dash_table, dcc
from data_handler import DataHandler
import pandas as pd

class AppLayout:
    def __init__(self):
        self.data_handler = DataHandler('C:/Users/User/Desktop/projet_python/projet_python/Python_reddit_posts.csv')
       
        self.layout = html.Div(className='container', children=[
            html.H1("Recherche de Résultats", style={'textAlign': 'center'}),
            html.Div(className='search-container', children=[
                dcc.Input(id='input-box', type='text', placeholder='Entrez votre recherche', className='input-box'),
                html.Button('Rechercher', id='search-button', className='search-button',n_clicks=0),
            ]),
            html.Div(id='output-container')
        ])

    def get_layout(self):
        return self.layout
    def get_data_handler(self):
        return self.data_handler
