#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import glob
import os
import time
import hashlib
import shutil
import os.path
import filecmp
import stdio
import exifread
import uuid
import re
from datetime import datetime

SHOW_ERRORS = True
SHOW_OUTPUT = True
SHOW_COUNTER = True

# SOURCE_PATH = '/home/zorze/tmp/img_s/'
SOURCE_PATH = 'x:\\img_s\\'
# TARGET_PATH = '/home/zorze/tmp/img_t/'
TARGET_PATH = 'x:\\img_t\\'
DB_PATH = 'x:\\'
SLASH = '\\'

def get_files(source_path):
    b = ['mpg','tif','nef', 'jpg', 'mov', 'tiff', 'mp4', 'avi'] #,'MPG','TIF','NEF', 'JPG', 'MOV', 'TIFF', 'MP4', 'AVI']
    xl = []
    for n in range(0, len(b)):
        for name in sorted(glob.glob(source_path + '**/*.' + b[n], recursive=True)):
            xl.append(name)
    return xl

def init_sqlite(db_path:str):
    db_filename = db_path + 'capa.db'
    print('Database:', db_filename)
    db_is_new = not os.path.exists(db_filename)
    if db_is_new:
        try:
            print('Creating db')
            db = sqlite3.connect(db_filename)
            cursor = db.cursor()
            cursor.execute('CREATE TABLE `files_hash` (\n'
                           '	`file_hash`	TEXT NOT NULL UNIQUE,\n'
                           '	`f_count`	INTEGER NOT NULL DEFAULT 0,\n'
                           '	PRIMARY KEY(`file_hash`));')
            db.commit()
            cursor.execute('''CREATE TABLE `file_log` (
            	                `log_uuid`	TEXT NOT NULL UNIQUE,
            	                `log_hash`	TEXT NOT NULL,
            	                `log_source`	TEXT NOT NULL,
            	                `log_target`	TEXT NOT NULL,
            	                `log_datetime`	TEXT NOT NULL ,
            	                `log_size`	INTEGER NOT NULL DEFAULT 0 );''')
            db.commit()
            cursor.execute('''CREATE TABLE errors_log(
                            err_id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
                            err_file text NOT NULL,
                            err_desc text NOT NULL,
                            err_datetime text NOT NULL,
                            err_file_hash text) ''')
            db.commit()
            cursor.execute('''CREATE UNIQUE INDEX errors_log_err_id_uindex ON errors_log (err_id);''')
            db.commit()
            
            print('Done!')
        except Exception as e:
            # Roll back any change if something goes wrong
            db.rollback()
            raise e
        finally:
            # Close the db connection
            db.close()
    else:
        print('DB already exists!')

def exifdate_date(exif_date):
    dum = str(exif_date).split()
    return dum[0].replace(':', '-')

def ensure_dir(tp):
    if not os.path.exists(tp):
        os.makedirs(tp)
        
def run_(target_path, source_path):
    xl = get_files(source_path)
    source_files_cnt = len(xl)
    

    ensure_dir(target_path + 'no_exif_dump' + SLASH)
    # print(' files:', "{0:6d}".format(source_files_cnt), file=open(target_path + "copy.log", "a"))
    # print('------------------------------------------------', file=open(target_path + "copy.log", "a"))
    ensure_dir(target_path + 'no_exif_dump' + SLASH)
    print(' Files:', "{0:6d}".format(source_files_cnt))
    print('------------------------------------------------')
    copy_file_cnt = 0
    error_1_cnt = 0
    error_2_cnt = 0
    error_3_cnt = 0
    error_4_cnt = 0
    
    for n in xl:
        flag, f_hash = is_new_file(n)
        # print('is new file responce',flag,f_hash)
        if flag:
            # print('process file:', n)
            f = open(n, 'rb')
            tags = exifread.process_file(f)
            nome = str(n)[str(n).rfind(SLASH) + 1:]
            # print('file', n, nome)
            try:
                exif_dir = exifdate_date(tags['EXIF DateTimeOriginal'])
                t_dir = target_path + exif_dir + SLASH
                ensure_dir(t_dir)
                t_file = nome
                if stdio.file_ok(t_dir + t_file):
                    # print('file exist', n, ' - ', nome)
                    if not filecmp.cmp(n, t_dir + t_file):
                        t_file = clean_file_name(t_file, ui=True)
                        shutil.copy2(n, t_dir + t_file)
                        copy_file_cnt += 1
                        error_1_cnt += 1
                        add_error(n, 'file duplicate com EXIF but diferent', f_hash, target_path)
                        add_new_file(f_hash, target_path)
                        add_file_in_log(n, t_dir + t_file, f_hash, target_path)
                        if SHOW_COUNTER:
                            print(' cópia:' + "{0:6d}".format(copy_file_cnt) + "{0:6d}".format(error_1_cnt)
                                  + "{0:6d}".format(error_2_cnt)
                                  + "{0:6d}".format(error_3_cnt)
                                  + "{0:6d}".format(error_4_cnt)
                                  , sep=' ', end='\r', flush=True)
                    else:
                        error_4_cnt += 1
                        add_error(n, 'file duplicate com EXIF but equal', f_hash, target_path)
        
                else: # OK
                    # if SHOW_OUTPUT:
                    #     print(' cópia:', 'O.K.      ', '[' + exif_dir + ']', t_file)
                    # print(' cópia:', 'O.K.      ', '[' + exif_dir + ']', t_file, file=open(target_path + "copy.log", "a"))
                    shutil.copy2(n, t_dir + t_file)
                    copy_file_cnt += 1
                    add_new_file(f_hash, target_path)
                    add_file_in_log(n, t_dir + t_file, f_hash, target_path)
                    if SHOW_COUNTER:
                        print(' cópia:' + "{0:6d}".format(copy_file_cnt) + "{0:6d}".format(error_1_cnt)
                              + "{0:6d}".format(error_2_cnt)
                              + "{0:6d}".format(error_3_cnt)
                              + "{0:6d}".format(error_4_cnt)
                              , sep=' ', end='\r', flush=True)
            except KeyError:
                # f_date = time.strftime('%Y-%m-%d', time.gmtime(os.path.getmtime(n)))
                f_date = get_date_from_filename(n)              
                exif_dir = target_path + f_date + SLASH
                # não tem exifread vai para exif_dir)
                ensure_dir(exif_dir)
                if stdio.file_ok(exif_dir + nome):
                    shutil.copy2(n, target_path + 'no_exif_dump' + SLASH + nome)
                    error_2_cnt += 1
                    add_error(n, 'file duplicate without EXIF and dublou', f_hash, target_path)
                    add_new_file(f_hash, target_path)
                    add_file_in_log(n, target_path + 'no_exif_dump' + SLASH + nome, f_hash, target_path)
                    if SHOW_COUNTER:
                        print(' cópia:' + "{0:6d}".format(copy_file_cnt) + "{0:6d}".format(error_1_cnt)
                              + "{0:6d}".format(error_2_cnt)
                              + "{0:6d}".format(error_3_cnt)
                              + "{0:6d}".format(error_4_cnt)
                              , sep=' ', end='\r', flush=True)
                        
                else:
                    # print(' cópia:', 'sem EXIF  ', '[' + f_date + ']', nome)
                    shutil.copy2(n, exif_dir + nome)
                    # print(' cópia:', 'sem EXIF  ', '[' + f_date + ']', nome, file=open(target_path + "copy.log", "a"))
                    # print(' cópia:', 'sem EXIF  ', '[' + f_date + ']', nome, file=open(target_path + "error.log", "a"))
                    copy_file_cnt += 1
                    error_3_cnt += 1
                    add_error(n, 'file witout EXIF', f_hash, target_path)
                    add_new_file(f_hash, target_path)
                    add_file_in_log(n, exif_dir + nome, f_hash, target_path)
                    # if SHOW_OUTPUT:
                    #     print(' cópia:', 'sem EXIF  ', '[' + f_date + ']', nome)
                    if SHOW_COUNTER:
                        print(' cópia:' + "{0:6d}".format(copy_file_cnt) + "{0:6d}".format(error_1_cnt)
                              + "{0:6d}".format(error_2_cnt)
                              + "{0:6d}".format(error_3_cnt)
                              + "{0:6d}".format(error_4_cnt)
                              , sep=' ', end='\r', flush=True)
        else:
            pass
            
    # print(file=open(target_path + "copy.log", "a"))
    # print('------------------------------------------------', file=open(target_path + "copy.log", "a"))
    # print('source:', "{0:6d}".format(source_files_cnt), file=open(target_path + "copy.log", "a"))
    # print('  copy:', "{0:6d}".format(copy_file_cnt), file=open(target_path + "copy.log", "a"))
    print()
    print('------------------------------------------------')
    print('source:', "{0:6d}".format(source_files_cnt))
    print('  copy:', "{0:6d}".format(copy_file_cnt))
    print('error1:', "{0:6d}".format(error_1_cnt))
    print('error2:', "{0:6d}".format(error_2_cnt))
    print('error3:', "{0:6d}".format(error_3_cnt))
    print('error4:', "{0:6d}".format(error_4_cnt))


def clean_file_name(a, ui=False):
    c = re.sub('[() ]', '_', a)
    if ui:
        b = str(uuid.uuid4())[9:13].upper()
        c = c.replace('.', '_' + b + '.')
        c = c.replace('__', '_')
    return c


def get_date_from_filename(a):
    xl = os.path.basename(a)
    # print('input:', xl)
    b = xl.replace(' ', '')
    b = b.replace('T', '')
    b = b.replace('_', '')
    b = b.replace('-', '')
    # print('b:',b)
    import re
    c = re.sub(r'[^0-9]+', '', b, re.I)
    d = c[:8]
    # print(d)
    if is_date(d):
        # print('date found...', d, '...')
        return d[:4] + '-' + d[4:6] + '-' + d[6:8]
    else:
        return 'no_exif_dump'
    

def is_date(date_text):
    try:
        if date_text != datetime.strptime(date_text, "%Y%m%d").strftime('%Y%m%d'):
        # if date_text != datetime.strptime(date_text, "%Y-%m-%d").strftime('%Y-%m-%d'):
            raise ValueError
        return True
    except ValueError:
        return False


def run_processor(source, target):
    print('Organize photos 3.0 ©Jorge Espiridião')
    print(' from:', source)
    print('   to:', target)
    
    t0 = time.time()
    run_(target, source)
    t1 = time.time()
    print('  time:', t1 - t0)
    # print('  time:', t1 - t0, file=open(target + "copy.log", "a"))

def is_new_file(file_name:str):
    bc = get_sha256(file_name)
    db = sqlite3.connect(DB_PATH + 'capa.db')
    cursor = db.cursor()
    cursor.execute('SELECT * FROM files_hash where file_hash=? ', (bc,))
    xl = cursor.fetchone()
    cursor.close()
    db.close()
    if xl is None:
        return True, bc
    else:
        return False, bc

def add_new_file(file_hash, target):
    db = sqlite3.connect(DB_PATH + 'capa.db')
    cursor = db.cursor()
    cursor.execute('insert into files_hash (file_hash, f_count) values(?, 0) ', (file_hash,))
    db.commit()

def add_file_in_log(f_source, f_target, f_hash, target,f_size=0):
    d = datetime.now().strftime('%d-%m-%Y %H:%M' )
    db = sqlite3.connect(DB_PATH + 'capa.db')
    cursor = db.cursor()
    cursor.execute('insert into file_log (log_uuid, log_hash, log_source, log_target, log_size, log_datetime) values(?,?,?,?,?,?) ',
                   ( str(uuid.uuid4()), f_hash, f_source, f_target, f_size, d))
    db.commit()

def add_error(s_file, e_desc, f_hash, target):
    d = datetime.now().strftime('%d-%m-%Y %H:%M' )
    db = sqlite3.connect(DB_PATH + 'capa.db')
    cursor = db.cursor()
    cursor.execute('insert into errors_log (err_file, err_desc, err_datetime, err_file_hash) values (?,?,?,?)',
                       (s_file, e_desc, d, f_hash))
    db.commit()
    
def get_sha256(file_name):
    sha256_hash = hashlib.sha256()
    with open(file_name, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
           sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


def main():
    init_sqlite(DB_PATH)
    run_processor(SOURCE_PATH, TARGET_PATH)


if __name__ == '__main__':
    main()


