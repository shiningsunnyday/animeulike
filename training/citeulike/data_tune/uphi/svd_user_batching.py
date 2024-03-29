# -*- coding: utf-8 -*-
"""CiteULike - BERT GRADIENT ACCUMULATION (static).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-RKLESrmv8Yow6eSeNGA2CwPdCqZrgor
"""



import pandas as pd
from torch.utils.data import Dataset
import os
os.environ['HOME']="dfs/user/msun415"
import pdb
import numpy as np
from abc import abstractmethod
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from typing import List
import torch
from torch.nn import functional as F
import random
import transformers
import torch.nn as nn
import itertools
from torch.utils.data import DataLoader
import time
import argparse
parser = argparse.ArgumentParser()

parser.add_argument('-d', action='store',
                    dest='devices',type=str,
                    help='devices ids, comma sep')
parser.add_argument('-b', action='store',
                    dest='batch_size',
                    help='batch size')       

parser.add_argument('-n', action='store',
                    dest='num_workers',
                    help='num workers')                          

parser.add_argument('-a', action='store',
                    dest='num_accumulation_steps',
                    help='number of accumulation steps') 
                 
                    
parser.add_argument('-m', action='store',
                    dest='mode',
                    help='anime2vec mode')

parser.add_argument("-u",action='store',dest='svd_avg',help='whether to avg svd'                    

results = parser.parse_args()
os.environ['CUDA_VISIBLE_DEVICES']=results.devices
device = "cuda:0"
BATCH_SIZE,NUM_WORKERS=int(results.batch_size),int(results.num_workers)
NUM_ACCUMULATION_STEPS=int(results.num_accumulation_steps)
assert BATCH_SIZE*NUM_ACCUMULATION_STEPS==100, "to be consistent with DropoutNet"
LR_DECAY_RATE=1.0

mode=results.mode
assert mode in {"bert-pretrained","tfidf","bert-biobert"}

NUM_EPOCHS=80
MOMENTUM=0.0

EMBEDDING_PATH="cached/citeulike/{}/".format(mode)
#one of bert-pretrained, bio-bert, tfidf

LR_SCALE_FACTOR=BATCH_SIZE*NUM_ACCUMULATION_STEPS/100



class DropoutNet(nn.Module):
    def __init__(self, **kwargs):
        super().__init__()
        assert {"item_drop_p","latent_dim","hidden_dims"}.issubset(set(kwargs.keys()))    
        for (k,v) in kwargs.items():
            setattr(self,k,v)

        self.V_dict=v_dict
        self.U_dict=u_dict 



        #LAYERS
        prev_dim=self.latent_dim+self.anime_dim
        for (i,hidden_dim) in enumerate(self.hidden_dims):            
            hidden_v=nn.Linear(prev_dim,hidden_dim)
            nn.init.normal_(hidden_v.weight,std=0.01)
            nn.init.zeros_(hidden_v.bias)
            hidden_u=nn.Linear(prev_dim,hidden_dim)
            nn.init.normal_(hidden_u.weight,std=0.01)
            nn.init.zeros_(hidden_u.bias)
            setattr(self,"hidden_u_{}".format(i),nn.DataParallel(hidden_u))
            setattr(self,"hidden_v_{}".format(i),nn.DataParallel(hidden_v))        
            setattr(self,"hidden_u_{}_norm".format(i),nn.DataParallel(nn.BatchNorm1d(hidden_dim)))
            setattr(self,"hidden_v_{}_norm".format(i),nn.DataParallel(nn.BatchNorm1d(hidden_dim)))            
            prev_dim=hidden_dim
        
        activation_options={"relu":nn.ReLU(),"sigmoid":nn.Sigmoid(),"tanh":nn.Tanh(),"identity":nn.Identity()}
        self.non_linearity=activation_options[self.activation] if "activation" in kwargs else nn.Identity()
        f_u=nn.Linear(self.hidden_dims[-1],self.latent_dim)
        nn.init.normal_(f_u.weight,std=0.01)
        nn.init.zeros_(f_u.bias)
        self.f_u=nn.DataParallel(f_u)        
        f_v=nn.Linear(self.hidden_dims[-1],self.latent_dim)
        nn.init.normal_(f_v.weight,std=0.01)
        nn.init.zeros_(f_v.bias)
        self.f_v=nn.DataParallel(f_v)
        self.f_u_cache={}
        self.f_v_cache={}


    def forward(self,u,v,u_phi,v_phi,u_inds,v_inds,y,eval=False):
        #note we're using ids, not indices
        
        B=u.shape[0]
        if eval:
            u_ind_mask=np.array(list(filter(lambda i:u_inds[i] not in self.f_u_cache,range(len(u_inds)))))
            v_ind_mask=np.array(list(filter(lambda i:v_inds[i] not in self.f_v_cache,range(len(v_inds)))))
            u,u_phi,v,v_phi=u[u_ind_mask],u_phi[u_ind_mask],v[v_ind_mask],v_phi[v_ind_mask]
            u_ind_mask,v_ind_mask=u_ind_mask.astype(int),v_ind_mask.astype(int)  

        u_mask=torch.rand_like(u)<self.user_drop_p
        u=u_mask*u
        v_mask=torch.rand_like(v)<self.item_drop_p
        v=v_mask*v

        
        phi_u=torch.cat((u,u_phi),axis=1)
        phi_v=torch.cat((v,v_phi),axis=1)
        for (i,hidden_dim) in enumerate(self.hidden_dims):
            phi_u=getattr(self,"hidden_u_{}".format(i))(phi_u)
            phi_v=getattr(self,"hidden_v_{}".format(i))(phi_v)
            phi_u=getattr(self,"hidden_u_{}_norm".format(i))(phi_u)
            phi_v=getattr(self,"hidden_v_{}_norm".format(i))(phi_v)
            phi_u=self.non_linearity(phi_u)
            phi_v=self.non_linearity(phi_v)

        f_u=self.f_u(phi_u)
        f_v=self.f_v(phi_v)

        if eval:
            for (u_ind,f_u_) in dict(zip(u_inds[u_ind_mask],f_u)).items():
                self.f_u_cache[u_ind]=f_u_
            for (v_ind,f_v_) in dict(zip(v_inds[v_ind_mask],f_v)).items():
                self.f_v_cache[v_ind]=f_v_
            f_u=torch.stack([self.f_u_cache[u_ind] for u_ind in u_inds])
            f_v=torch.stack([self.f_v_cache[v_ind] for v_ind in v_inds])

        f_u=f_u.view(B,1,self.latent_dim)
        f_v=f_v.view(B,self.latent_dim,1)
        out=torch.bmm(f_u,f_v)
        out=out.view(B,)
        loss=F.mse_loss(out,y)

        # pdb.set_trace()
        return out, loss

train_interact_path = "data/citeulike/dropoutnet_data/cold/train.csv"
test_interact_path = "data/citeulike/dropoutnet_data/cold/test.csv"
user_path="data/citeulike/dropoutnet_data/trained/cold/WRMF_cold_rank200_reg1_alpha10_iter10.U.txt"
item_path="data/citeulike/dropoutnet_data/trained/cold/WRMF_cold_rank200_reg1_alpha10_iter10.V.txt"

user_vectors = np.loadtxt(user_path)
user_vectors = user_vectors[1:, :]
item_vectors = np.loadtxt(item_path)
item_vectors = item_vectors[1:, :]

num_users = user_vectors.shape[0]
num_items = item_vectors.shape[0]

def read_iteraction_data(data_path):
    pref_matrix = np.zeros((num_users, num_items), dtype=np.int)
    user_ids = []
    item_ids = []
    for line in open(data_path):
        arr = line.strip().split(",")
        user_id = int(arr[0]) - 1
        item_id = int(arr[1]) - 1
        user_ids.append(user_id)
        item_ids.append(item_id)
        pref_matrix[user_id, item_id] = 1
    user_ids = sorted(list(set(user_ids)))
    item_ids = sorted(list(set(item_ids)))
    return user_ids, item_ids, pref_matrix

train_user_ids, train_item_ids, train_pref_matrix = read_iteraction_data(train_interact_path)
val_user_ids, val_item_ids, val_pref_matrix = read_iteraction_data(test_interact_path)
train_pref_matrix=train_pref_matrix[:,train_item_ids]
val_pref_matrix=val_pref_matrix[:,val_item_ids]


citeulike_data=pd.read_csv(train_interact_path,names=['user','item'],index_col=False)
citeulike_val_data=pd.read_csv(test_interact_path,names=['user','item'],index_col=False)


#@title Load cache
import json
VAR_NAMES=['u_dict','v_dict','val_v_dict','u_transforms','u_feats_svd_avg_std','v_feats_svd_std','val_v_feats_svd_std']
for j in VAR_NAMES:
    with open(EMBEDDING_PATH+j+".json") as f:
        dic=json.load(f)
        locals()[j]={int(float(k)):np.array(dic[k]) for k in dic}

u_feats,v_feats,val_v_feats=u_feats_svd_avg_std,v_feats_svd_std,val_v_feats_svd_std

print("LOADED CACHE")

LABELS_MEAN=0.007811738387556351
LABELS_STD=0.06936111446816964
#ensure this is the correct u_dict, v_dict
assert round(LABELS_MEAN,4)==round(np.dot(np.array(list(u_dict.values())),np.array(list(v_dict.values())).T).mean(),4)

# assert len(v_dict)==8000

#@title CiteULikePosOnly


#@title CiteULikeNegSample

import random
import pdb


class UserAnimePermuteID(Dataset):
    def __init__(self,u_dict,v_dict,u_feats,v_feats,n_scores_user=25,pos_neg_ratio=5,user_transform_p=0.5):
        self.n_scores_user=n_scores_user
        self.V_dict=v_dict
        self.U_dict=u_dict
        self.V_feats=v_feats 
        self.U_feats=u_feats
        self.V=np.array(list(v_dict.values()))
        self.U=np.array(list(u_dict.values()))
        self.V_phi=np.array(list(v_feats.values()))
        self.U_phi=np.array(list(u_feats.values()))
        raw_labels=np.dot(self.U,self.V.T)#(num users,num items)
        # self.labels=(raw_labels- np.mean(raw_labels)) / np.std(raw_labels)
        self.labels=raw_labels
        self.num_users,self.num_items=self.labels.shape
        self.user_ids=list(map(int,u_dict.keys()))
        self.item_ids=list(map(int,v_dict.keys()))
        self.user_permute=np.random.permutation(self.num_users)

        neg_random=lambda num: np.random.permutation(self.item_ids)[:num]
        num_neg=int(n_scores_user*pos_neg_ratio/(pos_neg_ratio+1))
        leftover_pos=n_scores_user-num_neg
        pmatrix=train_pref_matrix if train_pref_matrix.shape[1]==len(self.V) else val_pref_matrix
        def pos_random(i):
            vals=np.array(self.item_ids)[np.argwhere(pmatrix[i]>0)[:,0]]
            if len(vals)>leftover_pos: return np.random.choice(vals,leftover_pos)
            elif len(vals): return np.random.choice(np.tile(vals,leftover_pos//len(vals)+1),leftover_pos)
            else: return neg_random(leftover_pos)
        self.item_permute=np.array([np.random.permutation(np.append(neg_random(num_neg),pos_random(i))) for i in range(len(self.user_ids))])
        self.inv_user_ids=dict(zip(self.user_ids,range(len(self.user_ids))))
        self.inv_item_ids=dict(zip(self.item_ids,range(len(self.item_ids))))
        self.user_transform_p=user_transform_p
        
    def by_id(self, u_id,v_id):
        u,v,u_phi,v_phi=self.U_dict[u_id],self.V_dict[v_id],self.U_feats[u_id],self.V_feats[v_id]
        y=self.labels[self.inv_user_ids[u_id]][self.inv_item_ids[v_id]]
        return (u,v,u_phi,v_phi)+(u_id,v_id,)+(y,)

    def by_element_idx(self,idx): 
        item=idx%self.num_items 
        user=(idx-item)//self.num_items
        u_id,v_id=self.user_ids[user],self.item_ids[item]
        return self.by_id(u_id,v_id)
    
    def __getitem__(self,idx):        
        item_idx=idx%self.n_scores_user        
        user_idx=(idx-item_idx)//self.n_scores_user
        user_idx=self.user_permute[user_idx]
        permuted_item_id=self.item_permute[user_idx][item_idx]
        return self.by_id(self.user_ids[user_idx],permuted_item_id)

    def __len__(self): 
      return self.num_users * self.n_scores_user

class UserAnimeID(Dataset):
    def __init__(self,u_dict,v_dict,u_feats,v_feats):
        self.V_dict=v_dict
        self.U_dict=u_dict
        self.V_feats=v_feats 
        self.U_feats=u_feats
        self.V=np.array(list(v_dict.values()))
        self.U=np.array(list(u_dict.values()))
        self.V_phi=np.array(list(v_feats.values()))
        self.U_phi=np.array(list(u_feats.values()))
        raw_labels=np.dot(self.U,self.V.T)#(num users,num items)
        # self.labels=(raw_labels- np.mean(raw_labels)) / np.std(raw_labels)
        self.labels=raw_labels
        self.num_users,self.num_items=self.labels.shape
        self.user_ids=list(map(int,u_dict.keys()))
        self.item_ids=list(map(int,v_dict.keys()))
        
    def __getitem__(self,idx): 
        item=idx%self.num_items 
        user=(idx-item)//self.num_items
        # u_id,v_id=self.user_item_pairs[idx]
        u_id,v_id=self.user_ids[user],self.item_ids[item]
        u,v,u_phi,v_phi=self.U_dict[u_id],self.V_dict[v_id],self.U_feats[u_id],self.V_feats[v_id]
        y=self.labels[user][item]
        return (u,v,u_phi,v_phi)+(u_id,v_id,)+(y,)

    def __len__(self): 
      return self.num_items * self.num_users


class UserAnimeCacheID(UserAnimeID):
    def __init__(self,u_dict,v_dict,u_feats,v_feats):
        super().__init__(u_dict,v_dict,u_feats,v_feats)
        self.perimeter_idxes=list(range(len(v_dict)))+(len(v_dict)*np.arange(1,len(u_dict))).tolist()
    def __getitem__(self, idx):
        return super().__getitem__(self.perimeter_idxes[idx])
    def __len__(self):
        return len(self.perimeter_idxes)



#@title Initialize model
import torch.optim as optim
from torch.optim.lr_scheduler import MultiplicativeLR,LambdaLR
from sklearn.model_selection import ParameterGrid as pg


class MyDataParallel(nn.DataParallel):
    def __getattr__(self, name):
        return getattr(self.module, name)

LABELS_MEAN=0.007811738387556351
LABELS_STD=0.06936111446816964
config={#printed to save the model
    "momentum":[MOMENTUM],
    "hidden_dims":[[500]],
    "latent_dim":[200],#FIX
    "anime_dim":[300],#FIX
    "user_drop_p":[0.5],
    "item_drop_p":[0.5],
    "activation":["tanh"],
    "n_score_users":[36],
    "pos_neg_ratio":[5],
    "mode":[mode],#to make lookup easier
    "neg_thresh":[float("inf")]
}

configs=pg(config)



def get_optimizer(dn):

    optimizer=optim.SGD([{'params': dn.parameters()},
                        ], lr=0.005/(LR_SCALE_FACTOR*NUM_ACCUMULATION_STEPS),momentum=MOMENTUM)
    return optimizer

#@title Learning rate adjust
def adjust_learning_rate(optimizer, epoch,rate=LR_DECAY_RATE):
    # initial_lr=0.005/(LR_SCALE_FACTOR*NUM_ACCUMULATION_STEPS)
    optimizer.param_groups[0]['lr']*=rate
    # print("New lr:",optimizer.param_groups[1]['lr'])
    

#@title Plot
from matplotlib import pyplot as plt

def plot_train(losses,val=False):
    plt.title("{} Loss".format("Validation" if val else "Training"))
    plt.xlabel("Epoch")
    plt.ylabel("Relevance Loss")
    plt.plot(losses)
    plt.show()

#@title Training 

from tqdm import tqdm 
def evaluate(epoch,dn,val_dload,preds=None,tru=None,eval=False):
    dn.eval()
    with torch.no_grad():
        eval_loss=0.0
        for (j,data) in tqdm(enumerate(val_dload,0)):

            u,v,u_phi,v_phi,u_ids,v_ids,y=data
            v=np.zeros_like(v)
            a,b,c,d=torch.tensor(u,dtype=torch.float),torch.tensor(v,dtype=torch.float),torch.tensor(u_phi,dtype=torch.float),torch.tensor(v_phi,dtype=torch.float)

            z=torch.tensor(y,dtype=torch.float)
            u_ids,v_ids=u_ids.numpy(),v_ids.numpy()
            a,b,c,d,z=a.to(device),b.to(device),c.to(device),d.to(device),z.to(device)
            r,loss=dn.forward(a,b,c,d,u_ids,v_ids,z,eval=eval)
            if preds!=None and tru!=None:
                preds.extend(r.cpu().numpy())
                tru.extend(y.cpu().numpy())
            loss=loss.mean()
            eval_loss+=loss.item()
            
        print('[%d] eval loss: %.5f' %(epoch + 1,  eval_loss / (j+1)))
        return eval_loss / (j+1)

def item_recall_at_M(M, R_hat_np, val_pref_matrix):
    ranking = np.argsort(-R_hat_np, axis=1)
    topM = ranking[:,:M]

    n = np.array([len(set(a) & set(np.nonzero(b)[0])) for a, b in zip(topM, val_pref_matrix)])
    d = np.sum(val_pref_matrix > 0, axis=1)
    
    return np.mean(n[d>0] / d[d>0])

def user_recall_at_M(M, R_hat_np, val_pref_matrix):
    ranking = np.argsort(-R_hat_np, axis=1)
    topM = ranking[:,:M]

    pref = val_pref_matrix

    n = np.array([np.count_nonzero(topM[pref[:,i] > 0] == i) for i in range(pref.shape[1])])
    d = np.sum(pref > 0, axis=0)
    
    return np.mean(n[d>0] / d[d>0])


def cold_metric(n_users,n_items,config=None,dn=None):
    assert min(n_users,n_items)==0

    cache_uaid=UserAnimeCacheID(u_dict,val_v_dict,u_feats,val_v_feats)
    # sliced_uaid=SlicedUserAnimeID(u_dict,v_dict,u_feats,v_feats,slice_users=n_users,slice_items=n_items)
    dload=DataLoader(cache_uaid,batch_size=BATCH_SIZE,num_workers=NUM_WORKERS)
    preds,tru=[],[]
    if not dn:
        assert config
        dn=DropoutNet(**config)
        dn.load_state_dict(torch.load(PATH,map_location=device))
        dn=dn.to(device)
    
    evaluate(0,dn,dload,eval=True)
    print("CACHED")
    preds,tru=[],[]
    U_hat=torch.stack([dn.f_u_cache[k] for k in u_dict])
    V_hat=torch.stack([dn.f_v_cache[k] for k in val_v_dict])
    R_hat=U_hat.matmul(V_hat.T)
    R_hat_np=R_hat.cpu().numpy()
    ir=item_recall_at_M(100, R_hat_np, val_pref_matrix)
    ur=user_recall_at_M(100, R_hat_np, val_pref_matrix)
    dn.f_u_cache={}
    dn.f_v_cache={}
    return (ir,ur)




from multiprocessing import Pool

def train(dn,optimizer,num_epochs=100,cont=-1,num_accumulation_steps=NUM_ACCUMULATION_STEPS,save_every=1,metric_every=500*NUM_ACCUMULATION_STEPS,save_path=""):
    

    ### PICK UP WHERE IT LEFT OFF
    
    best_metric=float("-inf")
    preds=[]
    if os.path.isfile("{}_{}.pt".format(save_path,num_epochs-1)): 
        print("save_path","{}_{}.pt".format(save_path,num_epochs-1),"finished")
        return
    else:
        files=os.listdir(os.path.dirname(save_path))
        print(save_path)
        chkpts=[os.path.isfile("{}_{}.pt".format(save_path,save_every*i+save_every-1)) for i in range(num_epochs//save_every)]
        indmax=len(chkpts)-1-np.argmax(chkpts[::-1])
        if chkpts[indmax]:

            latest_ckpt="{}_{}.pt".format(save_path,save_every*indmax+save_every-1)
            cont=save_every*indmax-1+save_every
            print("latest ckpt",latest_ckpt)
            dn.load_state_dict(torch.load(latest_ckpt,map_location=device))
            print("continuing at",cont+1,"epoch")
        else:
            cont=-1
            print("training for",save_path)


    if os.path.isfile("{}_metrics.txt".format(save_path)):
        print("Exists!")
        raise AssertionError

    for epoch in range(cont+1,num_epochs):
        # uaid=CiteULikeNegSample(citeulike_data,u_dict,v_dict,u_feats,v_feats,neg_thresh=dn.neg_thresh,pos_neg_ratio=dn.pos_neg_ratio)
        uaid=UserAnimePermuteID(u_dict,v_dict,u_feats,v_feats,n_scores_user=dn.n_score_users,pos_neg_ratio=dn.pos_neg_ratio)
        dload=DataLoader(uaid,batch_size=BATCH_SIZE,num_workers=NUM_WORKERS)
        # val_uaid=CiteULikeNegSample(citeulike_val_data,u_dict,val_v_dict,u_feats,val_v_feats)
        val_uaid=UserAnimePermuteID(u_dict,val_v_dict,u_feats,val_v_feats,dn.n_score_users,pos_neg_ratio=dn.pos_neg_ratio)
        val_dload=DataLoader(val_uaid,batch_size=BATCH_SIZE,num_workers=NUM_WORKERS)
        dn.train(True)
        # data_iter=iter(dload) 
        epoch_loss=0.0

            
        for (i,data) in tqdm(enumerate(dload,0)):

            if i%metric_every==0:
                if i: adjust_learning_rate(optimizer, epoch)
                metrics=cold_metric(0,len(val_v_dict),dn=dn)
                with open("{}_metrics.txt".format(save_path),"a+") as f:                    
                    f.write("{},{}\n".format(*metrics))     
                    print("Save path:",save_path)                               
                    print("Metrics:",metrics)
                    best_metric=max(best_metric,metrics[0])
                    print("Best:",best_metric)

                # torch.save(dn.state_dict(),"{}_{}.pt".format(save_path,epoch))#to be in sync with latest in _metrics.txt
                dn.train(True)
                torch.cuda.empty_cache()
                
                if len(open("{}_metrics.txt".format(save_path),"r").readlines())==80: return
            
            u,v,u_phi,v_phi,u_ids,v_ids,y=data
            
            a,b,c,d=torch.tensor(u,dtype=torch.float),torch.tensor(v,dtype=torch.float),torch.tensor(u_phi,dtype=torch.float),torch.tensor(v_phi,dtype=torch.float)

            z=torch.tensor(y,dtype=torch.float)
            u_ids,v_ids=u_ids.numpy(),v_ids.numpy()
            a,b,c,d,z=a.to(device),b.to(device),c.to(device),d.to(device),z.to(device)
            r,loss=dn.forward(a,b,c,d,u_ids,v_ids,z)

            
            # with open("{}_batches.txt".format(save_path,epoch),"a+") as f:
            #     f.write("{}\n".format(loss.item()))
            
            loss.backward()
            
            if i%num_accumulation_steps==num_accumulation_steps-1:
                optimizer.step()
                optimizer.zero_grad()
                torch.cuda.empty_cache()

            epoch_loss+=loss.item()
            
        print('[%d] loss: %.5f' % (epoch + 1, epoch_loss / (i+1)))
        eval_loss=evaluate(epoch,dn,val_dload,preds)
        yield preds,epoch_loss/(i+1),eval_loss

        ###SAVE LATEST EPOCHS, BUT TFIDF TRAINS TOO FAST FOR IT TO SAVE EVERY LOSS
        ###SO JUST IGNORE FOR TFIDF, REMEMBER TO SAVE PLOTS
        # with open("{}.txt".format(save_path,epoch),"a+") as f:
        #     f.write("{},{},{}\n".format(epoch,epoch_loss/(i+1),eval_loss))

        
    

    
def run_experiment(dn,optimizer,num_epochs=100,plot_every=10,save_path=""):
    preds=None;epoch_losses=[];eval_losses=[]
    np.random.seed(0)
    random.seed(0)
  

    for _ in range(num_epochs):
        
        for (preds,t_l,v_l) in train(dn,optimizer,num_epochs,save_path=save_path):
            preds=preds
            epoch_losses.append(t_l)
            eval_losses.append(v_l)
            if len(epoch_losses)%plot_every==1:
                plot_train(epoch_losses)
            if len(epoch_losses)%plot_every==2:
                plot_train(eval_losses,True)

def checkpoint_name_from_config(path,config):
    #USAGE: path="models/tfidf_with_recs/"
    out=""
    for (k,v) in config.items():
        out+="{}={}__".format(k,v)
    out=out.rstrip("__")+".pt"
    return os.path.join(path,out)


###RUN EXPERIMENTS OVER ALL HPARAM CONFIGS
def run_experiments(configs,path="models/citeulike/bert/recs"):
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    for config in configs:
        save_path=checkpoint_name_from_config(path,config)
        os.makedirs(path,exist_ok=True)
        # SO COLAB PICKS UP WHERE IT LEFT OFF
        
        dn=DropoutNet(**config)
        # dn=nn.DataParallel(dn)
        dn=dn.to(device)
        optimizer=get_optimizer(dn)
        
        
        run_experiment(dn,optimizer,NUM_EPOCHS,plot_every=3,save_path=save_path)

run_experiments(configs,"models/citeulike/uphi/svd_batching/{}".format(mode))
