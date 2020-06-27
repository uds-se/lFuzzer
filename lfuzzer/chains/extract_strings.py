import sys


def extract(lines):
    for line in lines:
        if line.startswith("@.str"):
            stripped = line[line.find('"'):line.rfind('"') + 1]
            if stripped.endswith('\\00"'):
                stripped = stripped[:-4] + '"'
            stripped = stripped.replace("\\", "\\x")
            # correct if a \\ is in the string
            stripped = stripped.replace("\\x\\x", "\\\\")
            print(stripped)



if __name__ == "__main__":
    with open(sys.argv[1], "r") as bcfile:
        extract(bcfile.readlines())
