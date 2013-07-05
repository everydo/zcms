#!/usr/bin/env python
# -*- coding: utf8 -*-
# Usage: 
#       python clean.py  target_path
 
import os 
import shutil
import sys
 
 
def confirm(prompt=None, resp=False):
    """Confirm before delete target dirs"""
 
    if prompt is None:
        prompt = 'Confirm'
    if resp:
        prompt = '%s [%s]|%s:\t' % (prompt, 'y', 'n')
    else:
        prompt = '%s [%s]|%s:\t' % (prompt, 'n', 'y')
    
    while True:
        ans = raw_input(prompt)
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print 'Please input y or n.'
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False
 
 
def main():
    path = sys.argv[1]
    root_config = os.path.join(path, '_config.yaml')
    if not os.path.exists(root_config):
        print "\n You haven't finished the convertion job! Please check.\n"
        return 
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            dirpath = os.path.join(root, dir)
            if dirpath.endswith('.frs') and os.path.exists(dirpath):
                shutil.rmtree(dirpath)
    print "\n All .frs/ dirs has been removed"
 
 
if __name__ == "__main__":
    if confirm():
        main()
