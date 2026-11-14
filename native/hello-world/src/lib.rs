//! Small, synchronous bootstrap ABI. It is not the future Core/Engine ABI.
use std::{panic::catch_unwind, ptr, slice, str};

const OK: u32 = 0;
const BUFFER_TOO_SMALL: u32 = 1;
const INVALID_ARGUMENT: u32 = 2;
const INVALID_UTF8: u32 = 3;
const NAME_TOO_LONG: u32 = 4;
const PANIC: u32 = 255;
const MAX_NAME_BYTES: usize = 4096;
const PREFIX: &[u8] = b"Hello, ";
const SUFFIX: &[u8] = b"! From Rust.";

/// Returns the bootstrap ABI major version. No pointers or resources are involved.
#[unsafe(no_mangle)]
pub extern "C" fn nw_hello_abi_version() -> u32 {
    1
}

/// Writes a UTF-8 greeting into caller-owned storage, or reports the required length.
/// No pointer is retained and no allocation is transferred across the boundary.
///
/// # Safety
/// `written` must be aligned and writable for one `usize`. A nonempty name must be
/// readable for `name_len` bytes. A non-null output must be writable for `capacity`
/// bytes. All three regions must be disjoint and valid for the entire call.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn nw_hello_greet(
    name: *const u8,
    name_len: usize,
    output: *mut u8,
    capacity: usize,
    written: *mut usize,
) -> u32 {
    if written.is_null() {
        return INVALID_ARGUMENT;
    }
    // SAFETY: The caller supplies an aligned writable, non-overlapping length pointer.
    unsafe { written.write(0) };
    catch_unwind(|| {
        if name_len > MAX_NAME_BYTES {
            return NAME_TOO_LONG;
        }
        if (name.is_null() && name_len != 0) || (output.is_null() && capacity != 0) {
            return INVALID_ARGUMENT;
        }
        let name = if name_len == 0 {
            &[]
        } else {
            // SAFETY: The caller guarantees readability; length is bounded above.
            unsafe { slice::from_raw_parts(name, name_len) }
        };
        if str::from_utf8(name).is_err() {
            return INVALID_UTF8;
        }
        // The bounded input makes this addition non-overflowing.
        let required = PREFIX.len() + name.len() + SUFFIX.len();
        // SAFETY: Same caller-owned length pointer validated above.
        unsafe { written.write(required) };
        if capacity < required {
            return BUFFER_TOO_SMALL;
        }
        // SAFETY: Capacity covers the complete result, output is non-null, and
        // caller-owned regions are disjoint. No bytes beyond required are written.
        unsafe {
            ptr::copy_nonoverlapping(PREFIX.as_ptr(), output, PREFIX.len());
            ptr::copy_nonoverlapping(name.as_ptr(), output.add(PREFIX.len()), name.len());
            ptr::copy_nonoverlapping(
                SUFFIX.as_ptr(),
                output.add(PREFIX.len() + name.len()),
                SUFFIX.len(),
            );
        }
        OK
    })
    .unwrap_or(PANIC)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn greet(name: &[u8], output: &mut [u8]) -> (u32, usize) {
        let mut written = 0;
        // SAFETY: Distinct live slices and an aligned local length meet the ABI contract.
        let status = unsafe {
            nw_hello_greet(
                name.as_ptr(),
                name.len(),
                output.as_mut_ptr(),
                output.len(),
                &mut written,
            )
        };
        (status, written)
    }

    #[test]
    fn unicode_nul_and_empty_round_trip() {
        assert_eq!(nw_hello_abi_version(), 1);
        for name in ["World", "世界 🦀", "", "a\0b"] {
            let expected = format!("Hello, {name}! From Rust.");
            let mut output = vec![0xcc; expected.len() + 1];
            let (status, length) = greet(name.as_bytes(), &mut output);
            assert_eq!((status, length), (OK, expected.len()));
            assert_eq!(&output[..length], expected.as_bytes());
            assert_eq!(output[length], 0xcc);
        }
    }

    #[test]
    fn short_buffer_reports_size_without_writing() {
        let mut output = [0xcc; 2];
        assert_eq!(greet(b"World", &mut output), (BUFFER_TOO_SMALL, 24));
        assert_eq!(output, [0xcc; 2]);
    }

    #[test]
    fn invalid_utf8_and_oversized_input_do_not_write() {
        let mut output = [0xcc; 32];
        assert_eq!(greet(&[0xff], &mut output), (INVALID_UTF8, 0));
        assert_eq!(
            greet(&[b'x'; MAX_NAME_BYTES + 1], &mut output),
            (NAME_TOO_LONG, 0)
        );
        assert_eq!(output, [0xcc; 32]);
        let mut boundary = vec![0; MAX_NAME_BYTES + PREFIX.len() + SUFFIX.len()];
        assert_eq!(
            greet(&[b'x'; MAX_NAME_BYTES], &mut boundary),
            (OK, boundary.len())
        );
    }

    #[test]
    fn null_arguments_and_size_query() {
        let mut written = 99;
        // SAFETY: Null pointers exercise documented validation paths; all non-null
        // pointers point to valid, disjoint storage and are used within their bounds.
        unsafe {
            assert_eq!(
                nw_hello_greet(ptr::null(), 1, ptr::null_mut(), 0, &mut written),
                INVALID_ARGUMENT
            );
            assert_eq!(written, 0);
            assert_eq!(
                nw_hello_greet(ptr::null(), 0, ptr::null_mut(), 1, &mut written),
                INVALID_ARGUMENT
            );
            assert_eq!(
                nw_hello_greet(ptr::null(), 0, ptr::null_mut(), 0, ptr::null_mut()),
                INVALID_ARGUMENT
            );
            assert_eq!(
                nw_hello_greet(ptr::null(), 0, ptr::null_mut(), 0, &mut written),
                BUFFER_TOO_SMALL
            );
            assert_eq!(written, PREFIX.len() + SUFFIX.len());
        }
    }
}
