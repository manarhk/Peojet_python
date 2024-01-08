import pandas as pd

class DataHandler:
    def __init__(self, csv_file):
        self.df = pd.read_csv(csv_file)

    def filter_data(self, value):
        # Faire la recherche dans les colonnes 'title' et 'body'
        filtered_df = self.df[self.df['title'].str.contains(value, case=False) | self.df['body'].str.contains(value, case=False)]
        return filtered_df
