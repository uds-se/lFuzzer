
import os
import shutil
import urllib.request

tools = [
    "samples/<tool>"
]

dependencies = [
    "modules/trace-taint/sources/dependencies/",
]

dependencynames = [
    "commons-cli-1.3.1.jar",
    "gson-2.8.0.jar",
    "javax.json-1.1.2.jar",
    "javax.json-api-1.1.2.jar",
    "msgpack-core-0.8.12.jar"
]

# contains
files = [
    ("https://repo1.maven.org/maven2/commons-cli/commons-cli/1.3.1/commons-cli-1.3.1.jar", os.path.join("scripts", "downloads", "commons-cli-1.3.1.jar"), "dependency", "commons-cli-1.3.1.jar"),
    ("https://repo1.maven.org/maven2/com/google/code/gson/gson/2.8.0/gson-2.8.0.jar", os.path.join("scripts", "downloads", "gson-2.8.0.jar"), "dependency", "gson-2.8.0.jar"),
    ("https://repo1.maven.org/maven2/org/glassfish/javax.json/1.1.2/javax.json-1.1.2.jar", os.path.join("scripts", "downloads", "javax.json-1.1.2.jar"), "dependency", "javax.json-1.1.2.jar"),
    ("https://repo1.maven.org/maven2/javax/json/javax.json-api/1.1.2/javax.json-api-1.1.2.jar", os.path.join("scripts", "downloads", "javax.json-api-1.1.2.jar"), "dependency", "javax.json-api-1.1.2.jar"),
    ("https://repo1.maven.org/maven2/org/msgpack/msgpack-core/0.8.12/msgpack-core-0.8.12.jar", os.path.join("scripts", "downloads", "msgpack-core-0.8.12.jar"), "dependency", "msgpack-core-0.8.12.jar"),
    ("https://gist.githubusercontent.com/KartikTalwar/3095780/raw/c2ebc18d2ce6285c19beb5aa856dda0a3224f585/tiny.c", os.path.join("scripts", "downloads", "tiny.c"), "tool", "tinyc"),
]


def download():
    """
    Download licensed files.
    """
    for file in files:
        print(file[0])
        urllib.request.urlretrieve(file[0], file[1])

def distribute():
    """
    Distribute licensed files.
    """
    for file in files:
        if file[2] == "tool":
            for tool in tools:
                filepath = os.path.join(tool.replace("<tool>", file[3]))
                print(file[1], filepath)
                shutil.copy(file[1], filepath)
        if file[2] == "dependency":
            for dep in dependencies:
                filepath = os.path.join(dep, file[3])
                print(file[1], filepath)
                shutil.copy(file[1], filepath)

if __name__ == "__main__":
    download()
    distribute()
