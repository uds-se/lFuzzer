#!/bin/sh

RUNTIME=$1
SUBJECT=$2
SUBJECT_FLAGS=$3
LINKER_FLAGS=$4
CURRENTDIR=$(pwd)
sh clean.sh

# create afl folders and compile for afl
cd afl
mkdir tests
mkdir findings
mkdir dict
cp ../${SUBJECT}.c .
cp ../${SUBJECT}.h .
/home/programs/afl-2.52b/afl-gcc ${SUBJECT}.c -o ${SUBJECT} -ldl ${LINKER_FLAGS}
export AFL_SKIP_CPUFREQ=True
cd ..
# afl initalized

/home/lfuzzer/install/bin/trace-instr $(pwd)/${SUBJECT}.c /home/lfuzzer/samples/excluded_functions "$LINKER_FLAGS" > log.txt 2>&1
cd /home/lfuzzer/chains

CMD="{ time python3 chains.py -p ${CURRENTDIR}/${SUBJECT}.c -a False -i False -f=\"${SUBJECT_FLAGS}\" 1> /dev/null 2> error.log; echo \"run afl\"; \
cd ${CURRENTDIR}/afl; time /home/programs/afl-2.52b/afl-fuzz -i tests -o findings -x dict/ ./${SUBJECT} ${SUBJECT_FLAGS}> log.txt 2>&1; }"
echo $CMD

time timeout -k9 ${RUNTIME} bash -c "$CMD" > $CURRENTDIR/time.txt 2>&1 &
sleep ${RUNTIME}
sleep 15m

# check the coverage of pFuzzer alone
cd $CURRENTDIR
sh get_cov.sh ${SUBJECT} ${CURRENTDIR} "${SUBJECT_FLAGS}" "${LINKER_FLAGS}"

# then of afl and pFuzzer (as afl has the valid inputs of pFuzzer, those are already part of the queue)
#TODO check if afl always takes all valid inputs
cd $CURRENTDIR/afl/eval/
cp ../${SUBJECT}.c .
cp ../${SUBJECT}.h .
cp ../../../../chains/metric.py .
sh comp_run.sh ${SUBJECT} "${SUBJECT_FLAGS}" "${LINKER_FLAGS}"
