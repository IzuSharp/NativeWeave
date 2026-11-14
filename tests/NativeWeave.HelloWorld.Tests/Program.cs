using NativeWeave.HelloWorld;

static void Equal(string expected, string actual)
{
    if (expected != actual)
    {
        throw new InvalidOperationException($"Expected {expected.Length} characters, got {actual.Length}.");
    }
}

static void Throws<T>(Action action) where T : Exception
{
    try
    {
        action();
    }
    catch (T)
    {
        return;
    }

    throw new InvalidOperationException($"Expected {typeof(T).Name}.");
}

Equal("Hello, World! From Rust.", RustGreeting.Greet());
Equal("Hello, named! From Rust.", RustGreeting.Greet(name: "named"));
Func<string, string> methodGroup = RustGreeting.Greet;
Equal("Hello, delegate! From Rust.", methodGroup("delegate"));
foreach (string name in new[] { "", "世界 🦀", "a\0b", new string('x', 4096), new string('é', 2048) })
{
    Equal($"Hello, {name}! From Rust.", RustGreeting.Greet(name));
}

Throws<ArgumentNullException>(() => RustGreeting.Greet(null!));
Throws<ArgumentException>(() => RustGreeting.Greet("\ud800"));
Throws<ArgumentException>(() => RustGreeting.Greet(new string('x', 4097)));
Throws<ArgumentException>(() => RustGreeting.Greet(new string('é', 2049)));
Parallel.For(0, 1000, index => Equal($"Hello, {index}! From Rust.", RustGreeting.Greet(index.ToString(System.Globalization.CultureInfo.InvariantCulture))));
Console.WriteLine("PASS: default, named/delegate calls, Unicode, NUL, empty, size boundaries, invalid input and 1000 concurrent greetings.");
