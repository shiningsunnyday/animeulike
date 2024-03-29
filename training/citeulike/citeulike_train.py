# -*- coding: utf-8 -*-
"""CiteULike - Train.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/13EaxT_gTXtf_JdZveoqGAisWAvtJBTnh
"""

import pandas as pd
from torch.utils.data import Dataset
import os
import numpy as np
from abc import abstractmethod
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from typing import List
import torch
from torch.nn import functional as F

import torch.nn as nn
import itertools
from torch.utils.data import DataLoader

#@title Rec and TFIDF Dataset

from collections import OrderedDict as od, defaultdict as dd
class RecommendationDataset(Dataset):
    def __init__(self, path):
        self.path=path

        #pre-processing
        self.data = pd.read_csv(self.path, encoding = "ISO-8859-1").loc[:,"raw.title":"raw.abstract"]
        self.text_inds=["raw.title","raw.abstract"]


    def __len__(self):
        return len(self.data)


    def __getitem__(self, idx):
        id_1=int(self.rc_data["show1"][idx])
        id_2=int(self.rc_data["show2"][idx])
        data_1=self.data.iloc[self.index_map[id_1]].values
        data_2=self.data.iloc[self.index_map[id_2]].values
        return np.concatenate((data_1,data_2))


from functools import reduce

class TFIDF(RecommendationDataset):
    def __init__(self,path,max_features=2000,mode="train",featurizer=None):
        self.path=path

        #pre-processing
        self.data = pd.read_csv(self.path, encoding = "ISO-8859-1").loc[:,"raw.title":"raw.abstract"]
        self.text_inds=["raw.title","raw.abstract"]
        #featurizer={"fzer":TfidfFeaturizer,"scaler":MinMaxScaler}
        assert mode=="train" or featurizer 
        if featurizer:
            self.fzer=featurizer["fzer"]
        else:
            self.tf_config={
                'strip_accents':'ascii',
                'stop_words':'english',
                'max_features':max_features
            }
            self.dic=self.data.loc[:,self.text_inds]
            self.fzer=self.fit_text(TFIDF.get_text(self.dic))

    def top_words(self):
        return self.fzer.vocabulary_

    @staticmethod
    def get_text(dic,text_inds=["raw.title","raw.abstract"]):
        args=[dic[key].values for key in text_inds]
        text=[reduce(lambda cum,cur:str(cum)+str(cur),x) for x in zip(*args)]
        return text

    def __len__(self):
        return len(self.data)

    def fit_text(self,text:List[str]):
        fzer=TfidfVectorizer(**self.tf_config)
        fzer.fit(text)
        return fzer
    


    def featurize_article(self,item):
        item_str=reduce(lambda x,y:x+y,[str(item[text_ind]) for text_ind in self.text_inds])
        feats=self.featurize([item_str])
        return feats[0].astype(float)
    
    def featurize(self, text: List[str]):
        #assume fzer already transformed on train
        return self.fzer.transform(text)
 
    def get_article(self, idx):
        item=self.data.iloc[idx]
        return self.featurize_article(item)


#@title Initialize data
train_path="data/citeulike/article_data_train.csv"
val_path="data/citeulike/article_data_val.csv"
test_path="data/citeulike/article_data_test.csv"
articles=TFIDF(train_path)
#@title DropoutNet




class DropoutNet(nn.Module):
    def __init__(self, **kwargs):
        super().__init__()
        assert {"item_drop_p","user_drop_p","latent_dim","hidden_dim"}.issubset(set(kwargs.keys()))

        for (k,v) in kwargs.items():
            setattr(self,k,v)
        self.dim=self.latent_dim
        self.V_dict=v_dict
        self.U_dict=u_dict
        # self.item_drop_p=1.0
        # self.user_drop_p=1.0
        self.item_drop=nn.Dropout(self.item_drop_p)
        self.user_drop=nn.Dropout(self.user_drop_p)
        #LAYERS
        self.linear_u=nn.Linear(self.dim,self.hidden_dim)
        self.linear_v=nn.Linear(self.dim,self.hidden_dim)
        self.linear_phi_u=nn.Linear(self.anime_dim,self.hidden_dim)
        self.linear_phi_v=nn.Linear(self.anime_dim,self.hidden_dim)
        self.non_linearity={"relu":nn.ReLU(),"sigmoid":nn.Sigmoid(),"tanh":nn.Tanh(),"identity":nn.Identity()}[self.activation]
        self.f_u=nn.Linear(2*self.hidden_dim,self.dim)
        self.f_v=nn.Linear(2*self.hidden_dim,self.dim)


    def forward(self,u,v,u_phi,v_phi,y):
        #note we're using ids, not indices
        B=u.shape[0]
        v=self.item_drop(v) #(B,h) 
        u=self.user_drop(u)

        

        u=self.linear_u(u) #(B,h)
        v=self.linear_v(v) #(B,h)
        phi_u=self.linear_phi_u(u_phi) #(B,h) 
        phi_v=self.linear_phi_v(v_phi) #(B,h)
        u=self.non_linearity(u)
        v=self.non_linearity(v)
        phi_u=self.non_linearity(phi_u)
        phi_v=self.non_linearity(phi_v)
        f_u=torch.cat((u,phi_u),axis=1)
        f_v=torch.cat((v,phi_v),axis=1)
        f_u=self.f_u(f_u)#(B,dim)
        f_v=self.f_v(f_v)#(B,dim)
        f_u=self.non_linearity(f_u)
        f_v=self.non_linearity(f_v)
        f_u=f_u.view(B,1,self.dim)
        f_v=f_v.view(B,self.dim,1)
        out=torch.bmm(f_u,f_v)
        # out=self.sigmoid(out)#(B,1,1)
        out=out.view(B,)
        loss=F.mse_loss(out,y)
        return out, loss

#@title Load feats

train_interact_path = "citeulike/dropoutnet_data/cold/train.csv"
test_interact_path = "citeulike/dropoutnet_data/cold/test.csv"
test_ids_path = "citeulike/dropoutnet_data/cold/test_item_ids.csv"
user_path="citeulike/dropoutnet_data/trained/cold/WRMF_cold_rank200_reg1_alpha10_iter10.U.txt"
item_path="citeulike/dropoutnet_data/trained/cold/WRMF_cold_rank200_reg1_alpha10_iter10.V.txt"

user_vectors = np.loadtxt(user_path)
user_vectors = user_vectors[1:, :]
item_vectors = np.loadtxt(item_path)
item_vectors = item_vectors[1:, :]

num_users = user_vectors.shape[0]
num_items = item_vectors.shape[0]
user_df = user_vectors
item_df = item_vectors

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

train_pref_mask=train_pref_matrix>0.0
val_pref_mask=val_pref_matrix>0.0



#redundant
all_item_ids = range(num_items)
train_item_ids = sorted(list(set(all_item_ids) - set(val_item_ids)))

u_dict=dict(zip(train_user_ids,user_vectors[train_user_ids]))#{user_ind:item_vec}
v_dict=dict(zip(train_item_ids,item_vectors[train_item_ids]))#{anime_ind:item_vec}

citeulike_data=pd.read_csv(train_interact_path,names=['user','item'],index_col=False)
citeulike_val_data=pd.read_csv(test_interact_path,names=['user','item'],index_col=False)



val_item_df=pd.read_csv(val_path)
all_v_feats=np.array([self.get_article(i) for i in range(articles.__len__())])

v_feats=dict(zip(train_item_ids,all_v_feats[train_item_ids]))
all_u_transforms=[np.average(item_vectors[pref_mask.iloc[i].values],axis=0) for i in range(len(user_df))]
u_transforms=dict(zip(user_ids,all_u_transforms))

all_u_feats=[np.average(all_v_feats[pref_mask.iloc[i].values],axis=0) for i in range(len(user_df))]
u_feats=dict(zip(user_ids,all_u_feats))

all_val_v_feats=np.array([rec.featurize_anime(val_item_df.iloc[i]) for i in range(len(val_item_df))])
val_v_feats=dict(zip(val_ids,all_val_v_feats))
# compute val_v_dict

u_indexers=[np.arange(len(user_df))[mask] for mask in val_pref_mask.T.values]
indexer_avg=np.array([np.average(user_vectors.iloc[u_index,:],axis=0) for u_index in u_indexers])
val_v_dict=dict(zip(val_ids,indexer_avg))

#@title Standardize variables

import scipy
from scipy import stats
for var_name in ['u_dict','v_dict','u_feats','v_feats','u_transforms','val_v_dict','val_v_feats']:
    try:
        dic=locals()[var_name]
    except KeyError:
        print("no",var_name)
    std_dic={k:np.nan_to_num(stats.zscore(dic[k].tolist())) for k in dic}
    locals()[var_name]=std_dic
    print("standardized",var_name)

#@title Save cache
import json 

VAR_NAMES=['u_dict','v_dict','val_v_dict']

def save(vars=[],path="cached/citeulike/"):
    #make sure VAR_NAMES include ['u_dict','v_dict','u_feats','v_feats','u_transforms','val_v_dict','val_v_feats']
    for j in vars:
        try:
            dic=globals()[j]
            with open(path+j+'.json','w') as f:
                dic={k:dic[k].tolist() for k in dic}
                json.dump(dic,f)
        except KeyError:
            print("no",j)

save(VAR_NAMES)

#@title Load cache
import json
path="cached/citeulike/"
VAR_NAMES=['u_dict','v_dict','val_v_dict']
for j in VAR_NAMES:
    with open(path+j+".json") as f:
        dic=json.load(f)
        locals()[j]={int(float(k)):np.array(dic[k]) for k in dic}

# assert len(v_dict)==8000

#@title UserAnimeID


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
        self.labels=np.dot(self.U,self.V.T)#(num users,num items)
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
        return (u,v,u_phi,v_phi), y

    def __len__(self): 
      return self.num_items * self.num_users

# uaid=UserAnimeID(u_dict,v_dict,u_feats,v_feats)
# val_uaid=UserAnimeID(u_dict,val_v_dict,u_feats,val_v_feats)

#@title CiteULikePosOnly

class CiteULikePosOnly(Dataset):
    def __init__(self,data,u_dict,v_dict,u_feats,v_feats):
        self.data=data
        self.V_dict=v_dict
        self.U_dict=u_dict
        self.V_feats=v_feats 
        self.U_feats=u_feats
        self.V=np.array(list(v_dict.values()))
        self.U=np.array(list(u_dict.values()))
        self.V_phi=np.array(list(v_feats.values()))
        self.U_phi=np.array(list(u_feats.values()))
        self.labels=np.dot(self.U,self.V.T)#(num users,num items)
        self.num_users,self.num_items=self.labels.shape
    
    def __getitem__(self,idx): 
        user,item=self.data.iloc[idx].values-1
        u_id,v_id=user,item
        u,v,u_phi,v_phi=self.U_dict[u_id],self.V_dict[v_id],self.U_feats[u_id],self.V_feats[v_id]
        y=self.labels[user][item]
        return (u,v,u_phi,v_phi), y

    def __len__(self): 
        return len(self.data)

#@title CiteULikeNegSample

import random
import pdb
class CiteULikeNegSample(CiteULikePosOnly):
    def __init__(self,data,u_dict,v_dict,u_feats,v_feats,neg_thresh=-0.1,pos_neg_ratio=1.0,row_major=True):
        
        super().__init__(data,u_dict,v_dict,u_feats,v_feats)
        
        neg_mask=self.labels.reshape((-1,))<neg_thresh
        print("Neg:",np.sum(neg_mask))
        self.neg_inds=np.arange(len(neg_mask))[neg_mask]
        num_neg=int(len(self.data)*pos_neg_ratio)
        self.sampled_neg_inds=np.random.choice(self.neg_inds,(num_neg,),replace=False)

        self.row_major=row_major
        self.major_len=self.num_users if row_major else self.num_items
        self.minor_len=self.num_items if row_major else self.num_users
        

    def getitem(self,idx):
        #this first exhausts pos samples from super().__getitem__() before 
        #going to negative
        if idx<len(self.data):
            return super().__getitem__(idx)
        else:
            neg_idx=self.self.sampled_neg_inds[idx-len(self.data)]
            idx=self.neg_inds[neg_idx]
            major_ind=idx%self.major_len
            minor_ind=random.randrange(self.minor_len)
            inds=[minor_ind,major_ind]
            if self.row_major: inds=inds[::-1]
            user,item=inds
            u_id,v_id=self.user_ids[user],self.item_ids[item]
            u,v,u_phi,v_phi=self.U_dict[u_id],self.V_dict[v_id],self.U_feats[u_id],self.V_feats[v_id]
            y=self.labels[user][item]
            return (u,v,u_phi,v_phi), y
            
      
    def __len__(self): 
        return len(self.sampled_neg_inds)+len(self.data)

    

uaid=CiteULikeNegSample(citeulike_data,u_dict,v_dict,u_feats,v_feats)
val_uaid=CiteULikeNegSample(citeulike_val_data,u_dict,val_v_dict,u_feats,val_v_feats)
val_uaid.__len__()

import matplotlib.pyplot as plt

uaid_=CiteULikePosOnly(citeulike_data,u_dict,val_v_dict,u_feats,val_v_feats)
labels_=uaid_.labels.reshape((-1,))
mask=np.random.choice(np.arange(len(labels_)),size=(10000,),replace=False)
plt.hist(labels_[mask],bins=100)

#@title Initialize model
import torch.optim as optim
from torch.optim.lr_scheduler import MultiplicativeLR,LambdaLR
from sklearn.model_selection import ParameterGrid as pg

#ITERATE HPARAMS
config={
    "hidden_dim":[100],
    "latent_dim":[10],#FIX
    "anime_dim":[2006],#FIX
    "item_drop_p":[0],
    "user_drop_p":[0],
    "activation":['identity']
}
configs=pg(config)
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")



def evaluate(epoch,dn,val_dload,preds=None):
    dn.eval()
    with torch.no_grad():
        eval_loss=0.0
        for (j,data) in enumerate(val_dload,0):
            x,y=data 
            u,v,u_phi,v_phi=x
            v=np.zeros_like(v)
            a,b,c,d=torch.tensor(u,dtype=torch.float),torch.tensor(v,dtype=torch.float),torch.tensor(u_phi,dtype=torch.float),torch.tensor(v_phi,dtype=torch.float)
            z=torch.tensor(y,dtype=torch.float)
            a,b,c,d,z=a.to(device),b.to(device),c.to(device),d.to(device),z.to(device)
            r,loss=dn.forward(a,b,c,d,z)
            loss=loss.mean()
            eval_loss+=loss.item()
            if epoch % 10 == 9:
                preds.extend(r.cpu().numpy())
        print('[%d] eval loss: %.5f' %(epoch + 1,  eval_loss / (j+1)))
        return eval_loss / (j+1)
            
def train(dn,optimizer,val_dload,num_epochs=100,cont=-1,num_accumulation_steps=8,save_every=10,save_path=""):
    

    ### PICK UP WHERE IT LEFT OFF
    
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

            latest_ckpt="{}_{}.pt".format(save_path,save_every*indmax-1)
            cont=save_every*indmax-1
            print("latest ckpt",latest_ckpt)
            dn.load_state_dict(torch.load(latest_ckpt,map_location=device))
            print("continuing at",cont+1,"epoch")
        else:
            cont=-1
            print("training for",save_path)



    for epoch in range(cont+1,num_epochs):
        uaid=UserAnimeIDRandomAccess(u_dict,v_dict,u_feats,v_feats,sample_mask=sample_dic)
        dload=DataLoader(uaid,batch_size=4,shuffle=True,num_workers=2)
        dn.train(True)
        # data_iter=iter(dload) 
        epoch_loss=0.0
        if epoch >= 1:
            adjust_learning_rate(optimizer, epoch,rate=0.99)
        for (i,data) in enumerate(dload,0):
            u, v, u_input_ids, u_attention_mask, num_shows, v_input_ids, v_attention_mask, y = data

            u, v = torch.tensor(u,dtype=torch.float).to(device), torch.tensor(v,dtype=torch.float).to(device)
            u_input_ids, u_attention_mask, num_shows = u_input_ids.to(device), u_attention_mask.to(device), num_shows.to(device)
            v_input_ids, v_attention_mask = v_input_ids.to(device), v_attention_mask.to(device)
            y = torch.tensor(y,dtype=torch.float).to(device)

            r,loss=dn(u, v, u_input_ids, u_attention_mask, num_shows, v_input_ids, v_attention_mask, y)

            
            loss=loss.mean()
            s1=list(dn.parameters())[0].clone()

            loss.backward()
            
            if i%num_accumulation_steps==num_accumulation_steps-1:
                optimizer.step()
                optimizer.zero_grad()

            
            s2=list(dn.parameters())[0].clone()
            # assert i or (not torch.equal(s1.data,s2.data)) # only checks for i=0
            
            epoch_loss+=loss.item()
            torch.cuda.empty_cache()
        print('[%d] loss: %.5f' % (epoch + 1, epoch_loss / (i+1)))
        eval_loss=evaluate(epoch,dn,val_dload,preds)
        yield preds,epoch_loss/(i+1),eval_loss

        ###SAVE LATEST EPOCHS, BUT TFIDF TRAINS TOO FAST FOR IT TO SAVE EVERY LOSS
        ###SO JUST IGNORE FOR TFIDF, REMEMBER TO SAVE PLOTS
        with open("{}.txt".format(save_path,epoch),"a+") as f:
            f.write("{},{},{}\n".format(epoch,epoch_loss/(i+1),eval_loss))

        if epoch%save_every==save_every-1:
            torch.save(dn.state_dict(),"{}_{}.pt".format(save_path,epoch))
    

    
def run_experiment(dn,optimizer,uaid,val_uaid,num_epochs=100,plot_every=10,save_path=""):
    preds=None;epoch_losses=[];eval_losses=[]
    np.random.seed(0)
    random.seed(0)
  
    val_dload=DataLoader(val_uaid,batch_size=4,num_workers=2)
    for _ in range(num_epochs):
        
        for (preds,t_l,v_l) in train(dn,optimizer,val_dload,num_epochs,save_path=save_path):
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
        if config["item_drop_p"]!=config["user_drop_p"]: continue
        save_path=checkpoint_name_from_config(path,config)
        os.makedirs(path,exist_ok=True)
        # SO COLAB PICKS UP WHERE IT LEFT OFF
        
        dn=DropoutTransformerNet(**config)
        dn=dn.to(device)
        optimizer=get_optimizer(dn)
        
        
        run_experiment(dn,optimizer,uaid,val_uaid,250,plot_every=3,save_path=save_path)

run_experiments(configs,"models/recsys/tfidf")
