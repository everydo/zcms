#!/usr/bin/python
""" generate .frs metadata

How to use:

  dotfrs path title

"""
import sys
import os
import datetime

DIR_METADATA = """{
    "main": {
        "left_col": "",
        "hidden_keys": [
            "img",
            "index.rst"
        ],
        "keys": [
        ],
        "contenttype": "Folder"
    },
    "dublin": {
        "title": "%s",
        "description": "%s",
        "creators": [
            "%s"
        ],
        "created": "%s"
    }
}
"""

FILE_METADATA = """{
    "main": {
        "contenttype": "Document"
    },
    "dublin": {
        "title": "%s",
        "description": "%s",
        "creators": [
            "%s"
        ],
        "created": "%s"
    }
}
"""

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 2:
       print 'Usage: dotfrs.py rst_path creator [title description]'
    else:
       path, creator = args[:2]
       title, description = '', ''
       created = str(datetime.datetime.now())
       if len(args) > 2:
           title = args[2]
       else:
           for line in open(path).readlines()[:2]:
               if not line.startswith('=='):
                   title = line.strip()
                   break
       if len(args) > 3:
           description = args[3]

       path = os.path.abspath(path)

       dir_name = os.path.dirname(path)
       base_name = os.path.basename(path)

       dotfrspath = os.path.join(dir_name, '.frs')
       basenamefrspath = os.path.join(dir_name, '.frs', base_name)
       metadatafrspath = os.path.join(dir_name, '.frs', base_name, 'metadata.json')

       if not os.path.exists(dotfrspath):
           os.mkdir(dotfrspath)
       if not os.path.exists(basenamefrspath):
           os.mkdir(basenamefrspath)

       if os.path.isdir(path):
           template = DIR_METADATA
       else:
           template = FILE_METADATA

       body = template % (title, description, creator, created)
       open(metadatafrspath, 'w').write(body)
       print 'done: %s\ntitle: %s\nuser:%s\ndescription:%s\ntime:%s\n' % (metadatafrspath, title, creator,description,created)

