
import os

fil=os.path.dirname(str(__package__))
print(fil)

from shows import *



from collections import OrderedDict
import argparse 






def process_shows(args,output_file,target_file,prog_file):
    while True:
        show_ids=get_batch(target_file,progress_file,args['chunk_size'])
        inp=lambda id_:(id_,args['num_per'])
        oup=lambda x:x 
        try: res=pool_res(process_show,show_ids,inp,oup,32) 
        except AssertionError: print("done"); break
        assert len(res)>0
        write_res(output_file,[u.__username__ for u in res])
        write_prog(progress_file,show_ids)

def process_users(args,output_file,target_file,progress_file):
    #make sure no username overlaps
    while True:
        shows_set=set([int(l.strip('\n')) for l in open(args['shows_path'],"r").readlines()])
        usernames=get_batch(target_file,progress_file,args['chunk_size'])
        if not len(usernames): break
        usernames=[un.strip('\n') for un in usernames]
        inp=lambda un:(un,un)
        
        oup0=lambda r:list(filter(lambda y:y[1] in shows_set,r))
        oup1=lambda lis:list(map(lambda x:" ".join(list(map(str,x))),lis))
        res=pool_res(user_ratings,usernames,inp,lambda x:oup1(oup0(x)),32)
        assert len(res)>0
        write_res(output_file,res)
        write_prog(progress_file,["{}\n".format(u) for u in usernames])

def sort_usernames(path,out_path):
    with open(path,'r') as f:
        users=sorted(list(set(f.readlines())))
    with open(out_path,'w+') as f:
        for u in users:
            f.write(u)

if __name__=="__main__":
    fil=os.path.dirname(__file__)

    parser=argparse.ArgumentParser()
    parser.add_argument('-n','--num',default=10000,required=False)
    parser.add_argument('-u','--num_per', default=10,required=False) # remove duplicates, so actual count is lower
    parser.add_argument('-p','--path',default="utils/data/",required=False)
    parser.add_argument('-c','--chunk_size',default=32,required=False)
    parser.add_argument('-t','--task',default=1,required=False,
    help='0: process shows, 1: fetch user\'s reviews, 2: fetch top show links')

    args=vars(parser.parse_args())
    
    if not args["task"]:
        output_file=os.path.join(fil,args['path']+"10000_usernames_to_process.txt")
        # target_file=os.path.join(fil,args['path']+"10000_shows_to_process.txt")
        # progress_file=os.path.join(fil,args['path']+"10000_processed_shows.txt")
        # process_shows(args,output_file,target_file,progress_file)
        sort_file=os.path.join(fil,args['path']+"10000_sorted_usernames_to_process.txt")
        sort_usernames(output_file,sort_file)
    elif args["task"]==1:
        args['shows_path']=os.path.join(fil,args['path']+"10000_shows_to_process.txt")

        output_file=os.path.join(fil,args['path']+"10000_user_ratings.txt")
        target_file=os.path.join(fil,args['path']+"10000_sorted_usernames_to_process.txt")
        prog_file=os.path.join(fil,args['path']+"10000_processed_users.txt")
        process_users(args,output_file,target_file,prog_file)
    else:
        while True:
            try: shows=retrieve_top_shows(args["num"])
            except AssertionError: break
            if shows:
                print("done")
                break

            
        
