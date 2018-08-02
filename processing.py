import os
import sys

if __name__ == '__main__':
    with open('rat_list.txt') as f:
        ratname = f.readline()
        while len(ratname) > 1:
            print "processing -->" + ratname[0:-1]
            os.chdir("C:/tools")
            os.system("python uipath_project_render.py \"" + ratname[0:-1] + "\"")
            ratname = f.readline()