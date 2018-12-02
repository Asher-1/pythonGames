#!/bin/bash

GAME_NAME="nagslang"

MM_VERSION=`sed -ne 's/VERSION_STR = "\(.*\)"/\1/p' setup.py`
BUILD_NAME="${GAME_NAME}-${MM_VERSION}"
BUILD_FOLDER="build/${GAME_NAME}"
TARBALL_NAME="${BUILD_NAME}.tgz"

rm -rf ${BUILD_FOLDER}
mkdir -p ${BUILD_FOLDER} dist

hg archive ${BUILD_FOLDER}/ -I LICENSE.txt -I README.txt \
                            -I setup.py -I run_game.py \
                            -I run_game.pyw \
                            -I scripts -I data -I nagslang \
                            -I tools -I pyweek_upload.py \
                            -I requirements.txt

cd build
tar czf ../dist/${TARBALL_NAME} ${GAME_NAME}
