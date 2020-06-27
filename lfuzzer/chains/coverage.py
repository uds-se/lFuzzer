# coding=utf-8
# !/usr/bin/env python3
import os
import random
import subprocess

from ast import literal_eval


def run_and_trace(inpt: str, as_arg: bool, orig: bool):
    """
    Executes the C code and runs the tracing on it.
    :param inpt: The input to use to run the program.
    :param as_arg: Defines if the input is given as argument or via stdin.
    """
    global po
    if orig:
        run_subject = "%s.orig" % subject
    else:
        run_subject = "%s.cov" % subject

    exit_code = -1
    try:
        flags = args.flag.split(" ") if args.flag else []
        if as_arg:
            subprocess.call([run_subject] + flags + [inpt], timeout=10)
        else:
            ps = subprocess.Popen(('printf', '%s', inpt), stdout=subprocess.PIPE)
            exit_code = subprocess.call([run_subject] + flags, timeout=10, stdin=ps.stdout)
    except subprocess.TimeoutExpired:
        print("Timeout for: %s" + repr(inpt))
        exit_code = 0
    return exit_code



def run_loop(parentdir, arg: bool, subject: str):
    """
    Runs the program under test several times with different inputs inferred through the tainting data gained of previous
    program runs.
    :param parentdir: The folder in which the program under test lies in.
    :param arg: The flag to indicate if the value is given to the program as arg or via stdin (true for as arg)
    :param dfs: The search strategy, by default bfs is used (dfs is false).
    :return:
    """
    time = None
    for_metric = list()
    with open(os.path.join(parentdir, "valid_inputs.txt"), "r") as valid_inputs_file:
        for line in valid_inputs_file:
            if line.startswith("'") or line.startswith('"'):
                line = literal_eval(line.strip())
                if run_and_trace(line, arg, True) == 0:
                    for_metric.append((line, time))
                else:
                    print("Invalid Input: %s" % repr(line))
            elif line.startswith("Time"):
                time = line.split(": ")[1]

    cov_info = None
    valid_cov_increase_counter = 0
    with open("coverage.csv", "w") as cov_file:
        for inpt in for_metric:
            run_and_trace(inpt[0], arg, False)
            tmp_cov_info = subprocess.check_output(["gcovr", "--branches", "-s", "-r", "."], encoding="utf-8")
            tmp_cov_info = tmp_cov_info.split("branches: ")[1].split("% ")[0]
            if tmp_cov_info != cov_info:
                valid_cov_increase_counter += 1
                cov_info = tmp_cov_info
                cov_file.write("%s, %s\n" % (tmp_cov_info, inpt[1]))
    print("\nValid inputs that increase coverage: %d\n" % valid_cov_increase_counter)
    os.system("gcovr -r . --branches --html --html-details -o coverage.html")
    # os.system("grep '#####' *.gcov")


if __name__ == '__main__':
    import argparse

    rseed = int(os.environ.get('RSEED', '0'))
    random.seed(rseed)
    parser = argparse.ArgumentParser(description="Pychains")
    parser.add_argument('-p', "--program", metavar="subject", type=str,
                        help="The path to the subject as c file to run on.", required=True)
    parser.add_argument('-a', "--arg", metavar="arg", default="False", type=str,
                        help="Defines if the input is given as argument or via stdin.", required=False)
    parser.add_argument('-f', "--flag", metavar="flag", default="", type=str,
                        help="Defines the flag that is used if the program gets the argument over the command line.", required=False)
    parser.add_argument('-lf', "--linkerflags", metavar="flag", default="", type=str,
                        help="Defines the flag that is used if the program gets the argument over the command line.", required=False)
    args = parser.parse_args()
    subject = os.path.abspath(args.program)
    g_arg = args.arg.lower() == "true"
    g_parentdir = os.path.abspath(os.path.join(subject, os.pardir))
    os.chdir(g_parentdir)
    os.system("rm *.gcda *.gcno *.cov *.gcov *.orig")

    print(os.getcwd())
    print(args.linkerflags)
    # instrument program
    if args.linkerflags:
        subprocess.run(["gcc", subject, "-o", f"{subject}.orig", "-ldl", "-lm"] + args.linkerflags.split(" "))
        subprocess.run(["gcc" ,"-fprofile-arcs", "-ftest-coverage", subject, "-o" ,f"{subject}.cov", "-ldl", "-lm", "-DCOVERAGE"] + args.linkerflags.split(" "))
    else:
        subprocess.run(["gcc", subject, "-o", f"{subject}.orig", "-ldl", "-lm"])
        subprocess.run(["gcc" ,"-fprofile-arcs", "-ftest-coverage", subject, "-o" ,f"{subject}.cov", "-ldl", "-lm", "-DCOVERAGE"])

    run_loop(g_parentdir, g_arg, subject)