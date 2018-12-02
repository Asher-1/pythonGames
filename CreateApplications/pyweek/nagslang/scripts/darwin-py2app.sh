#!/bin/sh
# Copyright 2009 Jeremy Thurgood <firxen@gmail.com>
# GPL - see COPYING for details
#
# Usage: darwin-py2app

GAME_NAME="nagslang"

GAME_VERSION=`sed -ne 's/VERSION_STR = "\(.*\)"/\1/p' setup.py`
BUILD_NAME="${GAME_NAME}-${GAME_VERSION}"
BUILD_FOLDER="build/${GAME_NAME}"
DMG_NAME="${BUILD_NAME}.dmg"
PY2APP_LOG="py2app.log"

BASEDIR=`pwd`

echo "=== Setting up build environment ==="

./scripts/build_unix.sh

cd ${BUILD_FOLDER}

# find data -name '*.svg' -delete

mkdir data/icons/program
for f in $(find data/icons/werewolf-sonata*); do
    cp $f $(echo $f | sed 's@werewolf-sonata@program/icon@')
done

echo ""
echo "=== Running python setup.py ==="
echo "  Werewolf Sonata version: ${GAME_VERSION}"
echo "  Writing log to ${PY2APP_LOG}"

python setup.py py2app >${PY2APP_LOG} 2>&1

echo ""
echo "=== Removing useless cruft that just takes up space ==="
echo ""

for dir in docs examples tests; do
    find "dist/" -path "*/Resources/lib/*/pygame/${dir}/*" -delete
done

echo "=== Adding magic icon ==="
echo ""

cp data/icons/werewolf-sonata.icns dist/${GAME_NAME}.app/Contents/Resources/

echo "=== Copying libchipmunk ==="
echo ""

cp dist/${GAME_NAME}.app/Contents/Resources/lib/python*/pymunk/libchipmunk.dylib dist/${GAME_NAME}.app/Contents/MacOS/

echo "=== Building DMG ==="
echo ""

cd ${BASEDIR}

pwd
rm dist/${DMG_NAME} > /dev/null

echo -e "For some reason the game starts without a foreground window. Click on the icon in the dock (or minimize and restore from the menu) to get it back.\n\nIf this doesn't work, please let me (<firxen@gmail.com>) know, especially if you have any ideas about how to fix it.\n\nYou should also be able to use the unix tarball available at the same place you got this dmg.\n\nThanks." > ${BUILD_FOLDER}/dist/IMPORTANT\ NOTE.txt

hdiutil create -volname ${GAME_NAME} -srcfolder ${BUILD_FOLDER}/dist/*.app/ -srcfolder ${BUILD_FOLDER}/dist/IMPORTANT\ NOTE.txt dist/${DMG_NAME}

echo ""
echo "=== Done ==="
echo ""
du -sh dist/* | sed 's/^/   /'
echo ""

