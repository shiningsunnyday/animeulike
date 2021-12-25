import matplotlib.pyplot as plt 

import numpy as np 

import os
print(os.getcwd())

base="anime/anime_warm_fold/"
NAMES=[base+x for x in [
"activation=tanh__anime_dim=300__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=0.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__mode=tfidf__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_drop_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=300__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=0.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__mode=tfidf__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_transform_p=0.0.pt_metrics.txt",
"activation=tanh__anime_dim=300__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=0.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__mode=tfidf__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_transform_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=300__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=0.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__mode=tfidf__n_score_users=36__neg_thresh=inf__num_gnn_feats=32__pos_neg_ratio=5__user_transform_p=0.0.pt_metrics.txt",
"activation=tanh__anime_dim=300__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=0.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__mode=tfidf__n_score_users=36__neg_thresh=inf__num_gnn_feats=32__pos_neg_ratio=5__user_transform_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=300__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=1.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__mode=tfidf__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_drop_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=300__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=1.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__mode=tfidf__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_transform_p=0.0.pt_metrics.txt",
"activation=tanh__anime_dim=300__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=1.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__mode=tfidf__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_transform_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=300__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=1.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__mode=tfidf__n_score_users=36__neg_thresh=inf__num_gnn_feats=32__pos_neg_ratio=5__user_transform_p=0.0.pt_metrics.txt",
"activation=tanh__anime_dim=300__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=1.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__mode=tfidf__n_score_users=36__neg_thresh=inf__num_gnn_feats=32__pos_neg_ratio=5__user_transform_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=300__data_mode=('tf-idf', 'tf-idf')__eip=1.0__eup=0.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__mode=tfidf__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_drop_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=300__data_mode=('tf-idf', 'tf-idf')__eip=1.0__eup=0.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__mode=tfidf__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_transform_p=0.0.pt_metrics.txt",
"activation=tanh__anime_dim=300__data_mode=('tf-idf', 'tf-idf')__eip=1.0__eup=0.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__mode=tfidf__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_transform_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=300__data_mode=('tf-idf', 'tf-idf')__eip=1.0__eup=0.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__mode=tfidf__n_score_users=36__neg_thresh=inf__num_gnn_feats=32__pos_neg_ratio=5__user_transform_p=0.0.pt_metrics.txt",
"activation=tanh__anime_dim=300__data_mode=('tf-idf', 'tf-idf')__eip=1.0__eup=0.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__mode=tfidf__n_score_users=36__neg_thresh=inf__num_gnn_feats=32__pos_neg_ratio=5__user_transform_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=300__data_mode=('tf-idf', 'tf-idf')__eip=1.0__eup=1.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__mode=tfidf__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_drop_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=300__data_mode=('tf-idf', 'tf-idf')__eip=1.0__eup=1.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__mode=tfidf__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_transform_p=0.0.pt_metrics.txt",
"activation=tanh__anime_dim=300__data_mode=('tf-idf', 'tf-idf')__eip=1.0__eup=1.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__mode=tfidf__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_transform_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=300__data_mode=('tf-idf', 'tf-idf')__eip=1.0__eup=1.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__mode=tfidf__n_score_users=36__neg_thresh=inf__num_gnn_feats=32__pos_neg_ratio=5__user_transform_p=0.0.pt_metrics.txt",
"activation=tanh__anime_dim=300__data_mode=('tf-idf', 'tf-idf')__eip=1.0__eup=1.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__mode=tfidf__n_score_users=36__neg_thresh=inf__num_gnn_feats=32__pos_neg_ratio=5__user_transform_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=0.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_drop_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=0.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_transform_p=0.0.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=0.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_transform_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=0.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=32__pos_neg_ratio=5__user_drop_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=0.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=32__pos_neg_ratio=5__user_transform_p=0.0.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=0.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=32__pos_neg_ratio=5__user_transform_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=0.5__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_transform_p=0.0.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=0.5__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_transform_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=0.5__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=32__pos_neg_ratio=5__user_transform_p=0.0.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=0.5__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=32__pos_neg_ratio=5__user_transform_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=1.0__hidden_dims=[500]__item_corrupt_p=0.1__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_drop_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=1.0__hidden_dims=[500]__item_corrupt_p=0.3__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_drop_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=1.0__hidden_dims=[500]__item_corrupt_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_drop_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=1.0__hidden_dims=[500]__item_corrupt_p=0.7__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_drop_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=1.0__hidden_dims=[500]__item_corrupt_p=0.9__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_drop_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=1.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_drop_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=1.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_transform_p=0.0.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=1.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_transform_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=1.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=32__pos_neg_ratio=5__user_drop_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=1.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=32__pos_neg_ratio=5__user_transform_p=0.0.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=0.0__eup=1.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=32__pos_neg_ratio=5__user_transform_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=0.5__eup=0.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_transform_p=0.0.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=0.5__eup=0.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=32__pos_neg_ratio=5__user_transform_p=0.0.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=0.5__eup=0.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=32__pos_neg_ratio=5__user_transform_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=1.0__eup=0.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_drop_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=1.0__eup=0.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_transform_p=0.0.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=1.0__eup=0.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_transform_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=1.0__eup=0.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=32__pos_neg_ratio=5__user_drop_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=1.0__eup=0.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=32__pos_neg_ratio=5__user_transform_p=0.0.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=1.0__eup=0.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=32__pos_neg_ratio=5__user_transform_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=1.0__eup=1.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_drop_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=1.0__eup=1.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_transform_p=0.0.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=1.0__eup=1.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=0__pos_neg_ratio=5__user_transform_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=1.0__eup=1.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=32__pos_neg_ratio=5__user_drop_p=0.5.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=1.0__eup=1.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=32__pos_neg_ratio=5__user_transform_p=0.0.pt_metrics.txt",
"activation=tanh__anime_dim=774__data_mode=('tf-idf', 'tf-idf')__eip=1.0__eup=1.0__hidden_dims=[500]__item_drop_p=0.5__latent_dim=200__n_score_users=36__neg_thresh=inf__num_gnn_feats=32__pos_neg_ratio=5__user_transform_p=0.5.pt_metrics.txt",
]]

from itertools import cycle
cycol = cycle('bgrcmk')

thousands=4000
metric_every=500
FINISHED=True


scale_factor=100*metric_every/1000
num_iters=thousands*1000//(metric_every*100)
from matplotlib.markers import MarkerStyle

COLORS=[next(cycol) for i in range(len(NAMES))]
OUT_NAME=NAMES[0].replace(".txt",".png")
datas=[np.loadtxt("metrics/{}".format(NAME),dtype=str) for NAME in NAMES if len(NAME)]
urs=[[float(x.split(',')[0]) for x in data] for data in datas]
xs=np.arange(max([len(ur) for ur in urs]))*scale_factor
irs=[[float(x.split(',')[1]) for x in data] for data in datas]
xs,urs,irs=xs[:num_iters],[ur[:num_iters] for ur in urs],[ir[:num_iters] for ir in irs]

bests=[]

def get_name(x):
    x=x.rstrip(".pt_metrics.txt")
    kwargs_dic=list(map(lambda y:[y.split("=")[0],y.split("=")[1]],x.split("__")))
    kwargs=np.array(kwargs_dic)
    kwargs_dic=dict(zip(kwargs[:,0],kwargs[:,1]))
    typ="nani" if "user_drop_p" in kwargs_dic else "dn"
    eup=int(float(kwargs_dic["eup"]))
    inout=("IN" if eup else "OUT") if typ=="nani" else ("OUT" if eup else "IN")
    gnn="G" if int(float(kwargs_dic["num_gnn_feats"])) else "nG"
    cool="" if int(float(kwargs_dic["eip"])) else " (cool)"
    ut=" (ut)" if "user_transform_p" in kwargs and float(kwargs_dic["user_transform_p"]) else ""
    data_mode=kwargs_dic['data_mode'] if gnn else ""
    corrupt=" corrupt: "+kwargs_dic['item_corrupt_p'] if 'item_corrupt_p' in kwargs else ""
    mode=kwargs_dic["mode"]+ " " if "mode" in kwargs_dic else ""
    return "{}{}{} {}{} {}{}{}".format(mode,typ,ut,gnn,data_mode,inout,cool,corrupt)

labels=list(map(get_name,NAMES))

assert len(labels)==len(NAMES)

mask=np.array([len(ur)>=num_iters for ur in urs])
if FINISHED:
    urs,labels,COLORS=np.array(urs)[mask],np.array(labels)[mask],np.array(COLORS)[:mask.sum()]


for (ur,c) in zip(urs,COLORS):

    plt.plot(xs[:len(ur)],ur,color=c)
    ind=np.argmax(ur)
    bests.append(ur[ind])
    # plt.scatter([xs[ind]],[ur[ind]],c=c)

ml=max([len(l) for l in labels])
names=["{}:".format(l)+" %.3f"%bests[i] for (i,l) in enumerate(labels)]
plt.legend(names,fontsize=3)



# plt.axhline(y=max(ur),xmin=min(xs),xmax=max(xs))
y_max=max([max(ur) for ur in urs])+0.1
plt.yticks(np.arange(0,0.05*round(y_max*20),0.05).tolist())
plt.title("AnimeULike DropoutNet Warm Start User Recall@100")
plt.xlabel("# of updates (thousands)")
plt.ylabel("user recall@100")
plt.savefig("metrics/{}".format(OUT_NAME),dpi=1000)