import string
import random
import hashlib
import re
import config

def hash_md5(str):
    hasher = hashlib.md5()
    hasher.update(str.encode('utf-8'))
    password = hasher.hexdigest()
    return password

def gen_random_string(N):
    return ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=N))

def hash_filename(name):
    hash_object = hashlib.md5(name.encode())
    return hash_object.hexdigest()


def filename_character_check(name):
    return bool(re.match(r'^[a-zA-Z\-\.\d\/\-]+$', name))

def hash_with_prefix(str, prefix):
    tmp_secret = "%s-%s-%s" % (prefix, str, prefix)
    return hash_md5(tmp_secret)


def is_valid_pidurl(name):
    if not filename_character_check(name):
        return False

    if name.count(".") > 1:
        return False

    if "//" in name:
        return False

    name_lists = name.split("/")

    if len(name_lists) <= 1:
        return False

    if len(name_lists[0]) != config.PID_LENGTH:
        return False

    return True

def split_pidurl(name):
    namelist = name.split("/")
    pid = namelist[0]
    url = ""
    for i in range(1, len(namelist)):
        url += namelist[i] + "/"
    url = url[:-1]
    return pid, url





