#define _GNU_SOURCE
#define _LARGEFILE64_SOURCE
#include <stdatomic.h>
#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <sys/uio.h>
#include <time.h>
#include <unistd.h>

/* A disposable verification child's filesystem fault boundary. Product native
 * assets stay unchanged. Every real libc call is forwarded, except one selected
 * write may receive ENOSPC; barriers occur after the actual successful syscall.
 * No database API, SQL, application result or managed provider is substituted. */
static pthread_once_t initialized = PTHREAD_ONCE_INIT;
static _Thread_local int inside;
static _Atomic int selected;
static char target[PATH_MAX], arm_path[PATH_MAX], audit_path[PATH_MAX], release_path[PATH_MAX];
static int mode;
static ssize_t (*next_write)(int, const void *, size_t);
static ssize_t (*next_pwrite)(int, const void *, size_t, off_t);
static ssize_t (*next_pwrite64)(int, const void *, size_t, off64_t);
static ssize_t (*next_writev)(int, const struct iovec *, int);
static int (*next_fsync)(int);
static int (*next_fdatasync)(int);
static int (*next_unlink)(const char *);
static int (*next_unlinkat)(int, const char *, int);

static void copy_environment(char *destination, const char *name) {
    const char *value = getenv(name);
    if (value && value[0] == '/' && strlen(value) < PATH_MAX) strcpy(destination, value);
}

static void initialize(void) {
    inside++;
    next_write = dlsym(RTLD_NEXT, "write");
    next_pwrite = dlsym(RTLD_NEXT, "pwrite");
    next_pwrite64 = dlsym(RTLD_NEXT, "pwrite64");
    next_writev = dlsym(RTLD_NEXT, "writev");
    next_fsync = dlsym(RTLD_NEXT, "fsync");
    next_fdatasync = dlsym(RTLD_NEXT, "fdatasync");
    next_unlink = dlsym(RTLD_NEXT, "unlink");
    next_unlinkat = dlsym(RTLD_NEXT, "unlinkat");
    copy_environment(target, "NW_B22_IO_TARGET");
    copy_environment(arm_path, "NW_B22_IO_ARM");
    copy_environment(audit_path, "NW_B22_IO_AUDIT");
    copy_environment(release_path, "NW_B22_IO_RELEASE");
    const char *value = getenv("NW_B22_IO_MODE");
    if (value && !strcmp(value, "enospc")) mode = 1;
    if (value && !strcmp(value, "after-sync")) mode = 2;
    if (value && !strcmp(value, "after-unlink")) mode = 3;
    if (value && !strcmp(value, "after-staging-write")) mode = 4;
    if (!target[0] || !arm_path[0] || !audit_path[0]) mode = 0;
    inside--;
}

static long long monotonic_ns(void) {
    struct timespec value;
    if (clock_gettime(CLOCK_MONOTONIC, &value)) return -1;
    return (long long)value.tv_sec * 1000000000LL + value.tv_nsec;
}

static void audit(const char *event, const char *operation, int descriptor) {
    char buffer[384];
    int count = snprintf(buffer, sizeof(buffer),
        "{\"event\":\"%s\",\"operation\":\"%s\",\"tid\":%ld,\"fd\":%d,\"monotonicNs\":%lld}\n",
        event, operation, syscall(SYS_gettid), descriptor, monotonic_ns());
    int file = (int)syscall(SYS_openat, AT_FDCWD, audit_path, O_CREAT | O_APPEND | O_WRONLY | O_CLOEXEC, 0600);
    if (file >= 0) {
        if (count > 0 && (size_t)count < sizeof(buffer)) (void)syscall(SYS_write, file, buffer, (size_t)count);
        (void)syscall(SYS_fsync, file);
        (void)syscall(SYS_close, file);
    }
}

static int choose(void) {
    if (atomic_load(&selected) || access(arm_path, F_OK)) return 0;
    int expected = 0;
    return atomic_compare_exchange_strong(&selected, &expected, 1);
}

static int descriptor_matches(int descriptor) {
    char link[64], filename[PATH_MAX + 1];
    int length = snprintf(link, sizeof(link), "/proc/self/fd/%d", descriptor);
    if (length <= 0 || (size_t)length >= sizeof(link)) return 0;
    ssize_t count = readlink(link, filename, PATH_MAX);
    if (count < 0 || count >= PATH_MAX) return 0;
    filename[count] = 0;
    size_t target_length = strlen(target), filename_length = strlen(filename);
    if (mode == 4 && target_length && target[target_length - 1] == '/')
        return !strncmp(filename, target, target_length) && filename_length >= 5 && !strcmp(filename + filename_length - 5, ".part");
    return !strcmp(filename, target);
}

static int unlink_matches(const char *filename) {
    size_t length = strlen(target);
    if (length && target[length - 1] == '/')
        return !strncmp(filename, target, length) && filename[length] && !strchr(filename + length, '/');
    size_t target_length = strlen(target), filename_length = strlen(filename);
    if (mode == 4 && target_length && target[target_length - 1] == '/')
        return !strncmp(filename, target, target_length) && filename_length >= 5 && !strcmp(filename + filename_length - 5, ".part");
    return !strcmp(filename, target);
}

static int fail_write(int descriptor, const char *operation) {
    if (mode != 1 || !descriptor_matches(descriptor) || !choose()) return 0;
    audit("injected-libc-enospc", operation, descriptor);
    errno = ENOSPC;
    return 1;
}

static void barrier(const char *operation, int descriptor) {
    audit("completed-filesystem-call-held", operation, descriptor);
    long long start = monotonic_ns();
    struct timespec interval = {0, 1000000};
    while (release_path[0] && access(release_path, F_OK)) {
        if (monotonic_ns() - start > 60000000000LL) {
            audit("barrier-timeout", operation, descriptor);
            return;
        }
        nanosleep(&interval, NULL);
    }
    audit("barrier-released", operation, descriptor);
}

ssize_t write(int descriptor, const void *buffer, size_t length) {
    if (inside) return syscall(SYS_write, descriptor, buffer, length);
    pthread_once(&initialized, initialize);
    if (fail_write(descriptor, "write")) return -1;
    ssize_t result = next_write ? next_write(descriptor, buffer, length) : syscall(SYS_write, descriptor, buffer, length);
    int error = errno;
    if (result > 0 && mode == 4 && descriptor_matches(descriptor) && choose()) barrier("write", descriptor);
    errno = error; return result;
}

ssize_t pwrite(int descriptor, const void *buffer, size_t length, off_t offset) {
    if (inside) return syscall(SYS_pwrite64, descriptor, buffer, length, offset);
    pthread_once(&initialized, initialize);
    if (fail_write(descriptor, "pwrite")) return -1;
    ssize_t result = next_pwrite ? next_pwrite(descriptor, buffer, length, offset) : syscall(SYS_pwrite64, descriptor, buffer, length, offset);
    int error = errno;
    if (result > 0 && mode == 4 && descriptor_matches(descriptor) && choose()) barrier("pwrite", descriptor);
    errno = error; return result;
}

ssize_t pwrite64(int descriptor, const void *buffer, size_t length, off64_t offset) {
    if (inside) return syscall(SYS_pwrite64, descriptor, buffer, length, offset);
    pthread_once(&initialized, initialize);
    if (fail_write(descriptor, "pwrite64")) return -1;
    ssize_t result = next_pwrite64 ? next_pwrite64(descriptor, buffer, length, offset) : syscall(SYS_pwrite64, descriptor, buffer, length, offset);
    int error = errno;
    if (result > 0 && mode == 4 && descriptor_matches(descriptor) && choose()) barrier("pwrite64", descriptor);
    errno = error; return result;
}

ssize_t writev(int descriptor, const struct iovec *buffers, int count) {
    if (inside) return syscall(SYS_writev, descriptor, buffers, count);
    pthread_once(&initialized, initialize);
    if (fail_write(descriptor, "writev")) return -1;
    ssize_t result = next_writev ? next_writev(descriptor, buffers, count) : syscall(SYS_writev, descriptor, buffers, count);
    int error = errno;
    if (result > 0 && mode == 4 && descriptor_matches(descriptor) && choose()) barrier("writev", descriptor);
    errno = error; return result;
}

int fsync(int descriptor) {
    if (inside) return (int)syscall(SYS_fsync, descriptor);
    pthread_once(&initialized, initialize);
    int result = next_fsync ? next_fsync(descriptor) : (int)syscall(SYS_fsync, descriptor);
    int error = errno;
    if (!result && mode == 2 && descriptor_matches(descriptor) && choose()) barrier("fsync", descriptor);
    errno = error; return result;
}

int fdatasync(int descriptor) {
    if (inside) return (int)syscall(SYS_fdatasync, descriptor);
    pthread_once(&initialized, initialize);
    int result = next_fdatasync ? next_fdatasync(descriptor) : (int)syscall(SYS_fdatasync, descriptor);
    int error = errno;
    if (!result && mode == 2 && descriptor_matches(descriptor) && choose()) barrier("fdatasync", descriptor);
    errno = error; return result;
}

int unlink(const char *filename) {
    if (inside) return (int)syscall(SYS_unlink, filename);
    pthread_once(&initialized, initialize);
    int result = next_unlink ? next_unlink(filename) : (int)syscall(SYS_unlink, filename);
    int error = errno;
    if (!result && mode == 3 && unlink_matches(filename) && choose()) barrier("unlink", -1);
    errno = error; return result;
}

int unlinkat(int directory, const char *filename, int flags) {
    if (inside) return (int)syscall(SYS_unlinkat, directory, filename, flags);
    pthread_once(&initialized, initialize);
    char absolute[PATH_MAX + 1] = {0};
    if (filename[0] == '/' && strlen(filename) < PATH_MAX) strcpy(absolute, filename);
    int result = next_unlinkat ? next_unlinkat(directory, filename, flags) : (int)syscall(SYS_unlinkat, directory, filename, flags);
    int error = errno;
    if (!result && mode == 3 && absolute[0] && unlink_matches(absolute) && choose()) barrier("unlinkat", directory);
    errno = error; return result;
}
