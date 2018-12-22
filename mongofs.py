import os
import time
import config
import string_utils

class MongoDBFileSystem(object):


    def __init__(self, mongodbhandle):
        self.mongodb_handle = mongodbhandle
        self.filemeta_db = self.mongodb_handle.db.filesystem_meta
        self.filechunk_db = self.mongodb_handle.db.filesystem_datachunk
        self.create_db_index()


    def file_count(self):
        return self.filemeta_db.count()


    def create_db_index(self):
        if 'pid' not in self.filemeta_db.index_information():
            self.filemeta_db.create_index([('pid', 1)])


    def readtree(self, pid, dirbase = ""):
        fileD = self.filemeta_db.find({'pid': pid}, limit=config.MAX_FILENUM_ALLOWED)
        shownFile = []
        for item in fileD:
            fileRecord = {'pid': pid, 'filename': item['filename'], 'type': item['type'], 'data': str(item['data']),
                              'size': item['size'],
                              'mtime': item['mtime']}
            if dirbase != "":
                file_dirname = os.path.dirname(fileRecord['filename'])
                if file_dirname == dirbase:
                    shownFile.append(fileRecord)
            else:
                shownFile.append(fileRecord)

        for item in shownFile:
            if item['type'] == "file":
                item['expire'] = int(time.time()) + 86400
                item['signed'] = string_utils.hash_with_prefix(item['expire'], config.HMAC_KEY)
        print(shownFile)
        return shownFile



    def mkdir(self, pid, dirname):

        if dirname == "":
            return False

        parentpath = os.path.dirname(dirname)
        if parentpath != '':
            if self.filemeta_db.find_one({'pid': pid, 'filename': parentpath, 'type': 'dir'}) is None:
                return False

        item = self.filemeta_db.find_one({'pid': pid, 'filename':dirname})

        if item is not None:
            return False

        self.filemeta_db.insert_one(
            {'pid': pid, 'filename': dirname, 'type': 'dir', 'mtime': int(time.time()), 'data': '',
             'size': 4096})

        return True


    def delete(self, pid, filename):
        item = self.filemeta_db.find_one({'pid': pid, 'filename': filename})

        if item is None:
            return False

        if item['type'] == 'file' and item['data'] != '':
            self.filechunk_db.remove({'_id': item['data']})

        elif item['type'] == 'dir': #/Recursive Deleting
            diritems = self.readtree(pid, item['filename'])
            for diritem in diritems:
                self.delete(pid, diritem['filename'])

        self.filemeta_db.remove(item)
        return True

    def rename(self, pid, pathori, pathdst):

        if pathori == "" or pathdst == "":
            return False

        oriitem = self.filemeta_db.find_one({'pid': pid, 'filename': pathori})
        if oriitem is None:
            return False
        dstitem = self.filemeta_db.find_one({'pid': pid, 'filename': pathdst})
        if dstitem is not None:
            return False

        oriitem['filename'] = pathdst
        if oriitem['type'] == 'dir':
            fileD = self.filemeta_db.find({'pid': pid}, limit=config.MAX_FILENUM_ALLOWED)
            for f in fileD:
                tmpname = f['filename']
                if tmpname.startswith(pathori + "/"):
                    f['filename'] = tmpname.replace(pathori + "/", pathdst + "/", 1)
                    self.filemeta_db.save(f)
        self.filemeta_db.save(oriitem)
        return True

    def write(self, pid, path, content):

        if len(content) > config.MAX_FILE_SIZE or path == "":
            return False
        parentpath = os.path.dirname(path)
        if parentpath != '':
            if self.filemeta_db.find_one({'pid': pid, 'filename': parentpath, 'type': 'dir'}) is None:
                return False
        if isinstance(content, str):
            content = content.encode("utf-8")
        meta = self.filemeta_db.find_one({'pid': pid, 'filename': path, 'type': 'file'})
        if meta is None:
            tid = self.filechunk_db.insert_one({'data': content}).inserted_id
            meta = self.filemeta_db.insert_one(
                {'pid': pid, 'filename': path, 'type': 'file', 'mtime': int(time.time()), 'data': tid, 'size': len(content)})
        else:
            dataC = self.filechunk_db.find_one({'_id': meta['data']})
            if dataC is None:
                return False
            dataC['data'] = content
            self.filechunk_db.save(dataC)
            meta['mtime'] = int(time.time())
            meta['size'] = len(content)
            self.filemeta_db.save(meta)
        return True



    def read(self, pid, path):
        meta = self.filemeta_db.find_one({'pid': pid, 'filename': path})
        if meta is None:
            return None

        if meta['type'] == "dir":
            return b"dir"

        filedata = self.filechunk_db.find_one({'_id': meta['data']})
        if filedata is None:
            self.filemeta_db.remove(meta)
            return None
        return filedata['data']