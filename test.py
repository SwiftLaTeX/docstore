import requests
import config
class ProxyFilesystem(object):

    def __init__(self):
        self.remote_endpoint = ""
        self.s_token = ""

    def readdir(self, pid, dirname = ""):
        durl = self.remote_endpoint + "/" + pid + "/" + dirname
        headers = {'S-TOKEN': self.s_token}
        try:
            r = requests.post(durl, timeout=10, headers=headers, data={'op':'list'})
            if r.status_code == 200:
                return r.json()
            else:
                print("List failed %s" % r.text)
                return False
        except:
            print("List exeception %s" % durl)
            return False


    def mkdir(self, pid, dirname):
        durl = self.remote_endpoint + "/" + pid + "/" + dirname
        headers = {'S-TOKEN': self.s_token}
        try:
            r = requests.put(durl, timeout = 10, headers = headers)
            if r.status_code == 200:
                return True
            else:
                print("Mkdir failed %s" % r.text)
                return False
        except:
            print("Mkdir exeception %s" % durl)
            return False

    def delete(self, pid, filename):
        durl = self.remote_endpoint + "/" + pid + "/" + filename
        headers = {'S-TOKEN': self.s_token}
        try:
            r = requests.delete(durl, timeout=10, headers=headers)
            if r.status_code == 200:
                return True
            else:
                print("Delete failed %s" % r.text)
                return False
        except:
            print("Delete exeception %s" % durl)
            return False

    def rename(self, pid, pathori, pathdst):
        durl = self.remote_endpoint + "/" + pid + "/" + pathori
        headers = {'S-TOKEN': self.s_token}
        try:
            r = requests.post(durl, timeout=10, headers=headers, data={'op': 'rename', 'newpath':pathdst})
            if r.status_code == 200:
                return r.json()
            else:
                print("Rename failed %s" % r.text)
                return False
        except:
            print("Rename exeception %s" % durl)
            return False

    def write(self, pid, path, fileobj):
        durl = self.remote_endpoint + "/" + pid + "/" + path
        headers = {'S-TOKEN': self.s_token}
        files = {'file': fileobj}
        try:
            r = requests.put(durl, timeout=10, headers=headers, files= files)
            if r.status_code == 200:
                return True
            else:
                print("Upload failed %s" % r.text)
                return False
        except:
            print("Upload exeception %s" % durl)
            return False

    def read(self, pid, path, exp, sign):
        return "%s/%s/%s?expire=%s&signed=%s" % (self.remote_endpoint, pid, path, exp, sign)

ProxyFilesystem().write("abcdabcdabcdabcdabcdabcdabcdabcd", "sifjasiodfjhelloworld.txt", open("config.py", "rb"))
print(ProxyFilesystem().readdir("abcdabcdabcdabcdabcdabcdabcdabcd", ""))
print(ProxyFilesystem().read("abcdabcdabcdabcdabcdabcdabcdabcd", "sifjasiodfjhelloworld.txt", "1545606479", "8ab22851a20e607beba5083348b92884968ec51da416426fe5e63c2046274a2b"))
