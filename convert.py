#!/usr/bin/env python 
# -*- coding: utf8 -*-
# Usage:  python convert.py your_site_path  theme_name
# theme_name is the name under  `themes/`
# e.g.  python convery.py everydo.com   everydo.com
 
import os 
import sys
import json
import yaml
 
 
def convert_dir(path, theme, is_root=False):
    """ Convert directotries"""
    if is_root:
        jsonfile = '%s/.frs/metadata.json' % path
    else:
        jsonfile = '%s/.frs/%s/metadata.json' % \
            (os.path.dirname(path), os.path.basename(path))
    if not os.path.exists(jsonfile): return
    jsondata = json.load(open(jsonfile))
    # 1. convert left and right sidebar
    if 'left_col' in jsondata.get('main'):
        with open(os.path.join(path, '_left.rst'), 'w') as f:
            content = jsondata.get('main', {}).get('left_col', '')
            f.write(content.encode('utf8'))
    if 'right_col' in jsondata.get('main'):
        with open(os.path.join(path, '_right.rst'), 'w') as f:
            content = jsondata.get('main', {}).get('right_col', '')
            f.write(content.encode('utf8'))
    # 2. convert dirs configuraion
    yaml.safe_dump(
        {'title': jsondata.get('dublin', {}).get('title', ''),
         'description': jsondata.get('dublin', {}).get('description', ''),
         'theme_base': 'http://localhost:6543/themes/%s/' % theme,
         'theme_default': 'index.html',
         'theme': 'index.html',
         'order': jsondata.get('main', {}).get('keys', []),
         'exclude': jsondata.get('main', {}).get('hidden_keys', []),
        },
        open(os.path.join(path, '_config.yaml'), 'w'), 
        allow_unicode=True)
 
 
def convert_file(path):
    """Convert files"""
 
    jsonfile = '%s/.frs/%s/metadata.json' % \
                 (os.path.dirname(path), os.path.basename(path))
      # 转换文件头部信息
    if os.path.exists(jsonfile):
        with open(jsonfile, 'r') as f:
            jsondata = json.load(f)
        
        created = jsondata.get('dublin', {}).get('created', '')
        if created.find(':') == created.rfind(':'):
            pass
        else:
            created = created.rsplit(':', 1)[0]
        payload = yaml.safe_dump(
                {'title': jsondata.get('dublin', {}).get('title', ''),
                 'description': jsondata.get('dublin', {}).get('description', ''),
                 'creator': jsondata.get('dublin',{}).get('creators',[''])[0],
                 'created': created
                },
                allow_unicode=True, default_flow_style=False)
        format_payload = '---\n%s---\n' % payload
        if os.path.exists(path):
             with open(path, 'r+') as f:
                 linelist = f.readlines()
                 # 避免重复写入
                 if linelist[0].find('---') != -1:
                     return
                 linelist.insert(0, format_payload)
                 f.seek(0)
                 [f.write(line) for line in linelist]
 
 
def main():
    """Do sth here"""
    site_path = sys.argv[1]
    if not os.path.exists(site_path):
        print "\nNo such directotry: %s\n" % site_path
        return
    # special for site_path
    theme = sys.argv[2]
    convert_dir(site_path, theme, site_path == sys.argv[1])
    for root, dirs, files in os.walk(site_path):
        # 1.1 convert dirs
        for dir in dirs:
            dirpath = os.path.join(root, dir)
            if dirpath.find('.frs') != -1:
                continue
            convert_dir(dirpath,theme, dirpath == sys.argv[1])
        # 1.2 convert files
        for file in files:
            filepath  = os.path.join(root, file)
            if filepath.find('.frs') != -1 or not filepath.endswith('.rst'):
                continue
            convert_file(filepath)
    print "\nConvertion Done!\n"
 
if __name__ == "__main__":
    main()
