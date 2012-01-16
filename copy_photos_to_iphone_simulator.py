#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
import glob
import sys

def show_help():
  usage = """
USAGE:
  
  % copy_photos_to_iphone_simulator.py <src_photos_dir> [dst_sdk_version]

  src_photos_dir: コピー元写真のあるパス
  dst_sdk_version: コピー先sdk version。allで全て。指定無しだと最近のバージョンのみをコピー先に指定。
  
"""
  print usage

class iOSSDKNotFoundException(Exception): pass

def recent_sdk_version():
  int_versions = []
  versions = ios_sdk_versions()
  # Comma Separated Version
  for csv in [v.split('.') for v in versions]:
    result = 0
    i = 1
    for v in csv:
      # 4桁ベースだけど0除算面倒なのであとで桁下げしてる
      digit = 10000 / (10 ** i)
      result += digit * int(v)
      i += 1
    result /= 10
    int_versions.append(result)
  int_versions.sort()
  recent_int_version = int_versions[-1]
  recent_version = '.'.join([s for s in str(recent_int_version)])
  # Ver.a.b.c の cが無いケースへの対処
  versions.sort()
  versions.reverse()
  for version in versions:
    if recent_version.startswith(version):
      return version
  raise iOSSDKNotFoundException

def ios_sdk_versions():
  home = os.environ['HOME']
  simulators_dir = os.path.join(home, 'Library', 'Application Support', 'iPhone Simulator')
  path = '%s/[0-9].*' % simulators_dir
  versions = [s.split('/')[-1] for s in glob.glob(path)]
  return versions

def _simulator_media_base(ios_sdk_version):
  home = os.environ['HOME']
  return os.path.join(home, 'Library', 'Application Support', 'iPhone Simulator', ios_sdk_version, 'Media')
 
def is_photo_data_exist(ios_sdk_version):
  if os.path.exists(os.path.join(_simulator_media_base(ios_sdk_version), 'PhotoData')):
    return True
  return False
 
def has_jpeg_image(d):
  for x in os.listdir(d):
    (y, ext) = os.path.splitext(x)
    if ext and ('.jpg' == ext.lower() or '.jpeg' == ext.lower()):
      return True
  return False
 
def clear_media(ios_sdk_version):
  shutil.rmtree(os.path.join(_simulator_media_base(ios_sdk_version), 'DCIM'), True)

def clear_photodata(ios_sdk_version):
  shutil.rmtree(os.path.join(_simulator_media_base(ios_sdk_version), 'PhotoData'), True)
 
def copy_to_simulator(d, ios_sdk_version):
  dest_dir = os.path.join(_simulator_media_base(ios_sdk_version), 'DCIM', '100APPLE')
  if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)
  c = 0
  for x in os.listdir(d):
    (y, ext) = os.path.splitext(x)
    if ext and ('.jpg' == ext.lower() or '.jpeg' == ext.lower()):
      c += 1
      shutil.copy(os.path.join(d, x), os.path.join(dest_dir, "IMG_%04d.jpg" % (c)))


if __name__ == '__main__':
  print "iOS SDKs = %s" % ios_sdk_versions()
  print "recent_sdk_version = %s" % recent_sdk_version()
  
  sdk_versions = []
  if len(sys.argv) == 1:
    show_help()
    exit()
  elif len(sys.argv) == 2:
    sdk_versions.append(recent_sdk_version())
  elif len(sys.argv) == 3:
    if sys.argv[2] == 'all':
      sdk_versions = ios_sdk_versions()
    else:
      sdk_versions.append(sys.argv[2])
    
  photo_srcdir = sys.argv[1]
  print 'srcdir = %s' % photo_srcdir
  for ios_sdk_version in sdk_versions:
    clear_photodata(ios_sdk_version)
    print "copy to simulator ver.%s ..." % ios_sdk_version
    copy_to_simulator(photo_srcdir, ios_sdk_version)
