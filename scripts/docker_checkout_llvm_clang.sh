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

LLVM_VER=401
LLVM_URL=https://llvm.org/svn/llvm-project

TOOLCHAIN_DIR=/home/toolchains
TOOLCHAIN_BLD=${TOOLCHAIN_DIR}/build
TOOLCHAIN_NAME=llvm+clang-${LLVM_VER}

SRC_DIR=${TOOLCHAIN_BLD}/${TOOLCHAIN_NAME}
BLD_DIR=${TOOLCHAIN_BLD}/${TOOLCHAIN_NAME}_build
INSTALL_DIR=${TOOLCHAIN_DIR}/${TOOLCHAIN_NAME}

# get sources
mkdir -p "${TOOLCHAIN_BLD}"
cd "${TOOLCHAIN_BLD}"
wget https://releases.llvm.org/4.0.1/llvm-4.0.1.src.tar.xz
tar xf llvm-4.0.1.src.tar.xz
rm llvm-4.0.1.src.tar.xz
mv "llvm-4.0.1.src" "${TOOLCHAIN_NAME}"

cd "${TOOLCHAIN_NAME}/tools/"
wget https://releases.llvm.org/4.0.1/cfe-4.0.1.src.tar.xz
tar xf cfe-4.0.1.src.tar.xz
rm cfe-4.0.1.src.tar.xz
mv cfe-4.0.1.src clang

exit 0

#while [ "$?" != 0 ]; do
#  echo "restart svn co"
#  svn cleanup "${SRC_DIR}" > /dev/null 2>&1
#  svn co "${LLVM_URL}/llvm/tags/RELEASE_${LLVM_VER}/final/" "${SRC_DIR}"
#done
#
#svn co "${LLVM_URL}/cfe/tags/RELEASE_${LLVM_VER}/final/"  "${SRC_DIR}/tools/clang"
#
#while [ "$?" != 0 ]; do
#  echo "restart svn co"
#  svn cleanup "${SRC_DIR}/tools/clang" > /dev/null 2>&1
#  svn co "${LLVM_URL}/cfe/tags/RELEASE_${LLVM_VER}/final/"  "${SRC_DIR}/tools/clang"
#done