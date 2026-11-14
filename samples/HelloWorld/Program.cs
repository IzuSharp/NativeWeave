using NativeWeave.HelloWorld;

Console.WriteLine(args.Length == 0 ? RustGreeting.Greet() : RustGreeting.Greet(args[0]));
