from torch.utils.data import Dataset
import pandas as pd

class AnimeDataset(Dataset):
    def __init__(self, animes_path):
        self.animes_path=animes_path
        self.data=pd.read_csv(self.animes_path)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data.iloc[idx].values

class RecommendationDataset(Dataset):
    def __init__(self, recommendations_path):
        self.rc_path = recommendations_path
        self.rc_data = pd.read_csv(self.rc_path)

    def __len__(self):
        return len(self.rc_data)

    def __getitem__(self, idx):
        return self.rc_data.iloc[idx].values

if __name__ == "__main__":
    anime_data=AnimeDataset("animes.csv")
    anime_data.__getitem__(1)
    rec_data=RecommendationDataset("recs.csv")
    rec_data.__getitem__(13)