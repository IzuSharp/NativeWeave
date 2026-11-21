#!/usr/bin/env python3
"""External Linux x64 child tracer: one real SQLite write receives ENOSPC.

The selected file descriptor must resolve to the disposable database, WAL or
journal. Runtime logging, private configuration, stdout and unrelated files are
never faulted. The controller arms the fault for one fixed database scenario. This
is injected syscall failure, not an exhausted physical disk or a power-loss test.
"""
from __future__ import annotations

import argparse
import ctypes
import errno
import json
import os
from pathlib import Path
import signal
import sys
import time

PTRACE_TRACEME, PTRACE_PEEKUSER = 0, 3
PTRACE_GETREGS, PTRACE_SETREGS, PTRACE_SYSCALL = 12, 13, 24
PTRACE_SETOPTIONS, PTRACE_GETEVENTMSG, PTRACE_GET_SYSCALL_INFO = 0x4200, 0x4201, 0x420E
PTRACE_O_TRACESYSGOOD, PTRACE_O_TRACEFORK, PTRACE_O_TRACEVFORK = 1, 2, 4
PTRACE_O_TRACECLONE, PTRACE_O_TRACEEXEC, PTRACE_O_EXITKILL = 8, 16, 0x100000
WAIT_ALL = 0x40000000
OPTIONS = (PTRACE_O_TRACESYSGOOD | PTRACE_O_TRACEFORK | PTRACE_O_TRACEVFORK |
           PTRACE_O_TRACECLONE | PTRACE_O_TRACEEXEC | PTRACE_O_EXITKILL)
WRITE_SYSCALLS = {1: "write", 18: "pwrite64", 20: "writev", 296: "pwritev", 328: "pwritev2"}


class Registers(ctypes.Structure):
    _fields_ = [(name, ctypes.c_ulonglong) for name in (
        "r15", "r14", "r13", "r12", "rbp", "rbx", "r11", "r10", "r9", "r8",
        "rax", "rcx", "rdx", "rsi", "rdi", "orig_rax", "rip", "cs", "eflags",
        "rsp", "ss", "fs_base", "gs_base", "ds", "es", "fs", "gs")]


LIBC = ctypes.CDLL(None, use_errno=True)
LIBC.ptrace.argtypes = [ctypes.c_ulong, ctypes.c_ulong, ctypes.c_void_p, ctypes.c_void_p]
LIBC.ptrace.restype = ctypes.c_long


def ptrace(request, pid=0, data=0, address=0):
    pointer = ctypes.cast(data, ctypes.c_void_p) if not isinstance(data, int) else ctypes.c_void_p(data)
    ctypes.set_errno(0)
    result = LIBC.ptrace(request, pid, ctypes.c_void_p(address), pointer)
    if result == -1 and ctypes.get_errno():
        raise OSError(ctypes.get_errno(), "child ptrace operation failed")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--arm-file", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--maximum-seconds", type=float, default=180)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command or os.uname().machine != "x86_64" or not sys.platform.startswith("linux"):
        parser.error("This explicit profile requires Linux x64 and an actual child command")
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    target = str(args.target.resolve())
    selected = {target: "database", target + "-wal": "wal", target + "-journal": "journal"}
    log = args.receipt.open("w", buffering=1)
    def record(event, **values):
        log.write(json.dumps({"monotonicNs": time.monotonic_ns(), "event": event, **values}, sort_keys=True) + "\n")
    record("tracer-start", profile="linux-x64-injected-enospc", errno=errno.ENOSPC)
    child = os.fork()
    if child == 0:
        log.close()
        try:
            ptrace(PTRACE_TRACEME)
            os.kill(os.getpid(), signal.SIGSTOP)
            os.execvpe(command[0], command, os.environ)
        except BaseException as error:
            os.write(2, ("b22_trace_child_failed type=" + type(error).__name__ + "\n").encode())
            os._exit(125)
    tids = {child}
    injected_tids = set()
    armed_observed = False
    fired = False
    root_result = None
    started = time.monotonic()
    # The application shares this process group. Group TERM reaches it directly;
    # the tracer must stay alive until its real cleanup/exits have been observed.
    signal.signal(signal.SIGTERM, lambda *_: None)
    signal.signal(signal.SIGINT, lambda *_: None)
    try:
        _, status = os.waitpid(child, 0)
        if not os.WIFSTOPPED(status):
            record("ptrace-unavailable", childStatus=status)
            return 125
        ptrace(PTRACE_SETOPTIONS, child, OPTIONS)
        ptrace(PTRACE_SYSCALL, child)
        while tids:
            if time.monotonic() - started > args.maximum_seconds:
                record("tracer-deadline", liveThreads=len(tids))
                raise TimeoutError("External syscall fault fixture exceeded its maximum duration")
            try:
                pid, status = os.waitpid(-1, os.WNOHANG | WAIT_ALL)
            except ChildProcessError:
                break
            if pid == 0:
                time.sleep(0.0005)
                continue
            if os.WIFEXITED(status) or os.WIFSIGNALED(status):
                tids.discard(pid); injected_tids.discard(pid)
                if pid == child:
                    root_result = os.WEXITSTATUS(status) if os.WIFEXITED(status) else 128 + os.WTERMSIG(status)
                continue
            if not os.WIFSTOPPED(status):
                continue
            tids.add(pid)
            stop_signal = os.WSTOPSIG(status)
            event = status >> 16
            delivery_signal = 0
            if event in (1, 2, 3):
                created = ctypes.c_ulonglong()
                ptrace(PTRACE_GETEVENTMSG, pid, ctypes.byref(created))
                tids.add(created.value)
            elif stop_signal == (signal.SIGTRAP | 0x80):
                information = ctypes.create_string_buffer(128)
                ptrace(PTRACE_GET_SYSCALL_INFO, pid, ctypes.byref(information), ctypes.sizeof(information))
                operation = information.raw[0]
                if operation not in (1, 2):
                    raise RuntimeError("Kernel did not identify actual syscall entry/exit")
                registers = Registers()
                ptrace(PTRACE_GETREGS, pid, ctypes.byref(registers))
                is_exit = operation == 2
                if not is_exit:
                    if not armed_observed and args.arm_file.exists():
                        armed_observed = True; record("fault-armed")
                    if armed_observed and not fired and registers.orig_rax in WRITE_SYSCALLS:
                        descriptor = int(registers.rdi)
                        try:
                            filename = os.readlink(f"/proc/{pid}/fd/{descriptor}")
                        except OSError:
                            filename = ""
                        if filename in selected:
                            syscall = WRITE_SYSCALLS[registers.orig_rax]
                            registers.orig_rax = 0xFFFFFFFFFFFFFFFF
                            ptrace(PTRACE_SETREGS, pid, ctypes.byref(registers))
                            injected_tids.add(pid); fired = True
                            record("write-suppressed", tid=pid, fd=descriptor,
                                   fileKind=selected[filename], syscall=syscall)
                elif pid in injected_tids:
                    registers.rax = ctypes.c_ulonglong(-errno.ENOSPC).value
                    ptrace(PTRACE_SETREGS, pid, ctypes.byref(registers))
                    injected_tids.remove(pid)
                    record("enospc-returned", tid=pid, errno=errno.ENOSPC)
            elif stop_signal == signal.SIGSTOP:
                ptrace(PTRACE_SETOPTIONS, pid, OPTIONS)
            elif stop_signal != signal.SIGTRAP:
                delivery_signal = stop_signal
            try:
                ptrace(PTRACE_SYSCALL, pid, delivery_signal)
            except OSError as error:
                if error.errno != errno.ESRCH:
                    raise
        record("tracer-complete", faultFired=fired, childExit=root_result,
               elapsedSeconds=time.monotonic() - started, liveThreads=len(tids))
        return root_result if root_result is not None else 125
    except BaseException as error:
        record("tracer-failed", failureType=type(error).__name__, errno=getattr(error, "errno", None))
        for pid in list(tids):
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        while True:
            try:
                os.waitpid(-1, WAIT_ALL)
            except ChildProcessError:
                break
        return 125
    finally:
        log.close()


if __name__ == "__main__":
    sys.exit(main())
