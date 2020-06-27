#!/usr/bin/env python3
"""
Script for building, running and deleting the lFuzzer docker container.
"""
import subprocess
import sys
import argparse
import os


llvm_dockerfile = "Dockerfile.llvm"
lfuzzer_dockerfile = "Dockerfile.lfuzzer"
llvm_image = "lfuzzer_llvm:401"
lfuzzer_image = "lfuzzer_lfuzzer:latest"
container_name = "lfuzzer_container"

def build():
    """
    Builds the container by first building the llvm container and then consecutively building the lFuzzer container
    :return:
    """
    proc = subprocess.run(["docker", "image", "inspect", llvm_image], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        # get the llvm sources
        os.chdir("./scripts/")
        proc = subprocess.run(["sh", "docker_checkout_llvm_clang.sh"])
        os.chdir("..")
        if proc.returncode != 0:
            print("Downloading LLVM via SVN did not finish correctly. Check command line for further information.")
        # build llvm image
        proc = subprocess.run(["docker", "build", "-t", llvm_image, "-f", llvm_dockerfile, "."])

    # build lfuzzer image
    if proc.returncode != 0:
        print("LLVM image was not properly built. Check output for details.")
        exit(1)
    print("Building lFuzzer container.")
    # proc = subprocess.run(["docker", "build", "--no-cache", "-t", lfuzzer_image, "-f", lfuzzer_dockerfile, "."])
    proc = subprocess.run(["docker", "build", "-t", lfuzzer_image, "-f", lfuzzer_dockerfile, "."])
    if proc.returncode != 0:
        print("lFuzzer image was not properly built. Check output for details.")
        exit(1)


def rebuild():
    """
        Deletes the lfuzzer images including all containers and data and rebuilds it from scratch.
        """
    inpt = input(
        "Do you want to delete the lfuzzer image including all containers and experiment data and rebuild it? [yes/no]: ")
    if inpt == "yes":
        proc = subprocess.run(["docker", "rm", container_name])
        if proc.returncode != 0:
            print("lFuzzer container was not properly deleted. Check output for details.")
        proc = subprocess.run(["docker", "image", "rm", lfuzzer_image])
        if proc.returncode != 0:
            print("lFuzzer image was not properly deleted. Check output for details.")
        build()
    else:
        print("No image will be deleted. Stopping...")
        exit(0)


def start():
    """
    Starts the lfuzzer container.
    :return:
    """
    proc = subprocess.run(["docker", "image", "inspect", lfuzzer_image], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        inpt = input("lFuzzer image does not exist. Do you want to build it now (takes around an hour)? [y/n]: ")
        if inpt == "y":
            build()
        else:
            print("No image will be built. Stopping...")
            exit(0)
    print("Starting lFuzzer docker container.")
    # TODO check if container is already running
    is_there = container_name in str(subprocess.run(["docker", "ps", "-a"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout)
    is_running = container_name in str(subprocess.run(["docker", "ps"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout)
    if not is_there:
        print("Container does not exist. Container will be created and started and bash will be attached.")
        subprocess.run(["docker", "run", "-dt", "--name", container_name, lfuzzer_image])
        subprocess.run(["docker", "start", container_name])
        subprocess.run(["docker", "exec", "-it", container_name, "/bin/bash"])
        return
    elif is_there and not is_running:
        # if the container exists but is not running
        print("Already existing container will be started and bash will be attached.")
        subprocess.run(["docker", "start", container_name])
        subprocess.run(["docker", "exec", "-it", container_name, "/bin/bash"])
        return
    elif is_there and is_running:
        print("Container is already running! Attached second bash to running container.")
        subprocess.run(["docker", "exec", "-it", container_name, "/bin/bash"])
    else:
        print("Docker claims the container does not exist but is running. Something is going wrong.")
        exit(1)



def delete():
    """
    Deletes the lfuzzer and llvm images including all containers and data.
    """
    inpt = input("Do you want to delete the lfuzzer and llvm image including all containers and experiment data? [yes/no]: ")
    if inpt == "yes":
        proc = subprocess.run(["docker", "rm", container_name])
        if proc.returncode != 0:
            print("lFuzzer container was not properly deleted. Check output for details.")
        proc = subprocess.run(["docker", "image", "rm", lfuzzer_image])
        if proc.returncode != 0:
            print("lFuzzer image was not properly deleted. Check output for details.")
        proc = subprocess.run(["docker", "image", "rm", llvm_image])
        if proc.returncode != 0:
            print("llvm image was not properly deleted. Check output for details.")
    else:
        print("No image will be deleted. Stopping...")
        exit(0)


def stop():
    """
    Stops the lFuzzer docker container.
    :return:
    """
    inpt = input("Container will be stopped, all running experiments will be aborted (already generated data should will not be deleted). Are you sure? [y/n]: ")
    if inpt == "y":
        print("Stopping container...")
        proc = subprocess.run(["docker", "stop", container_name])
        if proc.returncode != 0:
            print("Could not stop the container. Check output.")
            exit(1)
        print("Stopped")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="lFuzzer Docker Wrapper")
    parser.add_argument('-b', "--build", action='store_true',
                        help="Builds the llvm image and consecutively the lFuzzer image. Takes about an hour.")
    parser.add_argument('-a', "--attach", action='store_true',
                        help="Runs the built container. Builds it on demand if not existing (takes about an hour to build).",)
    parser.add_argument('-d', "--delete", action='store_true',
                        help="Deletes the containers and the images. Containers must be stopped before deleting.")
    parser.add_argument('-s', "--stop", action='store_true',
                        help="Stops the running container, stopping all running experiments.")
    parser.add_argument('-r', "--rebuild", action='store_true',
                        help="Deleted the lFuzzer image and container including all experiment data and builds it from scratch. The LLVM image will be kept.")
    args = parser.parse_args(sys.argv[1:])

    if args.build:
        build()
    elif args.attach:
        start()
    elif args.delete:
        delete()
    elif args.stop:
        stop()
    elif args.rebuild:
        rebuild()
    else:
        print("Exactly one flag must be set.")
        parser.print_help()
        exit(1)