from utils.scrape_anime_local import *
from users import User
class Show:
    top_reviewers=[]
    def __init__(self, id_):
        self.__id__=id_
        self.__soup__=link_to_soup(pg_url(id_))
        self.__reviews_soup__=link_to_soup(slug_to_name(self.__soup__))

    def extract_top_reviewers(self, no_per_show):#currently only supports those on first pg
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

    
def retrieve_top_shows(num_shows,users_per_show):
    series=[link_to_id(x) for x in get_series(num_shows)]
    shows=[]
    for serie in series:
        try:
            show=Show(serie)
            show.extract_top_reviewers(users_per_show)
            shows.append(show)
            print("got {}!".format(serie))
        except:
            print("didn't get",serie)
    return shows
    
if __name__=="__main__":
    show=Show(5114)
    show.extract_top_reviewers(3)
    print([user.__username__ for user in show.top_reviewers])