#  Copyright (c) 2020-2022, Manfred Moitzi
#  License: MIT License
import time
import ezdxf

BIG_FILE = ezdxf.options.test_files_path / "CADKitSamples" / "torso_uniform.dxf"


def load_ascii():
    with open(BIG_FILE, "rt", encoding="cp1252") as fp:
        while True:
            line = fp.readline()
            if not line:
                break


def load_bytes():
    with open(BIG_FILE, "rb") as fp:
        while True:
            line = fp.readline()
            if not line:
                break


def print_result(time, text):
    print(f"Operation: {text} takes {time:.6f} s\n")


def run(func):
    start = time.perf_counter()
    func()
    end = time.perf_counter()
    return end - start


if __name__ == "__main__":
    print_result(run(load_ascii), "ascii stream reader")
    print_result(run(load_bytes), "byte stream reader")
