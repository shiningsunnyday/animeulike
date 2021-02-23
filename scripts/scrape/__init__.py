from shows import *
import os
from multiprocessing import Pool

from iteration_utilities import flatten
from collections import OrderedDict
import argparse 

fil=os.path.dirname(__file__)

def process_show(show_id,no_per):
    show=Show(show_id)
    show.extract_top_reviewers(no_per)
    return show.top_reviewers

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('-n','--num',default=250,required=False)
    parser.add_argument('-u','--num_per', default=10,required=False) # remove duplicates, so actual count is lower
    parser.add_argument('-p','--path',default="utils/data/",required=False)
    parser.add_argument('-c','--chunk_size',default=32,required=False)
    parser.add_argument('-t','--task',default=1,required=False,
    help='0: process shows, 1: fetch user\'s reviews, 2: remove duplicates')

    args=vars(parser.parse_args())
    shows_path=os.path.join(fil,args['path']+"shows_to_process.txt")
    if not args["task"]:
        if not os.path.isfile(shows_path):
            shows=retrieve_top_shows(args["num"])
            with open(shows_path,"w+") as f: 
                for x in shows: f.write("{}\n".format(x.__id__))
        num_read=0
        output_file=os.path.join(fil,args['path']+"usernames_to_process.txt")
        progress_file=os.path.join(fil,args['path']+"read_shows.txt")
        if os.path.isfile(progress_file):
            f=open(progress_file)
            num_read=len(f.readlines())
            print(num_read,"read")
        show_ids=open(shows_path,"r").readlines()[num_read:num_read+args['chunk_size']]
        with Pool(32) as p:
            x=p.starmap(process_show,[(id_,args['num_per']) for id_ in show_ids])
            #all or nothing, good for repeatedly running script
            users=list(flatten(x))
        with open(output_file,'a+') as f:
            for (i, u) in enumerate(users): 
                f.write('{}\n'.format(u.__username__))
        with open(progress_file,'a+') as f:
            for id_ in show_ids: f.write("{}".format(id_)) #writes finished ids
    elif args["task"]==1:
        #make sure no username overlaps
        users_path=os.path.join(fil,args['path']+"usernames_to_process.txt")
        temp_path=os.path.join(fil,args['path']+"temp.txt")
        od=OrderedDict.fromkeys(open(users_path).readlines())
        with open(temp_path,"w+") as f:
            for k in od.keys(): f.write(k)
        users_path=temp_path
        while True:
            num_read=0
            progress_file=os.path.join(fil,args['path']+"read_users.txt")
            output_file=os.path.join(fil,args['path']+"user_ratings.txt")
            shows_set=set([int(l.strip('\n')) for l in open(shows_path,"r").readlines()])
            if os.path.isfile(progress_file):
                f=open(progress_file)
                num_read=len(f.readlines())
                print(num_read,"read")
            usernames=open(users_path,'r').readlines()[num_read:num_read+args['chunk_size']]
            if not len(usernames): break
            usernames=[un.strip('\n') for un in usernames]
            with Pool(32) as p:
                x=p.starmap(user_ratings,[(un,un) for un in usernames])    
                all_ratings=[list(filter(lambda y:y[1] in shows_set,ratings)) for ratings in x]
            flat_ratings=list(flatten(all_ratings))
            assert len(flat_ratings) > 0#mal occasionally blocks
            with open(output_file,'a+') as f:
                for f_r in flat_ratings:
                    res=list(map(str,[f_r[0]]+f_r[1:]))
                    f.write(' '.join(res)+'\n')
            with open(progress_file,'a+') as f:
                for un in usernames: f.write("{}\n".format(un))
    elif args["task"]==2:
        pass
