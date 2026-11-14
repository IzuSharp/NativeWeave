using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

[assembly: DefaultDllImportSearchPaths(DllImportSearchPath.AssemblyDirectory | DllImportSearchPath.SafeDirectories)]

namespace NativeWeave.HelloWorld;

internal static unsafe partial class NativeMethods
{
    private const string Library = "nativeweave_hello";

    [LibraryImport(Library, EntryPoint = "nw_hello_abi_version")]
    [UnmanagedCallConv(CallConvs = [typeof(CallConvCdecl)])]
    internal static partial uint AbiVersion();

    [LibraryImport(Library, EntryPoint = "nw_hello_greet")]
    [UnmanagedCallConv(CallConvs = [typeof(CallConvCdecl)])]
    internal static partial uint Greet(byte* name, nuint nameLength, byte* output, nuint capacity, out nuint written);
}
