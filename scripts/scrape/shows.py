from utils.scrape_anime_local import *


import pandas as pd
from users import User
import os
import csv
from multiprocessing import Pool



class Show:
    scraped=None
    top_reviewers=[]
    pg_stop=50
    def __init__(self, id_):
        self.__id__=id_
        self.__pg_url__=pg_url(id_).rstrip('\n')
        self.__soup__=link_to_soup(self.__pg_url__)
        self.__reviews_soup__=link_to_soup(slug_to_name(self.__soup__))

    def extract_recommendations(self):
        rec_url=slug_to_name(self.__soup__).replace("reviews","userrecs")
        recs=get_pg_recs(rec_url)
        name=lambda x:int(x.split("/")[-2])
        rec_concat=lambda x:"\n".join([y.replace("\n","") for y in x])
        all_recs=[[self.__id__,name(x[0]),x[1],rec_concat(x[2])] for x in recs]
        return all_recs


    def extract_top_reviewers(self, no_per_show):#currently only supports those on first pg
        print("hey!")
        div=self.__reviews_soup__.find(class_="js-scrollfix-bottom-rel")
        
        reviews=div.find_all("div",class_="borderDark")[:no_per_show]
        reviewers=[]

        for review in reviews:
            div=child_find_all(review.div)[1]
            table=div.table
            td=child_find_all(table.tr,"td")[1]
            username=td.a.text
            reviewers.append(User(username))
        self.top_reviewers=reviewers

    def scrape_features(self):
        self.scraped=scrape_title(self.__pg_url__,self.pg_stop)[0]

    def write_to_csv(self,path):
        lis=self.scraped
        assert lis != []
        synopsis=lis[0]
        rating=float(lis[1])
        numericals=list(map(int,lis[1:6]))
        reviews=list(map(lambda x:x.replace('\n',''),lis[7:]))
        all_reviews='\n'.join(reviews)
        row_csv=[synopsis,rating]+numericals+[all_reviews]
        return row_csv
        
        
def group_write_to_csv(rows,path):
    b=True
    if os.path.isfile(path): b=False
    with open(path,'a+',newline='') as f:
        writer=csv.writer(f)
        if b: writer.writerow(["synopsis","rating","n1","n2","n3","n4","n5","reviews"])
        for row in rows: writer.writerow(row)

def group_write_rec_to_csv(rows,path):
    b=True
    if os.path.isfile(path): b=False
    with open(path,'a+',newline='') as f:
        writer=csv.writer(f)
        if b: writer.writerow(["show1","show2","helpful","recs"])
        for row in rows: writer.writerow(row)
    


def process_show(title):
    s=Show(title)
    s.scrape_features()
    return s.write_to_csv("")

import pdb 

def pool_scrape(output_file,target_file,prog_file,base,chunk_size=1):
    titles=get_batch(target_file,prog_file,chunk_size)
    inp=lambda x:int(x)
    out=lambda x:list(map(lambda y:tuple([y]),x))
    try:
        res=pool_res(process_show,titles,inp,out,chunk_size)
        assert len(res)>0
        print("writing")
        group_write_to_csv(res,output_file)
        write_res(prog_file,titles,"")
    except Exception as e:
        print(e)
        raise AssertionError
        
    

def get_r(title): 
    return Show(title).extract_recommendations()

def pool_recs(output_file,target_file,prog_file,base,chunk_size=8):
    titles=get_batch(output_file,prog_file,chunk_size)
    assert len(titles)>0
    inp=lambda x:int(x)


    titles=list(map(int,titles))
    with Pool(chunk_size) as p:
        res=p.map(get_r,titles)
    
    x=[]
    for r in res: 
        x.extend(list(filter(lambda y:y[1] in titles_set,r)))
    print("writing")
    group_write_rec_to_csv(x,"recs.csv")
    for title in titles: open(base+"/anime_processed.txt",'a+').write(str(title)+"\n")
    
#to scrape all pg features, run

# while True:
#     try: 
#         pool_scrape(base,8)
#     except Exception as e:
#         print(e)
#         break

if __name__=="__main__":
    base=os.path.dirname(__file__)
    while True:
        output_file=os.path.join(os.getcwd(),"10000_animes.csv")
        target_file=os.path.join(base,"utils/data","10000_shows_to_process.txt")
        prog_file=os.path.join(base,"utils/data","10000_anime_processed.txt")
        try: 
            pool_scrape(output_file,target_file,prog_file,base,32)
        except:
            break
    