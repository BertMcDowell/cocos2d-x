#!/usr/bin/python
# create_project.py
# Create cross-platform cocos2d-x project
# Copyright (c) 2012 cocos2d-x.org
# Author: WangZhe

# define global variables
context = {
"language"          : "undefined",
"src_project_name"  : "undefined",
"src_package_name"  : "undefined", 
"dst_project_name"  : "undeifned",
"dst_package_name"  : "undefined",
"src_project_path"  : "undefined",
"dst_project_path"  : "undefined",
"script_dir"        : "undefined",
"dst_upgrade_path"  : "undefined",
}
platforms_list = []

frameworksDest = "proj/Frameworks"
frameworks = {
"cocos2d_libs.xcodeproj" : "../../cocos2d_libs.xcodeproj",
"cocos2d-win32.vc2012.sln" : "../../cocos2d-win32.vc2012.sln",
"cocos2dx" : "../../cocos2dx",
"CocosDenshion" : "../../CocosDenshion",
"extensions" : "../../extensions",
"external/Box2D" : "../../external/Box2D",
"external/chipmunk" : "../../external/chipmunk",
"external/emscrpten" : "../../external/emscripten",
"external/libwebsockets" : "../../external/libwebsockets",
"external/sqlite3" : "../../external/sqlite3", 
"scripting/javascript" : "../../scripting/javascript", 
"scripting/lua" : "../../scripting/lua", 
}


content = {
"Classes" : "Classes",
"Resources" : "Resources",
}

# begin
import sys
import os, os.path
import json
import shutil
from shutil import ignore_patterns

def dumpUsage():
    print "Usage: create_project.py -project PROJECT_NAME -package PACKAGE_NAME -language PROGRAMING_LANGUAGE"
    print "Options:"
    print "  -project   PROJECT_NAME          Project name, for example: MyGame"
    print "  -package   PACKAGE_NAME          Package name, for example: com.MyCompany.MyAwesomeGame"
    print "  -language  PROGRAMING_LANGUAGE   Major programing lanauge you want to used, should be [cpp | lua | javascript]"
    print "  -path      OUTPUT_PATH           Optional destination path"
    print "  -upgrade   PROJECT_PATH          Path to the project to upgrade"
    print "  -help      HELP                  Display this message"
    print ""
    print "Sample 1: ./create_project.py -project MyGame -package com.MyCompany.AwesomeGame"
    print "Sample 2: ./create_project.py -project MyGame -package com.MyCompany.AwesomeGame -language javascript"
    print "Sample 3: ./create_project.py -project MyGame -package com.MyCompany.AwesomeGame -path path/to/project"
    print "Sample 4: ./create_project.py -project MyGame -upgrade path/to/project"
    print ""

def checkParams(context):
    # generate our internal params
    context["script_dir"] = os.getcwd() + "/"
    global platforms_list
    
    # invalid invoke, tell users how to input params
    if len(sys.argv) <= 0:
        dumpUsage()
        sys.exit()

    if "-help" == sys.argv[0]:
        dumpUsage()
        sys.exit()
    
    # set the default output path
    context["dst_project_path"] = os.getcwd() + "/../../projects/"

    # find our params
    for i in range(1, len(sys.argv)):
        if "-upgrade" == sys.argv[i]:
            # read the next param as upgrade_path
            context["dst_upgrade_path"] = sys.argv[i+1]
        if "-project" == sys.argv[i]:
            # read the next param as project_name
            context["dst_project_name"] = sys.argv[i+1]
        elif "-package" == sys.argv[i]:
            # read the next param as g_PackageName
            context["dst_package_name"] = sys.argv[i+1]
        elif "-language" == sys.argv[i]:
            # choose a scripting language
            context["language"] = sys.argv[i+1]
        elif "-path" == sys.argv[i]:
            # change the destination path
            context["dst_project_path"] = sys.argv[i+1]

    # pinrt error log our required paramters are not ready
    if context["dst_upgrade_path"] == "undefined":
        # append the project name to the path
        context["dst_project_path"] = os.path.join(context["dst_project_path"], context["dst_project_name"])

        raise_error = False
        if context["dst_project_name"] == "undefined":
            print "Invalid -project parameter"
            raise_error = True
        if context["dst_package_name"] == "undefined":
            print "Invalid -package parameter"
            raise_error = True
        if context["language"] == "undefined":
            print "Invalid -language parameter"
            raise_error = True
        if raise_error != False:
            dumpUsage()
            sys.exit()
                                     
        # fill in src_project_name and src_package_name according to "language"
        if ("cpp" == context["language"]):
            context["src_project_name"] = "HelloCpp"
            context["src_package_name"] = "org.cocos2dx.hellocpp"
            context["src_project_path"] = os.getcwd() + "/../../template/multi-platform-cpp"
            platforms_list = ["ios",
                              "android",
                              "win32",
                              "mac",
                              "blackberry",
                              "linux",
                              "marmalade"]
        elif ("lua" == context["language"]):
            context["src_project_name"] = "HelloLua"
            context["src_package_name"] = "org.cocos2dx.hellolua"
            context["src_project_path"] = os.getcwd() + "/../../template/multi-platform-lua"
            platforms_list = ["ios",
                              "android",
                              "win32",
                              "blackberry",
                              "linux",
                              "marmalade"]
        elif ("javascript" == context["language"]):
            context["src_project_name"] = "HelloJavascript"
            context["src_package_name"] = "org.cocos2dx.hellojavascript"
            context["src_project_path"] = os.getcwd() + "/../../template/multi-platform-js"
            platforms_list = ["ios",
                              "android",
                              "win32"]

    else:
        # append the project name to the path
        context["src_project_path"] = os.getcwd()
        context["dst_upgrade_path"] = os.path.join(context["dst_upgrade_path"], context["dst_project_name"])

# end of checkParams(context) function

def ireplace(old, new, text):
    idx = 0
    while idx < len(text):
        index_l = text.lower().find(old.lower(), idx)
        if index_l == -1:
            return text
        text = text[:index_l] + new + text[index_l + len(old):]
        idx = index_l + len(old)
    return text
# end ivariant string replace

def replaceString(filepath, src_string, dst_string):
    content = ""
    f1 = open(filepath, "rb")
    for line in f1:
        if src_string in line:
            content += ireplace(src_string, dst_string, line)
        else:
            content += line
    f1.close()
    f2 = open(filepath, "wb")
    f2.write(content)
    f2.close()
# end of replaceString

def replaceStrings(filepath, src_strings, dst_strings):
    content = ""
    f1 = open(filepath, "rb")
    for line in f1:
        for i in range(len(src_strings)):
            if src_strings[i] in line:
                line = ireplace(src_strings[i], dst_strings[i], line)
        content += line
    f1.close()
    f2 = open(filepath, "wb")
    f2.write(content)
    f2.close()
# end of replaceStrings

def replaceStringsInDir(path, src_strings, dst_strings):
    for root, dirs, files in os.walk(path):
        for name in files:
            replaceStrings(os.path.join(root, name), src_strings, dst_strings)
# end of replaceStringsInDir

def processPlatformProjects(platform):
    # determine proj_path
    proj_path = context["dst_project_path"] + "/proj.%s/" % platform
    java_package_path = ""

    # read josn config file or the current platform
    f = open("%s.json" % platform)
    data = json.load(f)

    # rename package path, like "org.cocos2dx.hello" to "com.company.game". This is a special process for android
    if (platform == "android"):
        src_pkg = context["src_package_name"].split('.')
        dst_pkg = context["dst_package_name"].split('.')
        os.rename(proj_path + "src/" + src_pkg[0],
                  proj_path + "src/" + dst_pkg[0])
        os.rename(proj_path + "src/" + dst_pkg[0] + "/" + src_pkg[1],
                  proj_path + "src/" + dst_pkg[0] + "/" + dst_pkg[1])
        os.rename(proj_path + "src/" + dst_pkg[0] + "/" + dst_pkg[1] + "/" + src_pkg[2],
                  proj_path + "src/" + dst_pkg[0] + "/" + dst_pkg[1] + "/" + dst_pkg[2])
        java_package_path = dst_pkg[0] + "/" + dst_pkg[1] + "/" + dst_pkg[2]

    # rename files and folders
    for i in range(0, len(data["rename"])):
        tmp = data["rename"][i].replace("PACKAGE_PATH", java_package_path)
        src = tmp.replace("PROJECT_NAME", context["src_project_name"])
        dst = tmp.replace("PROJECT_NAME", context["dst_project_name"])
        if (os.path.exists(proj_path + src) == True):
            os.rename(proj_path + src, proj_path + dst)

    # remove useless files and folders
    for i in range(0, len(data["remove"])):
        dst = data["remove"][i].replace("PROJECT_NAME", context["dst_project_name"])
        if (os.path.exists(proj_path + dst) == True):
            shutil.rmtree(proj_path + dst)
    
    # rename package_name. This should be replaced at first. Don't change this sequence
    for i in range(0, len(data["replace_package_name"])):
        tmp = data["replace_package_name"][i].replace("PACKAGE_PATH", java_package_path)
        dst = tmp.replace("PROJECT_NAME", context["dst_project_name"])
        if (os.path.exists(proj_path + dst) == True):
            replaceString(proj_path + dst, context["src_package_name"], context["dst_package_name"])
    
    # rename project_name
    for i in range(0, len(data["replace_project_name"])):
        tmp = data["replace_project_name"][i].replace("PACKAGE_PATH", java_package_path)
        dst = tmp.replace("PROJECT_NAME", context["dst_project_name"])
        if (os.path.exists(proj_path + dst) == True):
            replaceString(proj_path + dst, context["src_project_name"], context["dst_project_name"])
                  
    # done!
    print "proj.%s\t\t: Done!" % platform
# end of processPlatformProjects



# -------------- main --------------
# dump argvs
# print sys.argv

# prepare valid "context" dictionary
checkParams(context)
# import pprint
# pprint.pprint(context)
print context["dst_upgrade_path"]
if context["dst_upgrade_path"] != "undefined":

    if (os.path.exists(context["dst_upgrade_path"]) == True):

        # define the frameworks path
        frameworksPath = os.path.join ( context["dst_upgrade_path"], frameworksDest )
        print frameworksPath
        if (os.path.exists(frameworksPath) == True):
        
            # copy frameworks into the folder
            for framework in frameworks.keys():
                frameworkPath = frameworks[framework]
                sourcePath = context["src_project_path"]+"/"+frameworkPath
                destinationPath = os.path.join ( frameworksPath, framework )
                
                if (os.path.exists(destinationPath) == True):
                    shutil.rmtree(destinationPath, ignore_errors=True);
                
                if (os.path.isdir(sourcePath) == True):
                    shutil.copytree( sourcePath, destinationPath, symlinks=False, ignore=ignore_patterns('.*') )
                else:
                    shutil.copyfile ( sourcePath, destinationPath )
                
                print "Updated framework: " + framework


            print "Upgrade project complete at path: " + context["dst_upgrade_path"]

        else:
            print "Error:" + frameworksPath + " folder does not exists"
    else:
        print "Error:" + context["dst_upgrade_path"] + " folder does not exists"

else:

    # copy "lauguage"(cpp/lua/javascript) platform.proj into cocos2d-x/projects/<project_name>/folder
    if (os.path.exists(context["dst_project_path"]) == True):
        print "Error:" + context["dst_project_path"] + " folder already exists"
        print "Please remove the old project or choose a new PROJECT_NAME in -project parameter"
        sys.exit()
    else:
        shutil.copytree(context["src_project_path"], context["dst_project_path"], symlinks=False, ignore=ignore_patterns('.*'))

    # call process_proj from each platform's script folder          
    for platform in platforms_list:
        processPlatformProjects(platform)
    #    exec "import %s.handle_project_files" % (platform)
    #    exec "%s.handle_project_files.handle_project_files(context)" % (platform)

    # check to see if the path is not the default path
    if not "/../../projects/" in context["dst_project_path"]:
        # define the frameworks path
        frameworksPath = os.path.join ( context["dst_project_path"], frameworksDest )
        # create a frameworks path
        os.makedirs ( frameworksPath )

        # relative path to the project
        fixPathOrig = [ 
                        "../../../..", 
                        " ../../cocos2dx", 
                        " ../classes",
                        "path = ../Classes/AppDelegate.cpp;",
                        "path = ../Classes/AppDelegate.h;",
                        "path = ../Classes/HelloWorldScene.cpp;",
                        "path = ../Classes/HelloWorldScene.h;",
                        ]
        fixPathDest = [ 
                        "../"+frameworksDest, 
                        " ../"+frameworksDest+"/cocos2dx", 
                        " ../proj/classes",
                        "path = AppDelegate.cpp;",
                        "path = AppDelegate.h;",
                        "path = HelloWorldScene.cpp;",
                        "path = HelloWorldScene.h;",
                         ]

        # copy frameworks into the folder
        for framework in frameworks.keys():
            frameworkPath = frameworks[framework]
            sourcePath = context["src_project_path"]+"/"+frameworkPath
            destinationPath = os.path.join ( frameworksPath, framework )
            if (os.path.isdir(sourcePath) == True):
                shutil.copytree( sourcePath, destinationPath, symlinks=False, ignore=ignore_patterns('.*') )
            else:
                shutil.copyfile ( sourcePath, destinationPath )
            fixPathOrig.append ( frameworkPath )
            fixPathOrig.append ( frameworkPath.replace("/", "\\") )
            fixPathDest.append ( os.path.join ( frameworksDest, framework ) )
            fixPathDest.append ( os.path.join ( frameworksDest, framework ).replace("/", "\\") )
            print "Copied framework: " + framework

        #move the content folders
        contentDest = "proj"
        contentsPath = os.path.join ( context["dst_project_path"], contentDest )
        for contentKey in content:
            contentValue = content[contentKey]
            sourcePath = context["dst_project_path"]+"/"+contentValue
            destinationPath = os.path.join ( contentsPath, contentKey )
            shutil.move( sourcePath, destinationPath )
            fixPathOrig.append ( "../"+contentValue )
            fixPathOrig.append ( "..\\"+contentValue.replace("/", "\\") )
            fixPathDest.append ( "../"+os.path.join ( contentDest, contentKey ) )
            fixPathDest.append ( "..\\"+os.path.join ( contentDest, contentKey ).replace("/", "\\") )
            print "Moved Content: " + contentValue + " " + contentKey + " " + contentDest

        # on ios this messesup due to the class dir
        # fixPathOrig.append ( "path = ../classes;" )
        # fixPathDest.append ( "" )

        # fix up the refrences to the frameworks
        for platform in platforms_list:
            proj_path = context["dst_project_path"] + "/proj.%s/" % platform
            replaceStringsInDir (proj_path, fixPathOrig, fixPathDest)
            replaceStringsInDir (proj_path, [ "../proj.%s/" % platform ], [ "../../proj.%s/" % platform ])
            print "Fixed up frameworks for platform: " + platform


    print "New project has been created in this path: " + context["dst_project_path"].replace("/tools/project-creator/../..", "")
    print "Have Fun!"

