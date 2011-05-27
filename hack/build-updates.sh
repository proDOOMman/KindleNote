#! /bin/sh

HACKNAME="dev-key"
PKGNAME="${HACKNAME##*link}"
PKGVER="0.4.N"

KINDLE_MODELS="k2 k2i dx dxi dxg k3g k3w k3gb"

#Clearing dir with old files:
rm -f ./build/*
cp -f ../keystore/developer.keystore ./kindlenote.keystore

# Archive custom directory
#tar --exclude="*.svn" -cvzf ${HACKNAME}.tar.gz ../src/${HACKNAME}

for model in ${KINDLE_MODELS} ; do
	# Prepare our files for this specific kindle model...
	ARCH=${PKGNAME}_${PKGVER}_${model}

	# Build install update
	./kindle_update_tool.py m --${model} --sign ${ARCH}_install install.sh kindlenote.keystore mergekeystore.jar

	# Build uninstall update
	./kindle_update_tool.py m --${model} --sign ${ARCH}_uninstall uninstall.sh
done

# Remove custom directory archive
#rm -f ${HACKNAME}.tar.gz

# Move our updates :)
mv -f *.bin ./build/

rm -f kindlenote.keystore
