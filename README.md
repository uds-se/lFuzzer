lFuzzer 
========

General Information
-------------------

This package contains lFuzzer, presented in the paper [Learning Input Tokens for Effective Fuzzing](https://publications.cispa.saarland/3098/). We published the experiment results as well as the original experiment setup in the ACM library alongside with the paper (link TBA). This repository only contains lFuzzer itself.

In case of any questions, feel free to contact: bjoern.mathis (at) cispa.saarland.

Installation/Download
---------------------

Choose a machine to conduct the experiments on. lFuzzer should run properly on a computer with 4 CPU cores or more.

Connecting to the Container
---------------------------

1.  Install `Docker` and `Python 3` on your host machine (tested with Python 3.7.7)
2.  Clone this repository to the machine at which you want to conduct the experiments on.
3.  Start docker.
4.  Install the image by typing: `./lfuzzer-docker-wrapper.py -b` (the first installation takes some time since we first need to download and compile LLVM in a docker image and then install all tools in the lFuzzer image which is based on the LLVM image). Please assign at least 3 GB of RAM to docker, otherwise the compilation of LLVM might run out of memory.
5.  Once the container is installed as an image, you can connect to its bash: `./lfuzzer-docker-wrapper.py -a`.
6.  \[Optional\] If you want to connect other terminal windows to the container, you can use `./lfuzzer-docker-wrapper.py -a` again.

The container is now ready for running experiments and will not terminate if you disconnect from the bash. For stopping the container (and terminating all experiments), type: `./lfuzzer-docker-wrapper.py -s`

Running Experiments and Adding Subjects
---------------------------------------

**Make sure you did all steps under [Connecting to the Container](#connecting-to-the-container).**

Some error messages might appear during evaluation. Here a list of errors that are common, **and can be ignored**:

*   `rm: cannot remove <some_file>: No such file or directory` (the scripts clean the folders before running the experiments, if the folder does not contain previous results, the removal fails).
*   Errors printed by the test subjects, e.g. `syntax error` by tinyc.
*   For small runtimes the token extraction and seed input generation of lFuzzer might not finish, hence the consecutive start of afl will not happen leading to missing files in the afl folder when extracting coverage and other analysis results.

What **should not be ignored** are all compilation and linker errors (from python, java, and gcc) as well as notifications that a software tool cannot be found (e.g. java, python, gcc, and gcovr)! While lFuzzer runs, you should see the python script `chains.py` or `afl` running in the task manager (e.g. `htop`).

In the container, go to `/home/lfuzzer/`. Now you can do several things:

*   [Run lFuzzer on the sample subject `tinyc`.](#run-lfuzzer-on-tinyc)
*   [Run lFuzzer on a subject of your choice.](#run-lfuzzer-on-a-subject-of-your-choice)

Run lFuzzer on tinyc
--------------------

If you want to run lFuzzer on tinyc, do the following:

1.  In the container, go to `/home/lfuzzer/`.
2.  Use the script to run experiments by typing `./run_on_subject -p samples/tinyc/tiny.c -t 24h`. This runs lFuzzer on tinyc for 24 hours.

The specified timeout only defines the raw fuzzing time, instrumentation and compilation as well as result collection is done before (respectively after) fuzzing and adds up to the specified execution time. Hence, **expect runtimes that are up to 1 hour longer than the specified runtime** (mostly the overhead is around 20 minutes; larger programs take longer).

See [Collecting results](#collecting-results) to collect the evaluation results.

Run lFuzzer on a Subject of Your Choice
---------------------------------------

Disclaimer:
Due to compilation limitations, **only subjects that consist of one C file can be instrumented (and thus analyzed)**. 
In many cases though, it may be possible to simply concatenate the C files and compile them as one. 
We are currently preparing scripts that make it possible to also instrument subjects consisting of several C files. 
The limitation is solely an engineering one: currently the instrumentation pipeline cannot handle LLVM bitcode files, 
in the near future we will make new instrumentation scripts available that will be able to instrument bitcode files. 
Then one can use [wllvm](https://github.com/travitch/whole-program-llvm) to create one LLVM bitcode file from the 
source files which can be instrumented and compiled into an executable.

**lFuzzer requires the subject to report via the exit code if a given input is syntactically valid or not. The subject should return an exit code of 0 for syntactically valid inputs and a non-zero exit code (preferably 1) for syntactically invalid values.**

If you want to evaluate your own subject with lFuzzer, you need to perform the following steps:

1.  In the container, create a folder in `/home/lfuzzer/samples/` and put the subject's `*.c` and possibly `*.h` file in it.
2.  Now you can run the subject by using the run script: `./run_on_subject.py -p <path_to_subject> -t <timeout> -f="<program-flags>" -I/path/to/include -llibrary -L/path/to/library`. The parameters have the following meaning, `-p` and `-t` are required:
    *   `-p`: Path to the program under test.
    *   `-t`: Timeout in seconds (s), minutes (m), hours (h), days (d). See [timeout](https://linux.die.net/man/1/timeout) command for further information.
    *   `-f`: Flags for the program under test, e.g. if the program is started as follows: `./program -a -b test`, then the flag to the script would be `-f="-a -b test"`. The fuzzing input is still given via stdin.
    *   `-I`: Compiler/Linker flag as used when compiling the program on the command line. The given value will be used when instrumenting and compiling the program under test.
    *   `-l`: Compiler/Linker flag as used when compiling the program on the command line. The given value will be used when instrumenting and compiling the program under test.
    *   `-L`: Compiler/Linker flag as used when compiling the program on the command line. The given value will be used when instrumenting and compiling the program under test.

Collecting Results
------------------

Each subject folder contains raw, human readable results as text, html or csv. Those results can be read as follows (a subject folder is for example: `/home/lfuzzer/samples/tinyc`):

*   `coverage.csv`: Contains the branch coverage achieved with the syntactically valid inputs generated by lFuzzer before it switched to afl. Contains two columns: the first column contains the coverage as percentage, the second column the time in seconds lFuzzer was executed until this coverage was achieved (i.e. until the input was produced that increased the coverage). Assume the following data is present in the csv:
   
    26.9, 1.7880945205688477
    
    46.9, 2.0841102600097656
    
    This means that 26.9% branch coverage was achieved by an input that was generated 1.79s after lFuzzer started running. The next input that covered new code covered 20% more branches 2.08s after lFuzzer started. Hence, both inputs covered together 46.9% of the code.
*   `coverage.<subject>.c.html`: [gcovr](https://gcovr.com/en/stable/) coverage report for the syntactically valid inputs produced by lFuzzer before it switched to afl.
*   `time.txt`: The first three lines (until "run afl") contain the runtime of lFuzzer before it switched to afl as output of the [time](http://man7.org/linux/man-pages/man1/time.1.html) command.
*   `afl/findings/`: Contains the results of the afl execution. See [afl documentation](https://lcamtuf.coredump.cx/afl/README.txt) number 7: Interpreting output.
*   `afl/eval/coverage.csv`: Analogous to the above `coverage.csv`, including afl results. For the coverage annotated with time 0.0 lFuzzer produced the input that covered the respective code before switching to afl.
*   `afl/eval/coverage.<subject>.c.html`: Analogous to the above `coverage.<subject>.c.html` including afl results.

Deletion of Results and the Docker Image
----------------------------------------

You have three choices for deletion:

1.  You can either **delete all experiment results of a subject** but keep the container intact:
    1.  Go to a subject folder in the docker container.
    2.  Run `sh clean_all.sh` in the docker container.
2.  You can also **delete the container instance, the images (including the LLVM image) and thus all data produced by lFuzzer as well as lFuzzer itself** by and running `./lfuzzer-docker-wrapper.py -d` on the host machine. All running containers of lFuzzer must be stopped (using `./lfuzzer-docker-wrapper.py -s`) before running the script. If you did not use the `./lfuzzer-docker-wrapper.py` script for generating the container or renamed the container or images consider manually deleting them.
3.  You can rebuild the lFuzzer docker container without deleting the LLVM container (which is considerably faster than building both containers again). Run `./lfuzzer-docker-wrapper.py -r` on the host machine. **This will delete the lfuzzer image and containers, including all experiment data.** All running containers of lFuzzer must be stopped (using `./lfuzzer-docker-wrapper.py -s`) before running the script. If you did not use the `./lfuzzer-docker-wrapper.py` script for generating the container or renamed the container or images consider manually deleting them.