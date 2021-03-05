#!/usr/bin/env python
# coding: utf-8

# In[3]:


import urllib.request
import bs4
from iteration_utilities import flatten
import numpy as np
import os

from multiprocessing import Pool


MAL_TOP_USER_LINK="https://myanimelist.net/reviews.php?st=mosthelpful"
CROLL_LINK="https://www.crunchyroll.com/videos/anime"


# In[4]:


def link_to_soup(link,html=False):
    link=link.encode("ascii",'ignore')
    link=link.decode()
    source = urllib.request.urlopen(link).read()
    soup=bs4.BeautifulSoup(source,'lxml' if html else 'html.parser')
    return soup
def numeric(s):
    #returns only digits
    lis=list(s)
    dig=lambda x:x>='0' and x<='9'
    return int(''.join(list(filter(lambda x:dig(x),lis))))

def child_find_all(x,tag="div",class_=None):
    lis=list(filter(lambda y:y.name==tag,x.contents))
    return list(filter(lambda y:y.class_==class_,lis)) if class_ else lis
def child_find(x,tag="div"):
    return child_find_all(x)[0]

def slug_to_name(soup):
    nav=soup.find(attrs={"id":"horiznav_nav"})
    li=child_find_all(nav.ul,'li')[3]
    return li.a['href']
def reviewer_link(username):
    return "https://myanimelist.net/profile/{}/reviews".format(username)

# In[5]:
def pg_url(id_,reviews=False):
    s="https://myanimelist.net/anime/"
    s+="{}".format(id_)
    if reviews: s=slug_to_name(s)
    return s

def get_pg(i):
    links=[]
    url="https://myanimelist.net/topanime.php?limit={}".format(50*int(i))
    soup=link_to_soup(url)
    trs=soup.find_all("tr",class_="ranking-list")
    for tr in trs:
        td=tr.find_all('td')[1]
        link=td.a['href']
        links.append(int(link.split("/")[-2]))
    return links

def write_res(output_file,res,app="\n"):
    with open(output_file,'a+') as f:
        for r in res:
            f.write("{}{}".format(str(r),app))

def write_prog(progress_file,out):
    with open(progress_file,'a+') as f:
        for o in out: f.write("{}".format(str(o)))

def get_batch(output_file,progress_file,batch_size):
    if not os.path.isfile(output_file):
        f=open(output_file,'w+')
        f.close()
    if not os.path.isfile(progress_file):
        f=open(progress_file,'w+')
        f.close()
    f=open(progress_file,'r')
    num_read=len(f.readlines())
    print(num_read,"read")
    return open(output_file,"r").readlines()[num_read:num_read+batch_size]


def setup_shows_to_retrieve(num_shows):
    fil=os.path.dirname(__file__)
    target_file=os.path.join(fil,"data/pages_to_process.txt")
    prog_file=os.path.join(fil,"data/processed_pages.txt")
    out_file=os.path.join(fil,"data/10000_shows_to_process.txt")
    if not os.path.isfile(target_file):
        with open(target_file,'w+') as f:
            for pg in range(0,(num_shows-1)//50+1): 
                f.write("{}\n".format(pg)) 

    if not os.path.isfile(prog_file):
        f=open(prog_file,'w+')
        f.close()
    return target_file,prog_file,out_file

def get_series(target_file,prog_file,out_file,chunk_size=32):
    links=[]
    to_read=get_batch(target_file,prog_file,chunk_size)
    with Pool(chunk_size) as p:
        res=p.map(get_pg,to_read)
        assert len(res)>0
        res=list(flatten(res))
    write_res(out_file,res)
    write_prog(prog_file,to_read)

def retrieve_top_shows(num_shows):
    target_file,prog_file,out_file=setup_shows_to_retrieve(num_shows)
    if len(open(prog_file,"r").readlines())<num_shows:
        get_series(target_file,prog_file,out_file)
        return False
    return True




# In[6]:




def get_synopsis(soup):
    descr=soup.find('p',itemprop="description")
    return descr.text

def get_score(soup):
    rating=soup.find('span',itemprop="ratingValue")
    return float(rating.text)

def get_numerical_features(soup):
    # [#ranked, #popularity, #members, #favorites]
    extract=lambda x:''.join(list(filter(lambda y:y.isdigit(),list(x))))
    ranked_div=soup.find('div',attrs={"data-id":"info2"})
    ranked=ranked_div
    try:
        rank=extract(ranked.span.next_sibling)
        rank=int(rank)
        pop_div=ranked_div.parent
        divs=pop_div.find_all('div')
        fav=extract(divs[-2].span.next_sibling)
        members=extract(divs[-3].span.next_sibling)
        pop=extract(divs[-4].span.next_sibling)
    except: 
        return [8.52,319,423028,3851]
    return [rank,pop,members,fav]

def get_reviews(soup):    
    #divs with e.g. id=score12912 identifies a user
    numeric_reviews=soup.find_all('div',attrs={"id":lambda x: x and "score" in x})
    #for each numeric review, 
    #every category is rating/10, [overall,story,animation,sound,character,enjoyment]
    numerics=[]
    for numeric_review in numeric_reviews:
        # numeric=[]
        # table=numeric_review.table
        # for tr in table.find_all("tr"):
        #     numeric.append(int(tr.find_all('td')[-1].text))
        # # numerics.append(numeric)
        paragraphs=numeric_review.next_siblings
        review=""
        for p in paragraphs:
            if type(p)==bs4.element.Tag and p.name=="span": break
            elif type(p)==bs4.NavigableString: review+=(p.encode('ascii','ignore').decode())
        numerics.append(review)
    return numerics



def scrape_title(page,pg_cut=99999):
    #feat_vec:[synopsis,score,numeric feats,
    #          reviewer's category ratings + reviewer's review for all reviewers]
    #e.g. "https://myanimelist.net/anime/5114/Fullmetal_Alchemist__Brotherhood"
    soup=link_to_soup(page)
    lis=[get_synopsis(soup).encode('ascii','ignore').decode(),get_score(soup)]
    lis.extend(get_numerical_features(soup))
    i=1; a=-1; b=len(lis)
    while i<pg_cut and len(lis)>a:
        a=len(lis)
        try:
            sp=link_to_soup(page+"/reviews?p={}".format(i))
            lis.extend(get_reviews(sp))
        except:
            print("oh no")
            break
        print("got pg {}'s reviews".format(i))
        i+=1
    return lis, len(lis)-b


# In[7]:


def link_to_id(link):
    a=link.split('/')
    ind=a.index('anime')
    return int(a[ind+1])

def get_recs():
    dic=[]
    soup=link_to_soup(rec_url)
    trs=soup.find_all("tr")
    for i in range(len(trs)):
        tr=trs[i]
        tds=tr.find_all('td')
        td1,td2=tds[0],tds[1]
        get_name=lambda td:td.div.a['href']
        if not td1 or not td2: continue
        n1=get_name(td1)
        n2=get_name(td2)
        dic.append((link_to_id(n1),link_to_id(n2)))
    return dic


# In[8]:


def get_pg_recs(page):
    #for robustness, only returns anime with at least two mentions
    soup=link_to_soup(page+"/userrecs")
    content=soup.find('div',attrs={'id':"content"})
    table=content.table
    td=list(filter(lambda x:x.name=="td",table.tr.contents))[1]
    class_match=lambda x:("borderClass" in x.attrs.get("class",dict()))
    rec_lambda=lambda x:x.name=="div" and class_match(x)
    divs=list(filter(rec_lambda,td.contents))
    all_recs=[]
    for div in divs:
        td=div.table.tr.find_all("td")[1]
        lis=(list(filter(lambda x:x.name=="div",td.contents)))
        name=lis[1].a["href"]
        rec=lis[2].div.text
        recs=[rec]
        try:
            no_recs=int(lis[3].a.strong.text)+1
        except IndexError:
            all_recs.append([name,1,recs])
            continue
        other_recs=lis[4].contents[1::2]
        for rec in other_recs:
            recs.append(rec.div.text)
        all_recs.append([name,no_recs,recs])
    return all_recs


# In[ ]:





# In[9]:


def pg_reviews(link,ind):
    # returns [[id,#helpful,#rating]]
    ratings=[]
    try:
        soup=link_to_soup(link)
    except:
        return ratings
    reviews=[x.div for x in soup.find_all("div",class_="borderDark")]
    for review in reviews:
        rating=review.div.find_all("div")[-1].text
        rating=numeric(rating)
        all_divs=child_find_all(review,"div")
        entity=all_divs[1]
        entity=entity.find("a")["href"]
        anime_id=int(entity.split("/")[-2])
        helpful=all_divs[-1]
        helpful=int(helpful.table.tr.td.div.strong.span.text)
        ratings.append([ind,anime_id,helpful,rating])
    return ratings

def user_ratings(name,ind):#ind is any unique identifier for user
    pg_link=lambda i:"https://myanimelist.net/profile/{}/reviews?p={}".format(name,i)
    reviews=[]
    i=-1
    while True:
        l=len(reviews)
        i+=1
        link=pg_link(i)
        reviews.extend(pg_reviews(link,ind))
        if len(reviews)==l:
            break
    return reviews
        
def get_mal_top_users():
    soup=link_to_soup(MAL_TOP_USER_LINK)
    body=soup.body
    desc=body.find("div",attrs={"id":"content"})
    table=body.find("table")
    trs=table.find_all("tr")[1:]
    names=[]
    for tr in trs:
        td=tr.find_all("td")[1]
        ref=td.a["href"]
        name=ref.split('/')[-1]
        names.append(name)
    return names
    
def get_mal_user_ratings(users=None,ind=0):
    if not users:
        users=get_mal_top_users()[ind:]
    ratings=[]
    for i in range(len(users)):
        ratings.extend(user_ratings(users[i],users[i]))
    return ratings


# In[10]:






# In[ ]:

def write_id_username(users,path='data/id_to_username.txt'):
    with open(path,'w+') as f:
        for i,username in enumerate(users):
            f.write("{} {}\n".format(i,username))


# In[ ]:

def process_show(show_id,no_per):
    try:
        show=Show(show_id)
    except UnicodeEncodeError:
        print(show_id,"BAD")
    show.extract_top_reviewers(no_per)
    return show.top_reviewers


def pool_res(func,inp,inp_map,out_map,num_processes):

    with Pool(num_processes) as p:
        inp=[inp_map(x) for x in inp]
        res=p.starmap(func,inp) if isinstance(inp[0],list) else p.map(func,inp)
        assert len(res)>0
        res=list(map(out_map,res))
    return list(flatten(res))

if __name__ == "__main__":
    print(get_reviews(link_to_soup("https://myanimelist.net/anime/5114/Fullmetal_Alchemist__Brotherhood/reviews?p=50")))


