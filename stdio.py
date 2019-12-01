#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import platform
import sys
import string
import time
import datetime
from random import randrange
import urllib.request, urllib.error, urllib.parse
import glob
from operator import itemgetter, attrgetter


def read_config_file(file_name):
    lines = []
    try:
        f = open(file_name, "r")
        try:
            lines = f.readlines()
        finally:
            f.close()
    except IOError:
        print ('erro ao ler ini')
    return lines

def ini_file_to_dic(lines):
    dic = {}
    if not lines == []:
        for n in lines:
            dum = n.split('=')
            if len(dum) > 1:
                dic[dum[0]] = dum[1].strip('\n')
            else:
                dic[dum[0].strip('\n')] = None
        dic['error'] = False
    else:
        dic['error'] = True     

    return dic
               
def print2file(name,content):
    f = open(name,'w')
    print(content, file=f)

def read_file(file_name, mode = 1):
    try:
        f = open(file_name, "r")
        try:
            if mode == 1:
                # lines into a list.
                toto = f.readlines()
            elif mode == 2:
                # Read the entire contents of a file at once.
                toto = f.read()
            elif mode == 3:
                # OR read one line at a time.
                toto= f.readline()
            
        finally:
            f.close()
    except IOError:
        toto = 'error ao carregar ficheiro:' + file_name

    return toto

def log_write(file_name,content):
    d = datetime.datetime.now().strftime("%Y.%b.%d %H:%M:%S")
    with open(file_name, "a") as myfile:
        myfile.write(d + ': ' + content + '\n')


def wipe(path):
    # fp = open(path, "wb")
    # for i in range(os.path.getsize(path)):
    #     fp.write("*")
    #     fp.close()
    # os.unlink(path)

    with open(path, 'wb') as fout:
        fout.write(os.urandom(randrange(1309,7483)))

def debug(*args):
    print ('------------------ debug -------------------')
    for arg in args:
        print (arg)

    print ('------------------  fim  -------------------')

def debug_long(title,**kwargs):
    print ('------------------ debug -------------------')
    print (title)
    for key in kwargs:
        print((key, kwargs[key]))

    print ('------------------  fim  -------------------')

def int_format(number,sep = ' '):
    s = '%d' % number
    groups = []
    while s and s[-1].isdigit():
        groups.append(s[-3:])
        s = s[:-3]
    return s + sep.join(reversed(groups))

def float_format(number,sepi = ' ',sepf = ','):
    """ o dois é a precisão do numero flutuante """
    try:
        dum = str(number).split('.')
        # print dum
        toto = int_format(int(dum[0]),sepi) + sepf + dum[1][:2]
    except:
        return '0' + sepf + '00'
    return toto

def sort_files_by_last_modified(files):
    """ Given a list of files, return them sorted by the last
         modified times. """
    fileData = {}
    for fname in files:
        fileData[fname] = os.stat(fname).st_mtime

    fileData = sorted(list(fileData.items()), key = itemgetter(1))
    return fileData

def internet_on():
    try:
        response=urllib.request.urlopen('http://google.com',timeout=1)
        return True
    except urllib.error.URLError as err: pass
    return False

def delete_file(path,echo = False):
    if os.path.isfile(path):
        if echo:
            os.remove(path)

def file_ok(file):
    if os.path.exists(file):
        return True
    else:
        return False

def dir_ok(path, create = True):
    if os.path.isdir(path):
        pass
    else:
        if create:
            os.makedirs(path)

def last_file(path):
    files_by_date = sort_files_by_last_modified(path)
    if not files_by_date:
        toto = -1
    else:
        toto = files_by_date[0][0]
    return toto


def cp(source,target, echo = False):
    try:
        if echo:
            main.form.PRINT(source)
        shutil.copy2(source,target)
    except Exception:
        if echo:
            main.form.PRINT('File not found:' + str(source))

def hashfile(afile, hasher, blocksize=65536):

    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.digest()



def zip_file(filename):
    import gzip
    dum = filename + '.gz'
    dum = dum[:dum.rfind('.xml')]
    f_in = open(filename, 'rb')
    f_out = gzip.open(filename +'.gz', 'wb')
    f_out.writelines(f_in)
    f_out.close()
    f_in.close()

    if not file_ok(dum + '.gz'):
        os.rename(filename + '.gz',dum + '.gz',)
    return dum + '.gz'


def get_encode(t):
    import magic
    m = magic.open(magic.MAGIC_MIME_ENCODING)
    m.load()

    encoding = m.buffer(t)
    print('magic encoding',encoding)