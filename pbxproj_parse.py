#!/usr/bin/env python2.7
#-*- coding: utf-8 -*-
'''
@Author: shangshangqian
@since: 2019-11-13
@lastTime: 2019-11-14
@tip: Do not edit
'''


import json
import os
import sys
import cgi
import optparse
import traceback
import commands
import plistlib
import time
from datetime import datetime

pbxproj_objects_gloabl = {}
pbxproj_json_gloabl = '0'
option_global = ''#option==0表示获取每个target没有勾选的文件 option==1表示获取每个文件没有勾选的target

def parse_targets(project):
    targets = project['targets'];#获取所有target的target_id
    target_dict = {}
    all_file_list = []
    for target_id in targets:
        target = pbxproj_objects_gloabl[target_id]
        buildPhases_list = parse_target_buildPhases(target)
        all_file_list = list(set(buildPhases_list) | set(all_file_list))#并集，取到所有target所有的编译文件
        target_dict[target['name']] = list(set(buildPhases_list))
    
    if option_global == '0':
       parse_target_miss(target_dict,all_file_list)
    else:
       parse_file_ontarget(target_dict,all_file_list)
#    with open(pbxproj_json_gloabl,'w') as f:
#         json.dump(target_dict,f)
#         print("加载入文件完成...")

#获取每个编译文件没有勾选的target
def parse_file_ontarget(target_dict,all_file_list):
    miss_target_dict = {}
    for file_name in all_file_list:
        miss_target_list = []
        for target_name in target_dict.keys():
            target_files = target_dict[target_name]
            tmp_list = [file_name]
            intersection_list = list(set(tmp_list) & set(target_files))#取到当前文件名与target下编译文件的交集，如果数组数量小于1说明当前target里面不包含当前的文件名
            if len(intersection_list) < 1 and target_name != 'JoywokShareEx':
               miss_target_list.append(target_name)
                   
        if len(miss_target_list) > 0:
           miss_target_dict[file_name] = miss_target_list

    with open(pbxproj_json_gloabl,'w') as f:
         f.write('***********************************\n')
         f.write('json内容表示每个文件没有勾选的target\n')
         f.write('***********************************\n')
         json.dump(miss_target_dict,f,indent=4)
         print "\033[0;33m解析完成\033[0m"
         print "\033[0;35m ===================================================== \033[0m"
         print "\033[0;35m 分析文件路径:{0} \033[0m".format(pbxproj_json_gloabl)
         print "\033[0;35m ===================================================== \033[0m"

#获取每个target没有勾选的文件
def parse_target_miss(target_dict,all_file_list):
    miss_file_dict = {}
    for target_name in target_dict.keys():
        target_files = target_dict[target_name]
        intersection_list = list(set(all_file_list) - set(target_files))
        if len(intersection_list) > 0 and target_name != 'JoywokShareEx':
           miss_file_dict[target_name] = intersection_list

    with open(pbxproj_json_gloabl,'w') as f:
         f.write('***********************************\n')
         f.write('json内容表示每个target没有勾选的文件\n')
         f.write('***********************************\n')
         json.dump(miss_file_dict,f,indent=4)
         print "\033[0;33m解析完成\033[0m"
         print "\033[0;35m ===================================================== \033[0m"
         print "\033[0;35m 分析文件路径:{0} \033[0m".format(pbxproj_json_gloabl)
         print "\033[0;35m ===================================================== \033[0m"



#解析单个target下buildPhases的文件
def parse_target_buildPhases(target):
    buildPhases = target['buildPhases'];
    buildPhases_list = []
    for buildPhases_id in buildPhases:
        buildPhases_obj = pbxproj_objects_gloabl[buildPhases_id]
        if buildPhases_obj['isa'] == 'PBXSourcesBuildPhase':
            if len(parse_sources_phase(buildPhases_obj)) > 0:
               buildPhases_list.extend(parse_sources_phase(buildPhases_obj))
        elif buildPhases_obj['isa'] == 'PBXResourcesBuildPhase':
             if parse_resources_phase(buildPhases_obj) > 0:
                buildPhases_list.extend(parse_resources_phase(buildPhases_obj))

    return buildPhases_list

#获取target下的.m文件
def parse_sources_phase(buildPhases_obj):
    files = buildPhases_obj['files']
    sources_list = []
    for build_file_id in files:
        if pbxproj_objects_gloabl.has_key(build_file_id):
           build_file = pbxproj_objects_gloabl[build_file_id]
           if build_file.has_key('fileRef'):
              file_ref = build_file['fileRef']
              file_reference = pbxproj_objects_gloabl[file_ref]
              sources_list.append(file_reference['path'])

    return sources_list

#获取target下的.xib和.storyboard文件
def parse_resources_phase(buildPhases_obj):
    files = buildPhases_obj['files']
    resources_list = []
    file_reference_name = ''
    for build_file_id in files:
        build_file = pbxproj_objects_gloabl[build_file_id]
        if build_file.has_key('fileRef'):
           file_ref = build_file['fileRef']
           file_reference = pbxproj_objects_gloabl[file_ref]
           if file_reference['isa'] == 'PBXFileReference':
              if file_reference.has_key('path'):
                  file_reference_name = file_reference['path']
           elif file_reference['isa'] == 'PBXVariantGroup':
                file_reference_name = file_reference['name']

        if len(file_reference_name) > 0 and parse_valid_resources(file_reference_name) == True:
            resources_list.append(file_reference_name)

    return resources_list

#判断当前获取的文件名是否包含.xib和.storyboard
def parse_valid_resources(file_reference_name):
    if file_reference_name.endswith('.storyboard'):
        return True
    elif file_reference_name.endswith('.xib'):
        return True
    else:
       return False


if __name__ == '__main__':
    
    parser = optparse.OptionParser()
    parser.add_option("-p","--pbxproj_path", help="pbxproj的路径path")
    parser.add_option("-o","--option", help="option==0表示获取每个target没有勾选的文件 option==1表示获取每个文件没有勾选的target")
    (options, args) = parser.parse_args()
    pbxproj_path = options.pbxproj_path
    option = options.option
    if option is None:
       option_global = '0'
    else:
        option_global = option

    print "\033[0;33m正在解析pbxproj...\033[0m"
    #生成文件路径
    pbxproj_json_path ='{0}/project.json'.format(os.path.join(os.path.expanduser('~'),'Desktop'))
    if os.path.exists(pbxproj_json_path):
       os.remove(pbxproj_json_path)

    print os.path.expanduser('~')
    pbxproj_json_gloabl = '{0}/statistic.json'.format(os.path.join(os.path.expanduser('~'),'Desktop'))
    plutil_cmd = 'plutil -convert json {0}  -o {1}'.format(pbxproj_path,pbxproj_json_path)
    commands.getoutput(plutil_cmd)
    
    #获取索引文件的内容
    pbxproj_dict = json.load(open(pbxproj_json_path))
    pbxproj_objects = pbxproj_dict['objects']
    pbxproj_objects_gloabl = pbxproj_objects
    
    os.remove(pbxproj_json_path)
    if os.path.exists(pbxproj_json_gloabl):
       os.remove(pbxproj_json_gloabl)
    for series in pbxproj_objects.values():
            if series['isa'] == 'PBXProject':
               parse_targets(series)
               break
