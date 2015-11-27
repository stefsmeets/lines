#!/usr/bin/env python

import os
import sys


def find_LIBTBX_BUILD():
    raise RuntimeError("Could not locate LIBTBX_BUILD directory")


def set_environment_variables_osx():
    """This is annoying. It is not possible to change the environment variables for the running process, because they are evaluated at runtime.
    Some solutions are listed in http://stackoverflow.com/a/1186194
    From http://stackoverflow.com/questions/1178094/change-current-process-environment
    The best solution seems to be to set the environment variables, and then re-run the program
    The child process will then be able to read them"""

    BASE = os.environ.get('LIBTBX_BUILD', None)
    if not BASE:
        BASE = find_LIBTBX_BUILD()
        os.environ['LIBTBX_BUILD'] = BASE
    if not BASE:
        raise ImportError("Could not locate CCTBX, please ensure that LIBTBX_BUILD environment variable points at cctbx/cctbx_build")

    # cannot use sys.path here, because it is not persistent when calling child process
    PYTHONPATH = os.environ.get("PYTHONPATH", "")
    for src in ["../cctbx_sources",
                "../cctbx_sources/clipper_adaptbx",
                "../cctbx_sources/docutils",
                "../cctbx_sources/boost_adaptbx",
                "../cctbx_sources/libtbx/pythonpath",
                "lib" ]:
        # sys.path.insert(1, os.path.abspath(os.path.join(BASE, src)))
        PYTHONPATH = os.path.abspath(os.path.join(BASE, src)) + ":" + PYTHONPATH
    os.environ["PYTHONPATH"] = PYTHONPATH

    if "DYLD_LIBRARY_PATH" not in os.environ:
        os.environ['DYLD_LIBRARY_PATH'] = os.path.join(BASE, "lib") + ":" + os.path.join(BASE, "base", "lib")
    else:
        os.environ['DYLD_LIBRARY_PATH'] += ":" + os.path.join(BASE, "lib") + ":" + os.path.join(BASE, "base", "lib")


def set_environment_variables_linux():
    """ This doesn't work =( """

    BASE = os.environ.get('LIBTBX_BUILD', None)
    if not BASE:
        BASE = find_LIBTBX_BUILD()
        os.environ['LIBTBX_BUILD'] = BASE
    if not BASE:
        raise ImportError("Could not locate CCTBX, please ensure that LIBTBX_BUILD environment variable points at cctbx/cctbx_build")

    # cannot use sys.path here, because it is not persistent when calling child process
    PYTHONPATH = os.environ.get("PYTHONPATH", "")
    for src in ["../cctbx_sources",
                "../cctbx_sources/clipper_adaptbx",
                "../cctbx_sources/docutils",
                "../cctbx_sources/boost_adaptbx",
                "../cctbx_sources/libtbx/pythonpath",
                "lib"]:
        # sys.path.insert(1, os.path.abspath(os.path.join(BASE, src)))
        PYTHONPATH = os.path.abspath(os.path.join(BASE, src)) + ":" + PYTHONPATH
    os.environ["PYTHONPATH"] = PYTHONPATH

    clib1 = os.path.join(BASE, "lib")  # ~/cctbx/cctbx_build/lib
    clib2 = "/usr/lib"

    LD_LIBRARY_PATH = os.environ.get("LD_LIBRARY_PATH", "")

    if not LD_LIBRARY_PATH:
        LD_LIBRARY_PATH = clib1 + ":" + clib2
    else:
        LD_LIBRARY_PATH = clib1 + ":" + clib2 + ":" + LD_LIBRARY_PATH

    os.environ["LD_LIBRARY_PATH"] = LD_LIBRARY_PATH

    if "LD_LIBRARY_PATH" not in os.environ:
        os.environ['LD_LIBRARY_PATH'] = os.path.join(BASE, "lib") + ":/usr/lib"  # + os.path.join(BASE, "base", "lib")
    else:
        os.environ['LD_LIBRARY_PATH'] += ":" + os.path.join(BASE, "lib") + ":/usr/lib"  # + os.path.join(BASE, "base", "lib")


def set_environment_variables_windows():
    # on Windows this seems to work though
    if 'LIBTBX_BUILD' in os.environ:
        BASE = os.environ['LIBTBX_BUILD']
    elif os.path.exists("C:\cctbx\cctbx_build"):
        BASE = "C:\cctbx\cctbx_build"
        os.environ["LIBTBX_BUILD"] = BASE
    else:
        raise ImportError("Could not locate CCTBX, please ensure that LIBTBX_BUILD environment variable points at /cctbx/cctbx_build, or CCTBX is installed in C:\cctbx\\")

    for src in ["..\cctbx_sources",
                "..\cctbx_sources\clipper_adaptbx",
                "..\cctbx_sources\docutils",
                "..\cctbx_sources\\boost_adaptbx",
                "..\cctbx_sources\libtbx\pythonpath",
                "lib"]:
        sys.path.insert(1, os.path.join(BASE, src))

    cbin = os.path.join(BASE, "bin")  # C:\cctbx\cctbx_build\bin
    clib = os.path.join(BASE, "lib")  # C:\cctbx\cctbx_build\lib

    os.environ["PATH"] += ";" + cbin + ";" + clib
