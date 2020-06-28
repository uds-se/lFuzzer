#!/bin/bash -
# This is a helper script to download and build the correct version of llvm+clang
# for the project. It should work on most Linux and MacOSX.

die() {
    echo "error: $1" >&2
    exit 1
}

die_svn() {
    svn cleanup "$2" > /dev/null 2>&1
    echo "error: $1" >&2
    exit 1
}

need_cmd() {
    if ! command -v "$1" > /dev/null 2>&1; then
        die "required command not found: '$1'"
    fi
}

need_cmd mkdir
need_cmd svn

LLVM_VER=401
LLVM_URL=https://llvm.org/svn/llvm-project

TOOLCHAIN_DIR=./toolchains
TOOLCHAIN_BLD=${TOOLCHAIN_DIR}/build
TOOLCHAIN_NAME=llvm+clang-${LLVM_VER}

SRC_DIR=${TOOLCHAIN_BLD}/${TOOLCHAIN_NAME}
BLD_DIR=${TOOLCHAIN_BLD}/${TOOLCHAIN_NAME}_build
INSTALL_DIR=${TOOLCHAIN_DIR}/${TOOLCHAIN_NAME}

# get sources
mkdir -p "${SRC_DIR}"
svn co "${LLVM_URL}/llvm/tags/RELEASE_${LLVM_VER}/final/" "${SRC_DIR}"

while [ "$?" != 0 ]; do
  echo "restart svn co"
  svn cleanup "${SRC_DIR}" > /dev/null 2>&1
  svn co "${LLVM_URL}/llvm/tags/RELEASE_${LLVM_VER}/final/" "${SRC_DIR}"
done

svn co "${LLVM_URL}/cfe/tags/RELEASE_${LLVM_VER}/final/"  "${SRC_DIR}/tools/clang"

while [ "$?" != 0 ]; do
  echo "restart svn co"
  svn cleanup "${SRC_DIR}/tools/clang" > /dev/null 2>&1
  svn co "${LLVM_URL}/cfe/tags/RELEASE_${LLVM_VER}/final/"  "${SRC_DIR}/tools/clang"
done