from torch.utils.data import Dataset
import pandas as pd
import numpy as np
from abc import abstractmethod

class RecommendationDataset(Dataset):
    def __init__(self, index_path, animes_path, recommendations_path):
        self.rc_path = recommendations_path
        self.rc_data = pd.read_csv(self.rc_path)
        
        self.path=animes_path
        self.data=pd.read_csv(self.path)

        indices=list(map(int,open(index_path,'r').readlines()))
        self.index_map=dict(zip(indices,range(len(indices))))
    

    def __len__(self):
        return len(self.rc_data)

    def __getitem__(self, idx):
        id_1=int(self.rc_data["show1"][idx])
        id_2=int(self.rc_data["show2"][idx])
        data_1=self.data.iloc[self.index_map[id_1]].values
        data_2=self.data.iloc[self.index_map[id_2]].values
        return np.concatenate((data_1,data_2,self.rc_data.iloc[idx,2:]))

    @abstractmethod
    def __preprocess__(self,idx):
        #varies for different baseline methods
        pass

    @abstractmethod
    def __sample__(self):
        pass

if __name__ == "__main__":
    rec_data=RecommendationDataset("anime_index_map.txt","animes.csv","recs.csv")
    print(rec_data.__getitem__(2))