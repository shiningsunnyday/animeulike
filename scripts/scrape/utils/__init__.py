import os

print(os.getcwd())

if __name__=="__main__":
    base=os.path.dirname(os.path.relpath(__file__))
    # read_titles()
    # pref=process()
    # factor(pref)

    print(base)