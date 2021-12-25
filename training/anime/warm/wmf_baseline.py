from sklearn import preprocessing as prep
import pandas as pd
import numpy as np
import pdb

def prep_standardize_dense(x):
    scaler = prep.StandardScaler().fit(x)
    x_scaled = scaler.transform(x)
    x_scaled[x_scaled > 5] = 5
    x_scaled[x_scaled < -5] = -5
    x_scaled[np.absolute(x_scaled) < 1e-5] = 0
    return scaler, x_scaled

def user_recall_at_M(M, R_hat_np, val_pref_matrix):
    ranking = np.argsort(-R_hat_np, axis=1)
    topM = ranking[:,:M]

    pref = val_pref_matrix.to_numpy()

    n = np.array([np.count_nonzero(topM[pref[:,i] > 0] == i) for i in range(pref.shape[1])])
    d = np.sum(pref > 0, axis=0)
    
    return np.mean(n[d>0] / d[d>0])

ANIME_PATH="data/anime/train_val_test/10000"
warm_user_factors=pd.read_csv("{}/10000_warm_user_factors_large.csv".format(ANIME_PATH),index_col=0)
warm_item_factors=pd.read_csv("{}/10000_warm_item_factors_large.csv".format(ANIME_PATH),index_col=0)
cold_val_pref_matrix=pd.read_csv("{}/10000_val_pref_matrix.csv".format(ANIME_PATH),index_col=0)


popularity=np.array([np.arange(cold_val_pref_matrix.shape[1])[::-1] for _ in range(cold_val_pref_matrix.shape[0])])
print("Popularity:",user_recall_at_M(100,popularity,cold_val_pref_matrix))

pref_matrix,val_pref_matrix=pd.read_csv("{}/10000_warm_pref_matrix_train_0.csv".format(ANIME_PATH),index_col=0),pd.read_csv("{}/10000_warm_pref_matrix_test_0.csv".format(ANIME_PATH),index_col=0)
pref_mask=pref_matrix>0.0


print(pref_mask.shape)
u,v=warm_user_factors.values,warm_item_factors.values



popularity=np.array([np.arange(pref_mask.shape[1])[::-1] for _ in range(pref_mask.shape[0])])
relv=u.dot(v.T)
relv[pref_mask.values]=float("-inf")
print("In-matrix:",user_recall_at_M(100,relv,val_pref_matrix))

all_u_transforms=[np.average(v[pref_mask.iloc[i].values],axis=0) for i in range(pref_mask.shape[0])]

u=np.array(all_u_transforms)

relv=u.dot(v.T)
relv[pref_mask.values]=float("-inf")
print("Out-of-matrix:",user_recall_at_M(100,relv,val_pref_matrix))

pdb.set_trace()

print("Popularity:",user_recall_at_M(100,popularity,val_pref_matrix))