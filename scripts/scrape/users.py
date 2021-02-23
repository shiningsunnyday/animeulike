from utils.scrape_anime_local import *
class User:
    ratings_cache=[]
    reviewed_link=None
    def __init__(self, username):
        self.__username__=username
        self.reviewed_link=reviewer_link(username)
    
    def extract_ratings(self):
        self.ratings_cache=get_mal_user_ratings([self.__username__])
        return self.ratings_cache

if __name__=="__main__":
    user=User("tazillo")
    print(user.extract_ratings())
    