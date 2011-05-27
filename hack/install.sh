#!/bin/sh
# diff OTA patch script

_FUNCTIONS=/etc/rc.d/functions
[ -f ${_FUNCTIONS} ] && . ${_FUNCTIONS}


MSG_SLLVL_D="debug"
MSG_SLLVL_I="info"
MSG_SLLVL_W="warn"
MSG_SLLVL_E="err"
MSG_SLLVL_C="crit"
MSG_SLNUM_D=0
MSG_SLNUM_I=1
MSG_SLNUM_W=2
MSG_SLNUM_E=3
MSG_SLNUM_C=4
MSG_CUR_LVL=/var/local/system/syslog_level

logmsg()
{
    local _NVPAIRS
    local _FREETEXT
    local _MSG_SLLVL
    local _MSG_SLNUM

    _MSG_LEVEL=$1
    _MSG_COMP=$2

    { [ $# -ge 4 ] && _NVPAIRS=$3 && shift ; }

    _FREETEXT=$3

    eval _MSG_SLLVL=\${MSG_SLLVL_$_MSG_LEVEL}
    eval _MSG_SLNUM=\${MSG_SLNUM_$_MSG_LEVEL}

    local _CURLVL

    { [ -f $MSG_CUR_LVL ] && _CURLVL=`cat $MSG_CUR_LVL` ; } || _CURLVL=1

    if [ $_MSG_SLNUM -ge $_CURLVL ]; then
        /usr/bin/logger -p local4.$_MSG_SLLVL -t "ota_install" "$_MSG_LEVEL def:$_MSG_COMP:$_NVPAIRS:$_FREETEXT"
    fi

    [ "$_MSG_LEVEL" != "D" ] && echo "ota_install: $_MSG_LEVEL def:$_MSG_COMP:$_NVPAIRS:$_FREETEXT"
    [ -d /mnt/us/dev-key ] && echo "ota_install: $_MSG_LEVEL def:$_MSG_COMP:$_NVPAIRS:$_FREETEXT" >> /mnt/us/dev-key/install.log
}

if [ -z "${_PERCENT_COMPLETE}" ]; then
    export _PERCENT_COMPLETE=0
fi

update_percent_complete()
{
    _PERCENT_COMPLETE=$((${_PERCENT_COMPLETE} + $1))
    update_progressbar ${_PERCENT_COMPLETE}
}

[ -d /mnt/us/dev-key ] || mkdir /mnt/us/dev-key
[ -d /var/local/java/keystore ] || mkdir -p /var/local/java/keystore
logmsg "I" "update" "Update started"
update_percent_complete 2

logmsg "I" "update" "Keystore before installion:"
ls -lha /var/local/java/keystore/* >> /mnt/us/dev-key/install.log 2>&1
md5sum /var/local/java/keystore/* >> /mnt/us/dev-key/install.log 2>&1

update_percent_complete 33
if [ -f /var/local/java/keystore/developer.keystore ]; then
	BAKFILE=developer.keystore-`date +%s`
	cp -f /var/local/java/keystore/developer.keystore /var/local/java/keystore/$BAKFILE
	/usr/local/bin/java -jar mergekeystore.jar /var/local/java/keystore/developer.keystore kindlenote.keystore
	logmsg "I" "update" "Keys installed, backup in $BAKFILE"
else
	/usr/local/bin/java -jar mergekeystore.jar /var/local/java/keystore/developer.keystore kindlenote.keystore
	logmsg "I" "update" "Keys installed"
fi

logmsg "I" "update" "Keystore after installion:"
ls -lha /var/local/java/keystore/* >> /mnt/us/dev-key/install.log 2>&1
md5sum /var/local/java/keystore/* >> /mnt/us/dev-key/install.log 2>&1

update_percent_complete 66
if [ `date +%Y%m` -lt 201104 ]; then
logmsg "I" "update" "Date if too old, fixing it"
date 010100592013.30 >> /mnt/us/dev-key/install.log
hwclock -w
logmsg "I" "update" "Date set to 1 Jan 2013";
fi

logmsg "I" "update" "done"
update_progressbar 100

return 0
