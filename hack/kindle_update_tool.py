#!/usr/bin/python
# Kindle Firmware Update tool v0.11
# Copyright (c) 2009-2010 Igor Skochinsky & Jean-Yves Avenard
# $Id: kindle_update_tool.py 6765 2010-09-18 21:16:05Z NiLuJe $
# History:
#  2009-03-10 Initial release
#  2009-10-22 Update for K2 International support
#  2009-10-30 Add conversion from gzip tar to OTA update file, add signature of files for K2 International
#  2009-11-01 Use hashlib instead of obsolete md5
#             Add ability to install package without first installing the freekindle-k2i package.
#  2009-11-03 Fix progress bar during final sequence. Add uninstaller for k2i. Fix execution flag
#  2009-11-25 Add supports for firmware 2.3
#  2009-11-26 Make it compatible with Windows NT and later
#  2010-01-24 Add DXi support
#  2010-07-08 Add DXg support
#  2010-08-23 Add K3G support
#  2010-08-26 Add K3W support
#  2010-09-08 Sign the bundle file too, to make fw 3.x happy
#  2010-09-08 Fix a tempfile leak
#  2010-09-08 Add K3G UK support
#  2010-09-08 Allow switching between FB01 MANUAL/FC02 OTA/FD03 OTA update type via a flag
#  2010-09-08 Add extracting support for FD03 OTA updates

import tarfile, gzip, array, hashlib, sys, struct
from binascii import hexlify
import os, subprocess
import random, tempfile
import getopt

## For Signed Images Only

BASE_CMD = "openssl dgst -sha256 "
CMD_SIGN = BASE_CMD + "-sign %(privkey)s -out %(outfile)s %(infile)s"
KINDLE_HACK_DIR = "/etc/uks"
KINDLE_HACK_KEYNAME = "pubprodkey01.pem"
SIGN_KEY = """
-----BEGIN RSA PRIVATE KEY-----
MIICXgIBAAKBgQDJn1jWU+xxVv/eRKfCPR9e47lPWN2rH33z9QbfnqmCxBRLP6mM
jGy6APyycQXg3nPi5fcb75alZo+Oh012HpMe9LnpeEgloIdm1E4LOsyrz4kttQtG
RlzCErmBGt6+cAVEV86y2phOJ3mLk0Ek9UQXbIUfrvyJnS2MKLG2cczjlQIDAQAB
AoGASLym1POD2kOznSERkF5yoc3vvXNmzORYkRk1eJkJuDY6yAbYiO7kDppqj4l8
wGogTpv98OMXauY8JgQj6tgO5LkY2upttukDr8uhE2z9Dh7HMZV/rDYa+9rybJus
RiAQDmF+VCzY2HirjpsSzgRu0r82NC8znNm2eGORys9BvmECQQDoIokOr0fYz3UT
SbHfD3engXFPZ+JaJqU8xayR7C+Gp5I0CgSnCDTQVgdkVGbPuLVYiWDIcEaxjvVr
hXYt2Ac9AkEA3lnERgg0RmWBC3K8toCyfDvr8eXao+xgUJ3lNWbqS0HtwxczwnIE
H49IIDojbTnLUr3OitFMZuaJuT2MtWzTOQJBAK6GCHU54tJmZqbxqQEDJ/qPnxkM
CWmt1F00YOH0qGacZZcqUQUjblGT3EraCdHyFKVT46fOgdfMm0cTOB6PZCECQQDI
s5Zq8HTfJjg5MTQOOFTjtuLe0m9sj6zQl/WRInhRvgzzkDn0Rh5armaYUGIx8X0K
DrIks4+XQnkGb/xWtwhhAkEA3FdnrsFiCNNJhvit2aTmtLzXxU46K+sV6NIY1tEJ
G+RFzLRwO4IFDY4a/dooh1Yh1iFFGjcmpqza6tRutaw8zA==
-----END RSA PRIVATE KEY-----
"""

NEW_KEY = """
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDJn1jWU+xxVv/eRKfCPR9e47lP
WN2rH33z9QbfnqmCxBRLP6mMjGy6APyycQXg3nPi5fcb75alZo+Oh012HpMe9Lnp
eEgloIdm1E4LOsyrz4kttQtGRlzCErmBGt6+cAVEV86y2phOJ3mLk0Ek9UQXbIUf
rvyJnS2MKLG2cczjlQIDAQAB
-----END PUBLIC KEY-----
"""

INSTALL_SCRIPT = """
#!/bin/sh

_FUNCTIONS=/etc/rc.d/functions
[ -f ${_FUNCTIONS} ] && . ${_FUNCTIONS}

. /etc/sysconfig/mntus

#Restore original Kindle signing key
cat > /etc/uks/pubprodkey01.pem <<EOF
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCxfpiZ1dbdSOgrikqXD6lESUrD
5l52nN50iMh2vDcmW/FzkPDv0eRf1ci6w3ifhmHwqDK9OYNnowPapzUHAiHukXjW
rOC3fZYzgAxzIPN4NyUw369zFK2AALZnXptc68D/xxtZ94porf+kLtw/4vF2NhHs
XtchrpvID+Jhkor8MQIDAQAB
-----END PUBLIC KEY-----
EOF

update_progressbar 100

return 0
"""

if sys.hexversion >= 0x3000000:
  print "This script is incompatible with Python 3.x. Please install Python 2.6.x from python.org"
  sys.exit(2)

def dm(s):
  arr = array.array('B',s)
  for i in xrange(len(arr)):
    b = arr[i]^0x7A
    arr[i] = (b>>4 | b<<4)&0xFF
  return arr.tostring()

def md(s): #opposite of dm
  arr = array.array('B',s)
  for i in xrange(len(arr)):
    b = arr[i]
    b = (b>>4 | b<<4)&0xFF
    arr[i] = b^0x7A
  return arr.tostring()

def s_md5(s): #return md5 in string format
  m = hashlib.md5()
  m.update(s)
  return hexlify(m.digest())

def runCommand(cmd):
    """wrapper to simplify the execution of external programs.
    @param cmd: Command line to be executed
    @type cmd: string

    @return: tuple (exit code, stdout, stderr).
    @rtype: tuple
    """
    ssl = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    status = ssl.wait()
    out, err = ssl.communicate()
    return status, out, err

def extract_bin(binname):
    f = open(binname, "rb")
    sig, fromVer, toVer, devCode, optional = struct.unpack("<4sIIHBx", f.read(16))

    if sig in [ "FC02","FD03" ]:
      typ="OTA update"
    elif sig=="FB01":
      typ="Manual update"
    else:
      print "Not a Kindle update file!"
      return

    print "Signature: %s (%s)"%(sig,typ)
    if sig in [ "FC02","FD03" ]:
      print "min version: %d"%(fromVer)
      print "max version: %d"%(toVer)
      print "device code: %d%d"%divmod(devCode,256)
      print "optional: "+("yes" if optional else "no")
    print "md5 of tgz: %s"%dm(f.read(32))
    if sig in [ "FC02","FD03" ]:
        f.seek(64)
    elif sig=="FB01":
        f.seek(131072)
    open(binname+".tgz","wb").write(dm(f.read()))

def add_tarfile(tarinfo, file, tar, mode=0100644):
    tarinfo.mode = mode
    tarinfo.uid = tarinfo.gid = 0
    tarinfo.uname = tarinfo.gname = "root"
    fs = open(file,'rb')
    tar.addfile(tarinfo, fs)
    fs.close()

def create_sig(keyfile, name, tar, finalname=''):
    fd , sigfile = tempfile.mkstemp()
    os.close(fd)
    cmd = CMD_SIGN % { 'privkey': keyfile,
                       'outfile': sigfile,
                       'infile': name}
    print 'cmd = %s' % cmd
    status = runCommand(cmd)
    if status[0] != 0:
        raise ValueError("Openssl failed")
    # Add signature file
    if finalname == '':
        finalname = name
    tarinfo = tar.gettarinfo(sigfile, arcname=finalname+'.sig')
    add_tarfile(tarinfo, sigfile, tar)
    os.remove(sigfile)


def make_bin(basename, filelist, type, kver, sign=0, jailbreak=0):
    fd , tgz_fname = tempfile.mkstemp()
    os.close(fd)
    tar = tarfile.open(tgz_fname,"w:gz")

    dat_list = ""

    if sign:
        fd , keyfile = tempfile.mkstemp()
        fs = os.fdopen(fd,"wb")
        fs.write(SIGN_KEY)
        fs.close()

    if jailbreak:
        random.seed()

        # Create fake symlink
        namedir = '__dir' + str(random.randint(1000,9999))
        tarinfo = tarfile.TarInfo(namedir)
        tarinfo.type = tarfile.SYMTYPE
        tarinfo.linkname = KINDLE_HACK_DIR
        tar.addfile(tarinfo)

        # Create new key
        fd , tmpfile = tempfile.mkstemp()
        fs = os.fdopen(fd,"wb")
        fs.write(NEW_KEY)
        fs.close()
        tarinfo = tar.gettarinfo(tmpfile, arcname=namedir+'/'+KINDLE_HACK_KEYNAME)
        add_tarfile(tarinfo, tmpfile, tar)
        os.remove(tmpfile)

        # Create additional install script
        nameinstall = '_install' + str(random.randint(1000,9999)) + '.sh'
        fd , tmpinstall = tempfile.mkstemp()
        fs = os.fdopen(fd,"wb")
        fs.write(INSTALL_SCRIPT)
        fs.close()
        tarinfo = tar.gettarinfo(tmpinstall, arcname=nameinstall)
        add_tarfile(tarinfo, tmpinstall, tar)
        if sign:
            create_sig(keyfile, tmpinstall, tar, finalname=nameinstall)

        # Creating extra script signature

    if sign:
        for name in filelist:
            print "calculating signature for %s" % name
            create_sig(keyfile, name, tar)

    for name in filelist:
        print "adding %s"%name
        tarinfo = tar.gettarinfo(name)
        if name.endswith(".sh"):
            fid = 129
        else:
            fid = 128
        add_tarfile(tarinfo, name, tar)

        fsize = os.path.getsize(name) / 64
        inf = open(name,"rb")
        dat_list+="%d %s %s %d %s\n"%(fid, s_md5(inf.read()), name, fsize, name+"_file")
        inf.close()

    if jailbreak:
        fsize = os.path.getsize(tmpinstall) / 64
        inf = open(tmpinstall,"rb")
        dat_list+="%d %s %s %d %s\n"%(129, s_md5(inf.read()), nameinstall, fsize, nameinstall+"_file")
        inf.close()
        os.remove(tmpinstall)

    fd , tmpdat = tempfile.mkstemp()
    fs = os.fdopen(fd,"wb")
    fs.write(dat_list)
    fs.close()
    tarinfo = tar.gettarinfo(tmpdat, arcname=basename+'.dat')
    add_tarfile(tarinfo, tmpdat, tar)

    # Sign the bundle file, too (needed since fw 3.x)
    if sign:
        print "calculating signature for bundle file"
        create_sig(keyfile, tmpdat, tar, basename+'.dat')
        os.remove(keyfile)

    os.remove(tmpdat)
    tar.close()
    convert_bin(basename, tgz_fname, type, kver)
    os.remove(tgz_fname)

def convert_bin(basename, tgz_fname, type, kver):
    print "making bin file"
    if type==3:
      BLOCK_SIZE=64
      sig = "FD03"
    elif type==2:
      BLOCK_SIZE=64
      sig = "FC02"
    else:
      BLOCK_SIZE=131072
      sig = "FB01"

    f = open(tgz_fname, "rb").read()
    of = open(basename+".bin","wb")
    #C4 1D 3C 07 C2 B5 A0 08
    header = struct.pack("<4sIIHBB", sig, 0x0, 0x7fffffff, kver, 0, 0x13) #signature, fromVer, toVer, devCode, optional
    of.write(header)
    of.write(md(s_md5(f)))
    of.write("\0"*(BLOCK_SIZE - of.tell()))
    of.write(md(f))
    of.close()
    print "output written to "+basename+".bin"

def usage():
  print """
    Kindle Firmware Update tool v0.11
    Copyright (c) 2009-2010 Igor Skochinsky & Jean-Yves Avenard
    Usage:
    kindle_update_tool.py e update_mmm.bin
      Extract a Kindle or Kindle 2 firmware update file. Outputs a .tgz file
      with decrypted content.

    kindle_update_tool.py m [flags] name file1 [file2 ...]
      Where flags is one of the following:
        --k2 , --k2i, --dx, --dxi, --dxg, --k3g, --k3w, --k3gb
      Makes a Kindle 2, Kindle 2 International, Kindle DX, Kindle DX International,
      Kindle DX Graphite, Kindle 3G or Kindle 3 WiFi OTA firmware update
      file from the list of files.
      "name" is the update file suffix (final file will be called
      update_name.bin).
      Any file with .sh extension will be marked as a shell script to be
      executed.
      Flags:
        --k2:   generate a package for Kindle 2
        --k2i:  generate a package for Kindle 2 International
        --[dx|DX]:   generate a package for Kindle DX
        --[dxi|DXi]: generate a package for Kindle DX International
        --[dxg|DXg]: generate a package for Kindle DX Graphite
        --k3g:   generate a package for Kindle 3G
        --k3w:   generate a package for Kindle 3 WiFi
        --k3gb:  generate a package for Kindle 3G UK

        Flags for Firmware 2.2 and later:
        --sign: generate signed images.
                This is required for firmware 2.2 and later.
        --ex:   the generated package will install without the need to first
                install new RSA keys to the kindle (also called jailbreaking).
                It is imperative that the install script works 100%. As should
                they fail, it could leave your kindle in a corrupted state
                preventing to install future official Amazon updates.
                BIG FAT WARNING:
                This doesn't work anymore since firmware 2.4, and thus shouldn't
                be used when generating a package for current firmwares.
                No-op when generating a package for Kindle models always using
                firmware 2.5 or later (DXg, k3g, k3w, k3gb).

        Flags for Firmware 2.5 and later:
        --[fd|FD]: generate a FD03 OTA update (instead of a FC02)
        --[fb|FB]: generate a FB01 MANUAL (recovery) update (instead of an OTA FC02).
                   Probably not working right now, but here for completeness sake.

    kindle_update_tool.py c [flags] name tarname]
      Convert a GZIPPED TAR file into a Kindle DX, Kindle 2, or
      Kindle 2 International OTA firmware update file.
      "name" is the update file suffix
      (final file will be called update_name.bin).
      Flags:
        --k2:   generate a package for Kindle 2
        --k2i:  generate a package for Kindle 2 International
        --[dx|DX]:   generate a package for Kindle DX
        --[dxi|DXi]: generate a package for Kindle DX International
        --[dxg|DXg]: generate a package for Kindle DX Graphite
        --k3g:   generate a package for Kindle 3G
        --k3w:   generate a package for Kindle 3 WiFi
        --k3gb:  generate a package for Kindle 3G UK

        Flags for Firmware 2.5 and later:
        --[fd|FD]: generate a FD03 OTA update (instead of a FC02)
        --[fb|FB]: generate a FB01 MANUAL (recovery) update (instead of an OTA FC02).
                   Probably not working right now, but here for completeness sake.
"""

if len(sys.argv)<3:
    usage()
elif sys.argv[1]=="e":
    extract_bin(sys.argv[2])
elif sys.argv[1]=="c":
    try:
        opts, args = getopt.getopt(sys.argv[2:], "", ["k2", "k2i", "DX", "dx", "dxi", "DXi", "dxg", "DXg", "k3g", "k3w", "k3gb", "fd", "FD", "fb", "FB"])
    except getopt.GetoptError:
        # print help information and exit:
        print "Unrecognised option: "
        usage()
        sys.exit(2)
    type = 2
    kver = 0
    for o, a in opts:
        if o == "--k2":
            kver = 2
        elif o == "--k2i":
            kver = 3
        elif o in [ "--DX","--dx" ]:
            kver = 4
        elif o in [ "--DXi","--dxi" ]:
            kver = 5
        elif o == "--k3g":
            kver = 6
        elif o == "--k3w":
            kver = 8
        elif o in [ "--DXg","--dxg" ]:
            kver = 9
        elif o == "--k3gb":
            kver = 10
        elif o in [ "--FD","--fd" ]:
            type = 3
        elif o in [ "--FB","--fb" ]:
            type = 1
    if len(opts) < 1 or kver == 0:
        usage()
        sys.exit(2)
    name = args[0]
    tarname = args[1]
    convert_bin("update_"+name, tarname, type, kver)
elif sys.argv[1]=="m":
    try:
        opts, args = getopt.getopt(sys.argv[2:], "", ["k2", "k2i", "DX", "dx", "DXi", "dxi", "DXg", "dxg", "k3g", "k3w", "k3gb", "sign", "ex", "fd", "FD", "fb", "FB"])
    except getopt.GetoptError:
        # print help information and exit:
        print "Unrecognised option: "
        usage()
        sys.exit(2)
    sign = 0
    jailbreak = 0
    type = 2

    kver = 0
    for o, a in opts:
        if o == "--k2":
            kver = 2
        elif o == "--k2i":
            kver = 3
        elif o in [ "--DX","--dx" ]:
            kver = 4
        elif o in [ "--DXi","--dxi" ]:
            kver = 5
        elif o == "--k3g":
            kver = 6
        elif o == "--k3w":
            kver = 8
        elif o in [ "--DXg","--dxg" ]:
            kver = 9
        elif o == "--k3gb":
            kver = 10
        elif o == "--sign":
            sign = 1
        elif o == "--ex" and kver <= 5:
            jailbreak = 1
        elif o in [ "--FD","--fd" ]:
            type = 3
        elif o in [ "--FB","--fb" ]:
            type = 1
    if len(opts) < 1 or kver == 0:
        usage()
        sys.exit(2)
    name = args[0]
    filelist = args[1:]
    make_bin("update_"+name, filelist, type, kver, sign=sign, jailbreak=jailbreak)
else:
    usage()
    sys.exit(2)
