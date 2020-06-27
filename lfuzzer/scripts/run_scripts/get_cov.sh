#!/bin/sh

SUBJECT=$1
CURRENTDIR=$2
SUBJECT_FLAGS=$3
LINKER_FLAGS=$4
cd /home/lfuzzer/chains
python3 coverage.py -p ${CURRENTDIR}/${SUBJECT}.c -f="${SUBJECT_FLAGS}" -lf="${LINKER_FLAGS}" >> ${CURRENTDIR}/log.txt 2>&1
