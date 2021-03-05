import os
import numpy as np
import pandas as pd
if __name__ == "__main__":
    base=os.path.dirname(os.path.relpath(__file__))
    a_path=base+"/animes.csv"
    df=pd.read_csv(a_path)
    np.random.seed(0)
    val_test=np.random.choice(np.arange(len(df)),85,replace=False)
    train_mask=np.ones(len(df))
    train_mask[val_test]=0
    test=np.random.choice(np.arange(len(val_test)),35,replace=False)
    val_mask=np.ones(len(val_test))
    val_mask[test]=0
    train_inds,val_inds,test_inds=np.arange(len(df))[train_mask==1],val_test[val_mask==1],val_test[val_mask==0]
    train_inds,val_inds,test_inds=sorted(train_inds),sorted(val_inds),sorted(test_inds)
    train_df,val_df,test_df=df.iloc[train_inds],df.iloc[val_inds],df.iloc[test_inds]
    train_df['index'],val_df['index'],test_df['index']=train_inds,val_inds,test_inds
    train_df.set_index('index')
    val_df.set_index('index')
    test_df.set_index('index')
    print(train_df.head())
    assert len(set(train_inds).intersection(set(val_inds)))==0
    assert len(set(val_inds).intersection(set(test_inds)))==0
    assert len(set(train_inds).intersection(set(test_inds)))==0
    paths={}
    for s in {'train','val','test'}:
        x=a_path.replace('animes','animes_{}'.format(s))
        df_v=locals()['{}_df'.format(s)]
        df_v.to_csv(x)