#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import shutil
import os.path
import filecmp
import stdio
import exifread
import uuid
import re
import datetime
import sys
from dateutil.parser import parse


def exifdate_date(exif_date):
    dum = str(exif_date).split()
    return dum[0].replace(':', '-')


def ensure_dir(tp):
    if not os.path.exists(tp):
        os.makedirs(tp)


def run_(target_path, source_path):
    xl = get_files(source_path)
    source_files_cnt = len(xl)
    SHOW_ERRORS = True
    SHOW_OUTPUT = True
    SHOW_COUNTER = True
    ensure_dir(target_path + 'no_exif_dump/')
    print(' files:', "{0:6d}".format(source_files_cnt), file=open(target_path + "copy.log", "a"))
    print('------------------------------------------------', file=open(target_path + "copy.log", "a"))
    ensure_dir(target_path + 'no_exif_dump/')
    print(' files:', "{0:6d}".format(source_files_cnt))
    print('------------------------------------------------')
    copy_file_cnt = 0
    error_1_cnt = 0
    error_2_cnt = 0
    error_3_cnt = 0
    error_4_cnt = 0
    for n in xl:
        print('process file:', n)
        f = open(n, 'rb')
        tags = exifread.process_file(f)
        nome = str(n)[str(n).rfind('/') + 1:]
        # print('file', n, nome)
        try:
            exif_dir = exifdate_date(tags['EXIF DateTimeOriginal'])
            t_dir = target_path + exif_dir + '/'
            ensure_dir(t_dir)
            t_file = nome
            
            if stdio.file_ok(t_dir + t_file):
                # print('file exist', n, ' - ', nome)
                if not filecmp.cmp(n, t_dir + t_file):
                    print('------------------------------------------------', file=open(target_path + "error.log", "a"))
                    print('    Ficheiro com EXIF duplicado mas diferente   ', file=open(target_path + "error.log", "a"))
                    print('          nome:', t_file, file=open(target_path + "error.log", "a"))
                    print('        origem:', n, file=open(target_path + "error.log", "a"))
                    print('          para:', t_dir, file=open(target_path + "error.log", "a"))
                    print('            PC:', copy_file_cnt, file=open(target_path + "error.log", "a"))
                    print('     corregido:', t_file, file=open(target_path + "error.log", "a"))
                    print('------------------------------------------------', file=open(target_path + "error.log", "a"))
                    t_file = clean_file_name(t_file, ui=True)
                    shutil.copy2(n, t_dir + t_file)
                    copy_file_cnt += 1
                    error_1_cnt += 1
                    if SHOW_COUNTER:
                        print(' cópia:' + "{0:6d}".format(copy_file_cnt) + "{0:6d}".format(error_1_cnt)
                              + "{0:6d}".format(error_2_cnt)
                              + "{0:6d}".format(error_3_cnt)
                              + "{0:6d}".format(error_4_cnt)
                              , sep=' ', end='\r', flush=True)
                else:
                    print('------------------------------------------------', file=open(target_path + "error.log", "a"))
                    print('    Ficheiro com EXIF duplicado mas igual   ', file=open(target_path + "error.log", "a"))
                    print('          nome:', t_file, file=open(target_path + "error.log", "a"))
                    print('        origem:', n, file=open(target_path + "error.log", "a"))
                    print('          para:', t_dir, file=open(target_path + "error.log", "a"))
                    print('            PC:', copy_file_cnt, file=open(target_path + "error.log", "a"))
                    print(' não corregido:', t_file, file=open(target_path + "error.log", "a"))
                    print('------------------------------------------------', file=open(target_path + "error.log", "a"))
                    error_4_cnt += 1
            
            else:
                # if SHOW_OUTPUT:
                #     print(' cópia:', 'O.K.      ', '[' + exif_dir + ']', t_file)
                print(' cópia:', 'O.K.      ', '[' + exif_dir + ']', t_file, file=open(target_path + "copy.log", "a"))
                shutil.copy2(n, t_dir + t_file)
                copy_file_cnt += 1
                if SHOW_COUNTER:
                    print(' cópia:' + "{0:6d}".format(copy_file_cnt) + "{0:6d}".format(error_1_cnt)
                          + "{0:6d}".format(error_2_cnt)
                          + "{0:6d}".format(error_3_cnt)
                          + "{0:6d}".format(error_4_cnt)
                          , sep=' ', end='\r', flush=True)
        except KeyError:
            # f_date = time.strftime('%Y-%m-%d', time.gmtime(os.path.getmtime(n)))
            f_date = get_date_from_filename(n)
            exif_dir = target_path + f_date + '/'
            # não tem exifread vai para exif_dir)
            ensure_dir(exif_dir)
            if stdio.file_ok(exif_dir + nome):
                print('------------------------------------------------', file=open(target_path + "error.log", "a"))
                print('        Ficheiro sem EXIF e duplicado           ', file=open(target_path + "error.log", "a"))
                print('          nome:', nome, file=open(target_path + "error.log", "a"))
                print('        origem:', n, file=open(target_path + "error.log", "a"))
                print('            PC:', copy_file_cnt, file=open(target_path + "error.log", "a"))
                print('copy 2 no_exif:', 'no_exif_dump', file=open(target_path + "error.log", "a"))
                print('------------------------------------------------', file=open(target_path + "error.log", "a"))
                shutil.copy2(n, target_path + 'no_exif_dump/' + nome)
                error_2_cnt += 1
                if SHOW_COUNTER:
                    print(' cópia:' + "{0:6d}".format(copy_file_cnt) + "{0:6d}".format(error_1_cnt)
                          + "{0:6d}".format(error_2_cnt)
                          + "{0:6d}".format(error_3_cnt)
                          + "{0:6d}".format(error_4_cnt)
                          , sep=' ', end='\r', flush=True)
            else:
                print(' cópia:', 'sem EXIF  ', '[' + f_date + ']', nome)
                shutil.copy2(n, exif_dir + nome)
                print(' cópia:', 'sem EXIF  ', '[' + f_date + ']', nome, file=open(target_path + "copy.log", "a"))
                print(' cópia:', 'sem EXIF  ', '[' + f_date + ']', nome, file=open(target_path + "error.log", "a"))
                copy_file_cnt += 1
                error_3_cnt += 1
                # if SHOW_OUTPUT:
                #     print(' cópia:', 'sem EXIF  ', '[' + f_date + ']', nome)
                if SHOW_COUNTER:
                    print(' cópia:' + "{0:6d}".format(copy_file_cnt) + "{0:6d}".format(error_1_cnt)
                          + "{0:6d}".format(error_2_cnt)
                          + "{0:6d}".format(error_3_cnt)
                          + "{0:6d}".format(error_4_cnt)
                          , sep=' ', end='\r', flush=True)
    print(file=open(target_path + "copy.log", "a"))
    print('------------------------------------------------', file=open(target_path + "copy.log", "a"))
    print('source:', "{0:6d}".format(source_files_cnt), file=open(target_path + "copy.log", "a"))
    print('  copy:', "{0:6d}".format(copy_file_cnt), file=open(target_path + "copy.log", "a"))
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
    b = xl.replace(' ', '_')
    b = b.replace('T', '_')
    c = b.split('_')
    for n in c:
        d = n.replace('-', '')
        # print(d, end='\n')
        if is_date(d):
            # print('date found...', d, '...')
            return d[:4] + '-' + d[4:6] + '-' + d[6:8]
    try:
        return time.strftime('%Y-%m-%d', time.gmtime(os.path.getmtime(a)))
    except:
        return 'no_exif_dump'


def is_date(string):
    try:
        parse(string)
        return True
    except ValueError:
        return False


def main():
    print('Organize photos 3.0 ©Jorge Espiridião')
    source_path = '/media/zorze/CA4C01E74C01CEDF/'  # 'c:/tmp/'
    target_path = '/vmware/sandra/'  # 'c:/target/'
    print(datetime.datetime.now().strftime('%d.%b.%Y %H:%M') + '\n', source_path,
          file=open(target_path + "copy.log", "a"))
    print(' from:', source_path, file=open(target_path + "copy.log", "a"))
    print('   to:', target_path, file=open(target_path + "copy.log", "a"))
    print(' from:', source_path)
    print('   to:', target_path)
    
    t0 = time.time()
    run_(target_path, source_path)
    t1 = time.time()
    print('  time:', t1 - t0)
    print('  time:', t1 - t0, file=open(target_path + "copy.log", "a"))


if __name__ == '__main__':
    main()
    # xl = ['2017-06-03 22.30.32.jpg','20171112_132509.jpg', 'Airborne_Cargo_2016-08-25T192147.jpg',
    # 'IMG_20150801_215449.jpg','20171112_135221.mp4', 'VID_20151219_173438.mp4',
    # '20160810_155058.jpg']
    # for n in xl:
    # print(n)
    # get_date_from_filename(n)
    # print('----------')
    # todo tirar data pelo nome do ficheiro
    # atenção á duplicação do rawtherapy
