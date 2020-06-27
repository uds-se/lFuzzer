import os
import sys
import subprocess
from io import BytesIO
from random import shuffle

max_exec = 1000000000
subject_flags = sys.argv[1]
PUT = "subject"


counter = 0
files = list()
filesfolders = ["../findings/queue/", "../findings/hangs/"]
for filesfolder in filesfolders:
    for f in os.listdir(filesfolder):
        if f.startswith("id:"):
            starttime = os.path.getctime(os.path.join(filesfolder, f))
            files.append((starttime, os.path.join(filesfolder, f)))
files = sorted(files, key=lambda x: x[0])
starttime = files[0][0]
endtime = 0
current_out = ""
#shuffle(files)
valid_files = list()
valid_inputs = list()
with open("valid_inputs.txt", "w") as output_file:
    for f in files:
        file = f[1]
        # print(f)
        print("File %d of %d" % (counter, len(files)))
        counter += 1
        print(str(file))
        inpt = ""
        with open(file, encoding="latin-1") as inputfile:
            try:
                inpt = inputfile.read()
            except UnicodeDecodeError:
                print("No valid Unicode in file %s" % file)
                inpt = "File has no valid unicode encoding: %s" % file
        print(repr(inpt))
        # print("Before Cleaning: %s" % repr(input))
        # input = input.replace("\0", "")
        # print("After cleaning: %s" % repr(input))
        try:
            ps = subprocess.Popen(('cat', str(file)), stdout=subprocess.PIPE)
            output = subprocess.call([f'./{PUT}'] + subject_flags.split(" "), timeout=10, stdin=ps.stdout)
        except subprocess.TimeoutExpired:
            print("Timed out.")
            output = 0
        if output == 0:
            valid_inputs.append(inpt)
            gentime = f[0] - starttime
            output_file.write("Generation Time: %d\n" % gentime)
            output_file.write("File: %s\n" % str(file))
            output_file.write(repr(inpt) + "\n\n")
            valid_files.append(f)

        if counter == max_exec:
            break

cov_info = None
valid_cov_increase_counter = 0
with open("coverage.csv", "w") as cov_file:
    for f in valid_files:
        file = f[1]
        try:
            ps = subprocess.Popen(('cat', str(file)), stdout=subprocess.PIPE)
            output = subprocess.call([f'./{PUT}.cov'] + subject_flags.split(" "), timeout=10, stdin=ps.stdout)
        except subprocess.TimeoutExpired:
            print("Timed out.")
            output = 0
        tmp_cov_info = subprocess.check_output(["gcovr", "--branches", "-s", "-r", "."], encoding="utf-8")
        tmp_cov_info = tmp_cov_info.split("branches: ")[1].split("% ")[0]
        if tmp_cov_info != cov_info:
            valid_cov_increase_counter += 1
            cov_info = tmp_cov_info
            cov_file.write("%s, %s\n" % (tmp_cov_info,float(f[0]) - starttime))
print("\nValid inputs that increase coverage: %d\n" % valid_cov_increase_counter)

os.system("gcovr -r . --branches --html --html-details -o coverage.html")

# print(current_out)
# print(endtime - starttime)
