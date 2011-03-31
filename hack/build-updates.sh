#! /bin/sh
#
# $Id: build-updates.sh 7361 2011-03-07 20:31:58Z NiLuJe $
#

HACKNAME="dev-key"
PKGNAME="${HACKNAME##*link}"
PKGVER="0.1.N"

KINDLE_MODELS="k2 k2i dx dxi dxg k3g k3w k3gb"

# Archive custom directory
tar --exclude="*.svn" -cvzf ${HACKNAME}.tar.gz ../src/${HACKNAME}

for model in ${KINDLE_MODELS} ; do
	# Prepare our files for this specific kindle model...
	ARCH=${PKGNAME}_${PKGVER}_${model}

	# Build install update
	./kindle_update_tool.py m --${model} --sign ${ARCH}_install install.sh developer.keystore ${HACKNAME}.tar.gz

	# Build uninstall update
	./kindle_update_tool.py m --${model} --sign ${ARCH}_uninstall uninstall.sh
done

# Remove custom directory archive
rm -f ${HACKNAME}.tar.gz

# Move our updates :)
mv -f *.bin ../
