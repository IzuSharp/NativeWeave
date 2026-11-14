#ifndef NATIVEWEAVE_HELLO_H
#define NATIVEWEAVE_HELLO_H
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Bootstrap ABI 1. C calling convention. Lengths are bytes; no NUL terminator.
 * Status: 0 OK, 1 buffer too small, 2 invalid argument, 3 invalid UTF-8,
 * 4 name exceeds 4096 bytes, 255 caught Rust panic.
 * name is borrowed; output and written are caller-owned. Regions must be valid
 * and disjoint. written is required. (NULL, 0) queries required output length.
 * Validation errors leave output untouched and written zero. Capacity errors
 * return the required length. Ignore written/output after a caught panic.
 * No pointers are retained, allocations transferred, callbacks or threads started.
 * Panic containment does not cover abort/OOM or invalid foreign pointers.
 */
uint32_t nw_hello_abi_version(void);
uint32_t nw_hello_greet(const uint8_t *name, size_t name_len,
                        uint8_t *output, size_t capacity, size_t *written);
#ifdef __cplusplus
}
#endif
#endif
