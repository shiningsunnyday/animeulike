from shows import *
import os

from iteration_utilities import flatten
import argparse 

fil=os.path.dirname(__file__)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('-n','--num',default=2,required=False)
    parser.add_argument('-u','--num_per', default=2,required=False) # remove duplicates, so actual count is lower
    parser.add_argument('-p','--path',default="utils/data/id_to_username.txt",required=False)
    parser.add_argument('-r','--result',default="utils/data/user_ratings.txt",required=False)
    args=vars(parser.parse_args())
    shows=retrieve_top_shows(args["num"],args["num_per"])
    users=list(set(flatten([show.top_reviewers for show in shows])))
    inds={}
    with open(os.path.join(fil,args['path']),'w+') as f:
        for (i, u) in enumerate(users): 
            f.write('{} {}'.format(i, u.__username__))
            inds[u.__username__]=i
    all_ratings=[user_ratings(user.__username__,user.__username__) for user in users]
    all_ratings=sorted(all_ratings,key=lambda x:-len(x))
    ratings=list(flatten(all_ratings))
    with open(os.path.join(fil,args['result']),'w+') as f:
        for rating in ratings: 
            res=list(map(str,[inds[rating[0]]]+rating[1:]))
            f.write(' '.join(res)+'\n')
