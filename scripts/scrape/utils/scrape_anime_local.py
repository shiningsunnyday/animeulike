#!/usr/bin/env python
# coding: utf-8

# In[3]:


import urllib.request
import bs4
import numpy as np

MAL_TOP_USER_LINK="https://myanimelist.net/reviews.php?st=mosthelpful"
CROLL_LINK="https://www.crunchyroll.com/videos/anime"


# In[4]:


def link_to_soup(link,html=False):
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
        

def get_series(num_shows):
    links=[]
    for pg in range(0,(num_shows-1)//50+1):
        url="https://myanimelist.net/topanime.php?limit={}".format(50*pg)
        soup=link_to_soup(url)
        trs=soup.find_all("tr",class_="ranking-list")
        for tr in trs:
            td=tr.find_all('td')[1]
            links.append(td.a['href'])
            if len(links)==num_shows: break
    return links


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
    rank=extract(ranked.span.next_sibling)
    rank=int(rank)
    pop_div=ranked_div.parent
    divs=pop_div.find_all('div')
    fav=extract(divs[-2].span.next_sibling)
    members=extract(divs[-3].span.next_sibling)
    pop=extract(divs[-4].span.next_sibling)
    return [rank,pop,members,fav]

def get_reviews(soup):    
    #divs with e.g. id=score12912 identifies a user
    numeric_reviews=soup.find_all('div',attrs={"id":lambda x: x and "score" in x})
    #for each numeric review, 
    #every category is rating/10, [overall,story,animation,sound,character,enjoyment]
    numerics=[]
    for numeric_review in numeric_reviews:
        numeric=[]
        table=numeric_review.table
        for tr in table.find_all("tr"):
            numeric.append(int(tr.find_all('td')[-1].text))
        numerics.append(numeric)
        paragraphs=numeric_review.next_siblings
        review=""
        for p in paragraphs:
            if type(p)==bs4.element.Tag and p.name=="span": break
            elif type(p)==bs4.NavigableString: review+=p
        numerics.append(review)
    return numerics



def scrape_title(page):
    #feat_vec:[synopsis,score,numeric feats,
    #          reviewer's category ratings + reviewer's review for all reviewers]
    #e.g. "https://myanimelist.net/anime/5114/Fullmetal_Alchemist__Brotherhood"
    soup=link_to_soup(page)
    lis=[get_synopsis(soup),get_score(soup)]
    lis.extend(get_numerical_features(soup))
    i=1; a=-1; b=len(lis)
    while len(lis)>a:
        a=len(lis)
        lis.extend(get_reviews(link_to_soup(page+"/reviews?p={}".format(i))))
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
    soup=link_to_soup(link)
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
    reviews=[]; l=0; i=0;
    while True:
        l=len(reviews)
        i+=1
        try:
            link=pg_link(i)
            reviews.extend(pg_reviews(link,ind))
            print("#reviews from {} is now {}".format(name,len(reviews)))
        except:
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

if __name__ == "__main__":
    ratings=get_mal_user_ratings() #[of form [index of user,anime id,#helpful,rating]]
    np.savetxt('data/user_ratings.txt',ratings,'%d')
    users=get_mal_top_users()
    write_id_username(users)


