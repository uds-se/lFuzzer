#!/bin/sh

SUBJECT=$1
SUBJECT_FLAGS=$2
LINKER_FLAGS=$3
rm *.html *.gcda *.gcno *.txt subject subject.cov
gcc ${SUBJECT}.c -o subject -ldl -lm ${LINKER_FLAGS}
gcc -fprofile-arcs -ftest-coverage ${SUBJECT}.c -o subject.cov -ldl -lm ${LINKER_FLAGS}
python3 eval.py "${SUBJECT_FLAGS}" False > log.txt
