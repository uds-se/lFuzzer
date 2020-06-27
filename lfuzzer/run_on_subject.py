#!/usr/bin/env python3

"""
A script to run lFuzzer on a given program.
"""
import os
import shutil
import urllib.request
import subprocess
import argparse
from pathlib import Path
import sys

run_script_folder = os.path.join("/", "home", "lfuzzer", "scripts", "run_scripts")

def compile_and_run(prog: str, time: str, prog_flag: str, link_compile_flags):
    """
    Compiles the program under test and runs the fuzzer on it.
    :param prog: path to program
    :param time: runtime
    :param through_arg: flag if the program is called
    :param prog_flag:
    :param linker_flags:
    :return:
    """
    prog_path = Path(prog)
    os.chdir(prog_path.parent)
    # try to copy, if file exists ignore and assume all folders and files already exist
    try:
        shutil.copy(os.path.join(run_script_folder, "clean.sh"), ".")
        shutil.copy(os.path.join(run_script_folder, "get_cov.sh"), ".")
        shutil.copy(os.path.join(run_script_folder, "run_exp.sh"), ".")
        shutil.copytree(os.path.join(run_script_folder, "afl"), "afl")
    except FileExistsError:
        pass
    subprocess.run(["sh", "run_exp.sh", time, prog_path.name.replace(prog_path.suffix, ""), prog_flag, link_compile_flags])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="lFuzzer Docker Wrapper")
    parser.add_argument('-p', "--program", type=str, required=True,
                        help="Path to the program c file to fuzz.")
    parser.add_argument('-t', "--time", type=str, required=True,
                        help="The runtime given as timeout time. Examples: 42m for 42 minutes, 1h for one hour, 2d for two days.")
    parser.add_argument('-f', "--flag", metavar="flag", default="", type=str,
                        help="Defines the flags that are used if the program gets the argument over the command line."
                             "If -a is active, the input will be the last argument after the flags."
                             "A possible input would be: -f=\"-a --arg2 sample_arg\"", required=False)
    parser.add_argument('-I', "--include", metavar="flag", default=[], action="append", nargs='*',
                        help="Use as the -I command for a c compiler.",
                        required=False)
    parser.add_argument('-l', "--linkerflag", metavar="flag", default=[], action="append", nargs='*',
                        help="Use as the -l command for a c compiler.",
                        required=False)
    parser.add_argument('-L', "--linkerinclude", metavar="flag", default=[], action="append", nargs='*',
                        help="Use as the -L command for a c compiler.",
                        required=False)
    args = parser.parse_args(sys.argv[1:])

    print(args)

    link_compile_flags = ""
    if args.include:
        link_compile_flags += "-I" + " -I".join([el[0] for el in args.include])
    if args.linkerinclude:
        link_compile_flags += "-L" + " -L".join([el[0] for el in args.linkerinclude])
    if args.linkerflag:
        link_compile_flags += "-l" + " -l".join([el[0] for el in args.linkerflag])
    print(link_compile_flags)
    compile_and_run(args.program, args.time, args.flag, link_compile_flags)
