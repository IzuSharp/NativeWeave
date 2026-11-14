using System.Text;

namespace NativeWeave.HelloWorld;

/// <summary>Creates a greeting using the precompiled Rust bootstrap library.</summary>
/// <remarks>
/// This stateless API is thread-safe. It owns no disposable resources and starts no runtime,
/// worker, callback or asynchronous operation. It demonstrates packaging and interop only.
/// Supported assets are listed in the package manifest; Linux x64 is the initial CI target.
/// </remarks>
public static class RustGreeting
{
    private const int MaxNameBytes = 4096;
    private static readonly UTF8Encoding Utf8 = new(false, true);

    /// <summary>Returns a UTF-8 greeting constructed by Rust.</summary>
    /// <param name="name">The name to greet, defaulting to World. Empty names and embedded NULs are preserved.</param>
    /// <returns>A managed string containing <c>Hello, {name}! From Rust.</c>.</returns>
    /// <exception cref="ArgumentNullException"><paramref name="name"/> is null.</exception>
    /// <exception cref="ArgumentException">The name is invalid UTF-16 or exceeds 4096 UTF-8 bytes.</exception>
    /// <exception cref="DllNotFoundException">No compatible native asset is installed for the current platform.</exception>
    /// <exception cref="BadImageFormatException">The native asset has an incompatible binary format.</exception>
    /// <exception cref="EntryPointNotFoundException">The installed native asset lacks a bootstrap export.</exception>
    /// <exception cref="InvalidOperationException">The native ABI, status, or returned length is incompatible.</exception>
    /// <remarks>
    /// Synchronous and thread-safe; cancellation and timeouts do not apply. Buffers are borrowed
    /// only during each call. Rust allocates no greeting storage. Names up to 256 UTF-8 bytes and
    /// results up to 512 bytes use stack storage; larger values allocate bounded managed arrays.
    /// Each call performs ABI validation, a size query and one write (three FFI calls), UTF-8
    /// encoding/decoding, and a result-string allocation. No zero-copy or speedup claim is made.
    /// Native libraries remain loaded for the process lifetime. This is an experimental bootstrap API.
    /// </remarks>
    public static unsafe string Greet(string name = "World")
    {
        ArgumentNullException.ThrowIfNull(name);
        // Reject oversized UTF-16 before counting, bounding validation work as well as buffers.
        if (name.Length > MaxNameBytes)
        {
            throw new ArgumentException("The name must fit in 4096 UTF-8 bytes.", nameof(name));
        }

        int length;
        try
        {
            length = Utf8.GetByteCount(name);
        }
        catch (EncoderFallbackException exception)
        {
            throw new ArgumentException("The name must contain valid UTF-16.", nameof(name), exception);
        }

        if (length > MaxNameBytes)
        {
            throw new ArgumentException("The name must fit in 4096 UTF-8 bytes.", nameof(name));
        }

        if (NativeMethods.AbiVersion() != 1)
        {
            throw new InvalidOperationException("NativeWeave.HelloWorld requires bootstrap ABI 1. Reinstall the matching package.");
        }

        Span<byte> input = length <= 256 ? stackalloc byte[length] : new byte[length];
        Utf8.GetBytes(name, input);
        fixed (byte* inputPointer = input)
        {
            uint status = NativeMethods.Greet(inputPointer, (nuint)length, null, 0, out nuint required);
            if (status != 1 || required == 0 || required > MaxNameBytes + 64)
            {
                throw new InvalidOperationException($"Rust greeting size query failed (status {status}).");
            }

            Span<byte> output = required <= 512 ? stackalloc byte[(int)required] : new byte[(int)required];
            fixed (byte* outputPointer = output)
            {
                status = NativeMethods.Greet(inputPointer, (nuint)length, outputPointer, required, out nuint written);
                if (status != 0 || written != required)
                {
                    throw new InvalidOperationException($"Rust greeting write failed (status {status}).");
                }
            }

            return Utf8.GetString(output);
        }
    }
}
