using System.Reflection;
using System.Text;
using System.Xml.Linq;
using NativeWeave.HelloWorld;

// Maintainer tooling only: inspect the actual compiled assembly, never used by the AOT app.
string root = Path.GetFullPath(args[0]);
Assembly assembly = typeof(RustGreeting).Assembly;
Type[] types = assembly.GetExportedTypes();
if (types.Length != 1 || types[0] != typeof(RustGreeting) || !types[0].IsAbstract || !types[0].IsSealed)
{
    throw new InvalidOperationException("Unexpected public type. Review and update the API baseline.");
}

MethodInfo[] methods = types[0].GetMethods(BindingFlags.Public | BindingFlags.Static | BindingFlags.DeclaredOnly);
if (methods.Length != 1)
{
    throw new InvalidOperationException("Unexpected public method. Review the API baseline.");
}

MethodInfo method = methods[0];
ParameterInfo parameter = method.GetParameters().Single();
var nullability = new NullabilityInfoContext();
if (method.Name != "Greet" || method.ReturnType != typeof(string) || parameter.ParameterType != typeof(string)
    || parameter.Name != "name" || (string?)parameter.DefaultValue != "World"
    || nullability.Create(parameter).ReadState != NullabilityState.NotNull
    || nullability.Create(method.ReturnParameter).ReadState != NullabilityState.NotNull)
{
    throw new InvalidOperationException("Public signature, nullability or default changed. Review compatibility.");
}

string signature = $"public static string {method.Name}(string {parameter.Name} = \"{parameter.DefaultValue}\");";
string baseline = $"public static class {types[0].FullName}\n{signature}\n";
string baselinePath = Path.Combine(root, "docs", "api-baseline.txt");
if (File.ReadAllText(baselinePath).Replace("\r\n", "\n") != baseline)
{
    throw new InvalidOperationException("Compiled API differs from docs/api-baseline.txt.");
}

XDocument xml = XDocument.Load(Path.ChangeExtension(assembly.Location, ".xml"));
XElement[] members = xml.Descendants("member").ToArray();
if (members.Length != 2 || members.Any(member => member.Element("summary") is null || member.Element("remarks") is null))
{
    throw new InvalidOperationException("Every public member needs summary and remarks documentation.");
}

XElement methodDocs = members.Single(member => ((string?)member.Attribute("name"))?.StartsWith("M:", StringComparison.Ordinal) == true);
if ((string?)methodDocs.Element("param")?.Attribute("name") != parameter.Name || methodDocs.Element("returns") is null)
{
    throw new InvalidOperationException("Parameter or return XML documentation is missing.");
}

static string Prose(XElement element)
{
    var copy = new XElement(element);
    foreach (XElement reference in copy.Descendants().Where(child => child.Name.LocalName is "paramref" or "see").ToArray())
    {
        reference.ReplaceWith((string?)reference.Attribute("name") ?? (string?)reference.Attribute("cref") ?? reference.Value);
    }
    return string.Join(" ", copy.Value.Split((char[]?)null, StringSplitOptions.RemoveEmptyEntries));
}
var output = new StringBuilder("# Hello World API reference\n\nGenerated from the compiled bootstrap assembly and XML by `tools/ApiDocs`; do not hand-edit.\n\nPackage: `NativeWeave.HelloWorld` (experimental).\n\n```csharp\n");
output.Append(baseline).Append("```\n");
foreach (XElement member in members)
{
    output.Append("\n## `").Append((string?)member.Attribute("name")).Append("`\n\n");
    foreach (XElement element in member.Elements())
    {
        output.Append("- **").Append(element.Name.LocalName);
        if (element.Attribute("name") is { } name) output.Append(' ').Append(name.Value);
        if (element.Attribute("cref") is { } cref) output.Append(' ').Append(cref.Value);
        output.Append(":** ").Append(Prose(element)).Append('\n');
    }
}

string reference = Path.Combine(root, "docs", "api-reference.md");
if (args.Contains("--write", StringComparer.Ordinal))
{
    File.WriteAllText(reference, output.ToString());
}
else if (!File.Exists(reference) || File.ReadAllText(reference) != output.ToString())
{
    throw new InvalidOperationException("API reference is stale. Run the ApiDocs tool with --write.");
}
Console.WriteLine("PASS: compiled API baseline, nullability, defaults, XML coverage and generated reference.");
