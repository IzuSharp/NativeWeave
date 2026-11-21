// Signature formatting adapted from the pinned Design compiler-symbol inventory.
// This tool imports the actual compiled product assembly. It is not used by Native AOT consumers.
using System.Collections.Immutable;
using System.Text;
using System.Text.Json;
using System.Xml.Linq;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
if (args.Length < 3) throw new ArgumentException("Usage: ApiCheck <repo-root> <dotnet-root> <assembly> [--write]");
var root = Path.GetFullPath(args[0]); var sdk = Path.GetFullPath(args[1]); var assemblyPath = Path.GetFullPath(args[2]);
var references = Directory.GetFiles(Path.Combine(sdk, "packs", "Microsoft.NETCore.App.Ref", "11.0.0", "ref", "net11.0"), "*.dll").Select(p => MetadataReference.CreateFromFile(p)).ToList();
references.AddRange(Directory.GetFiles(Path.GetDirectoryName(assemblyPath)!, "*.dll").Where(p => p != assemblyPath).Select(p => MetadataReference.CreateFromFile(p)));
var library = MetadataReference.CreateFromFile(assemblyPath); references.Add(library);
var compilation = CSharpCompilation.Create("NativeWeave.Database.PostgreSql.ApiCheck", references: references, options: new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary, metadataImportOptions: MetadataImportOptions.All));
var assembly = (IAssemblySymbol)(compilation.GetAssemblyOrModuleSymbol(library) ?? throw new InvalidOperationException("Cannot import assembly"));
bool CompilerAttribute(AttributeData a) => a.AttributeClass?.ContainingNamespace.ToDisplayString() is "System.Runtime.CompilerServices" or "System.Diagnostics";
// A type used in a signature is not a type declaration. In particular, base types,
// interfaces and return types must not acquire "class", variance or constraints.
var typeFormat = new SymbolDisplayFormat(
    globalNamespaceStyle: SymbolDisplayGlobalNamespaceStyle.Omitted,
    typeQualificationStyle: SymbolDisplayTypeQualificationStyle.NameAndContainingTypesAndNamespaces,
    genericsOptions: SymbolDisplayGenericsOptions.IncludeTypeParameters,
    miscellaneousOptions: SymbolDisplayMiscellaneousOptions.IncludeNullableReferenceTypeModifier | SymbolDisplayMiscellaneousOptions.UseSpecialTypes | SymbolDisplayMiscellaneousOptions.EscapeKeywordIdentifiers);
var typeNameFormat = typeFormat.WithGenericsOptions(SymbolDisplayGenericsOptions.IncludeTypeParameters | SymbolDisplayGenericsOptions.IncludeVariance);
var format = new SymbolDisplayFormat(
    globalNamespaceStyle: SymbolDisplayGlobalNamespaceStyle.Omitted,
    typeQualificationStyle: SymbolDisplayTypeQualificationStyle.NameAndContainingTypesAndNamespaces,
    genericsOptions: SymbolDisplayGenericsOptions.IncludeTypeParameters | SymbolDisplayGenericsOptions.IncludeTypeConstraints | SymbolDisplayGenericsOptions.IncludeVariance,
    memberOptions: SymbolDisplayMemberOptions.IncludeAccessibility | SymbolDisplayMemberOptions.IncludeModifiers | SymbolDisplayMemberOptions.IncludeContainingType | SymbolDisplayMemberOptions.IncludeType | SymbolDisplayMemberOptions.IncludeParameters | SymbolDisplayMemberOptions.IncludeExplicitInterface | SymbolDisplayMemberOptions.IncludeConstantValue | SymbolDisplayMemberOptions.IncludeRef,
    parameterOptions: SymbolDisplayParameterOptions.IncludeType | SymbolDisplayParameterOptions.IncludeName | SymbolDisplayParameterOptions.IncludeDefaultValue | SymbolDisplayParameterOptions.IncludeParamsRefOut | SymbolDisplayParameterOptions.IncludeExtensionThis,
    propertyStyle: SymbolDisplayPropertyStyle.ShowReadWriteDescriptor,
    kindOptions: SymbolDisplayKindOptions.IncludeTypeKeyword | SymbolDisplayKindOptions.IncludeMemberKeyword,
    miscellaneousOptions: SymbolDisplayMiscellaneousOptions.IncludeNullableReferenceTypeModifier | SymbolDisplayMiscellaneousOptions.UseSpecialTypes | SymbolDisplayMiscellaneousOptions.EscapeKeywordIdentifiers);
string TypeName(ITypeSymbol type) => type.ToDisplayString(typeFormat);
string[] Attributes(ImmutableArray<AttributeData> attributes) => attributes
    .Where(a => !CompilerAttribute(a))
    .Select(a => a.ToString() ?? throw new InvalidOperationException("Missing attribute display"))
    .OrderBy(x => x, StringComparer.Ordinal).ToArray();
string InlineAttributes(ImmutableArray<AttributeData> attributes) => string.Concat(Attributes(attributes).Select(a => "[" + a + "] "));
ImmutableArray<IParameterSymbol> Parameters(ISymbol symbol) => symbol switch
{
    IMethodSymbol method => method.Parameters,
    IPropertySymbol property => property.Parameters,
    INamedTypeSymbol { DelegateInvokeMethod: { } invoke } => invoke.Parameters,
    _ => ImmutableArray<IParameterSymbol>.Empty
};
ImmutableArray<ITypeParameterSymbol> TypeParameters(ISymbol symbol) => symbol switch
{
    IMethodSymbol method => method.TypeParameters,
    INamedTypeSymbol type => type.TypeParameters,
    _ => ImmutableArray<ITypeParameterSymbol>.Empty
};
ImmutableArray<AttributeData> ReturnAttributes(ISymbol symbol) => symbol switch
{
    IMethodSymbol method => method.GetReturnTypeAttributes(),
    IPropertySymbol { GetMethod: { } getter } => getter.GetReturnTypeAttributes(),
    INamedTypeSymbol { DelegateInvokeMethod: { } invoke } => invoke.GetReturnTypeAttributes(),
    _ => ImmutableArray<AttributeData>.Empty
};
string[] ConstraintTypes(ITypeParameterSymbol parameter) => parameter.ConstraintTypes
    .Select((type, index) => TypeName(type.WithNullableAnnotation(parameter.ConstraintNullableAnnotations[index]))).ToArray();
string ConstraintClause(ITypeParameterSymbol parameter)
{
    var constraints = new List<string>();
    if (parameter.HasUnmanagedTypeConstraint) constraints.Add("unmanaged");
    else if (parameter.HasValueTypeConstraint) constraints.Add("struct");
    else if (parameter.HasReferenceTypeConstraint)
        constraints.Add(parameter.ReferenceTypeConstraintNullableAnnotation == NullableAnnotation.Annotated ? "class?" : "class");
    if (parameter.HasNotNullConstraint) constraints.Add("notnull");
    constraints.AddRange(ConstraintTypes(parameter));
    if (parameter.HasConstructorConstraint) constraints.Add("new()");
    if (parameter.AllowsRefLikeType) constraints.Add("allows ref struct");
    return constraints.Count == 0 ? "" : "where " + parameter.ToDisplayString(typeFormat) + " : " + string.Join(", ", constraints);
}
string[] Constraints(ISymbol symbol) => TypeParameters(symbol).Select(ConstraintClause).Where(x => x.Length != 0).ToArray();
string AccessibilityText(Accessibility accessibility) => accessibility switch
{
    Accessibility.Public => "public",
    Accessibility.Protected => "protected",
    Accessibility.ProtectedOrInternal => "protected internal",
    Accessibility.ProtectedAndInternal => "private protected",
    Accessibility.Internal => "internal",
    Accessibility.Private => "private",
    _ => throw new InvalidOperationException("Unsupported declared accessibility: " + accessibility)
};
string[] TypeModifiers(INamedTypeSymbol type)
{
    var modifiers = new List<string> { AccessibilityText(type.DeclaredAccessibility) };
    if (type.IsStatic) modifiers.Add("static");
    else if (type.TypeKind == TypeKind.Class)
    {
        if (type.IsAbstract) modifiers.Add("abstract");
        if (type.IsSealed) modifiers.Add("sealed");
    }
    if (type.TypeKind == TypeKind.Struct)
    {
        if (type.IsReadOnly) modifiers.Add("readonly");
        if (type.IsRefLikeType) modifiers.Add("ref");
    }
    return modifiers.ToArray();
}
string RefPrefix(RefKind kind) => kind switch
{
    RefKind.Ref => "ref ",
    RefKind.RefReadOnly => "ref readonly ",
    _ => ""
};
string NamedTypeDeclaration(INamedTypeSymbol type)
{
    string prefix = string.Join(" ", TypeModifiers(type)) + " ";
    string name = type.ToDisplayString(typeNameFormat);
    string declaration;
    if (type.TypeKind == TypeKind.Delegate)
    {
        var invoke = type.DelegateInvokeMethod ?? throw new InvalidOperationException("Missing delegate Invoke: " + name);
        declaration = prefix + "delegate " + RefPrefix(invoke.RefKind) + TypeName(invoke.ReturnType) + " " + name
            + "(" + string.Join(", ", invoke.Parameters.Select(p => InlineAttributes(p.GetAttributes()) + p.ToDisplayString(format))) + ")";
    }
    else
    {
        string kind = type.TypeKind switch
        {
            TypeKind.Class => type.IsRecord ? "record class" : "class",
            TypeKind.Struct => type.IsRecord ? "record struct" : "struct",
            TypeKind.Interface => "interface",
            TypeKind.Enum => "enum",
            _ => throw new InvalidOperationException("Unsupported public type kind: " + type.TypeKind)
        };
        declaration = prefix + kind + " " + name;
        var bases = new List<string>();
        if (type.TypeKind == TypeKind.Enum)
            bases.Add(TypeName(type.EnumUnderlyingType ?? throw new InvalidOperationException("Missing enum underlying type: " + name)));
        else
        {
            if (type.TypeKind == TypeKind.Class && type.BaseType is { SpecialType: not SpecialType.System_Object } baseType)
                bases.Add(TypeName(baseType));
            bases.AddRange(type.Interfaces.Select(TypeName));
        }
        if (bases.Count != 0) declaration += " : " + string.Join(", ", bases);
    }
    var constraints = Constraints(type);
    return declaration + (constraints.Length == 0 ? "" : " " + string.Join(" ", constraints));
}
string MemberDeclaration(ISymbol symbol)
{
    // Symbol display preserves operators, indexers, tuple element names, defaults,
    // ref/scoped modifiers and generic constraints. It omits attributes, so insert
    // each parameter's attributes at its own token boundary, never by text replace.
    var parts = symbol.ToDisplayParts(format);
    var insertions = new Dictionary<int, string>();
    var parameters = Parameters(symbol);
    for (int i = 0; i < parts.Length; i++)
    {
        if (symbol is IPropertySymbol property && parts[i].Kind == SymbolDisplayPartKind.Keyword && parts[i].ToString() == "get"
            && property.GetMethod is { } getter)
        {
            string annotations = InlineAttributes(getter.GetAttributes())
                + string.Concat(Attributes(getter.GetReturnTypeAttributes()).Select(a => "[return: " + a + "] "));
            if (annotations.Length != 0) insertions.Add(i, annotations);
        }
        if (parts[i].Kind != SymbolDisplayPartKind.ParameterName || parts[i].Symbol is not IParameterSymbol parameter
            || !parameters.Any(p => SymbolEqualityComparer.Default.Equals(p, parameter))) continue;
        string attributes = InlineAttributes(parameter.GetAttributes());
        if (attributes.Length == 0) continue;
        int angles = 0, parentheses = 0, brackets = 0, start = 0;
        for (int j = i - 1; j >= 0; j--)
        {
            string token = parts[j].ToString();
            if (token == ">") angles++;
            else if (token == "<") angles--;
            else if (token == "]") brackets++;
            else if (token == "[")
            {
                if (brackets == 0 && angles == 0 && parentheses == 0) { start = j + 1; break; }
                brackets--;
            }
            else if (token == ")") parentheses++;
            else if (token == "(")
            {
                if (parentheses == 0 && angles == 0 && brackets == 0) { start = j + 1; break; }
                parentheses--;
            }
            else if (token == "," && angles == 0 && parentheses == 0 && brackets == 0) { start = j + 1; break; }
        }
        while (start < i && parts[start].Kind == SymbolDisplayPartKind.Space) start++;
        insertions.Add(start, attributes);
    }
    var text = new StringBuilder();
    for (int i = 0; i < parts.Length; i++)
    {
        if (insertions.TryGetValue(i, out string? attributes)) text.Append(attributes);
        text.Append(parts[i].ToString());
    }
    return text.ToString();
}
string Declaration(ISymbol symbol)
{
    var text = new StringBuilder();
    foreach (string attribute in Attributes(symbol.GetAttributes())) text.Append('[').Append(attribute).Append("]\n");
    if (symbol is not IPropertySymbol)
        foreach (string attribute in Attributes(ReturnAttributes(symbol))) text.Append("[return: ").Append(attribute).Append("]\n");
    return text.Append(symbol is INamedTypeSymbol type ? NamedTypeDeclaration(type) : MemberDeclaration(symbol)).ToString();
}

using var baseline = JsonDocument.Parse(File.ReadAllText(Path.Combine(root, "src/Data.Postgres/public-api.expected.json")));
var expected = baseline.RootElement.GetProperty("symbols").EnumerateArray().ToDictionary(x => x.GetProperty("id").GetString()!, x => x.Clone(), StringComparer.Ordinal);
var actual = new Dictionary<string, ISymbol>(StringComparer.Ordinal);
void Add(ISymbol symbol)
{
    if (symbol.DeclaredAccessibility is not (Accessibility.Public or Accessibility.Protected or Accessibility.ProtectedOrInternal)) return;
    if (symbol is IMethodSymbol m && m.MethodKind is MethodKind.PropertyGet or MethodKind.PropertySet or MethodKind.EventAdd or MethodKind.EventRemove or MethodKind.StaticConstructor) return;
    if (symbol is IFieldSymbol f && f.Name == "value__" && f.ContainingType.TypeKind == TypeKind.Enum) return;
    var id = symbol.GetDocumentationCommentId(); if (id is not null) actual.Add(id, symbol);
}
void Walk(INamespaceSymbol ns)
{
    foreach (var child in ns.GetNamespaceMembers()) Walk(child);
    foreach (var type in ns.GetTypeMembers().Where(t => t.DeclaredAccessibility == Accessibility.Public)) { Add(type); foreach (var member in type.GetMembers()) Add(member); }
}
Walk(assembly.GlobalNamespace);
var failures = new List<string>();
foreach (var key in actual.Keys.Except(expected.Keys)) failures.Add("Unexpected public symbol: " + key);
foreach (var key in expected.Keys.Except(actual.Keys)) failures.Add("Missing public symbol: " + key);
foreach (var key in expected.Keys.Intersect(actual.Keys))
{
    var wanted = expected[key].GetProperty("signature").GetString(); var got = Declaration(actual[key]);
    if (wanted != got) failures.Add(key + "\n expected: " + wanted + "\n actual: " + got);
}
var xml = XDocument.Load(Path.ChangeExtension(assemblyPath, ".xml"));
var docs = xml.Descendants("member").ToDictionary(e => e.Attribute("name")!.Value, StringComparer.Ordinal);
var output = new StringBuilder("# NativeWeave.Database.PostgreSql API reference\n\nGenerated from the compiled product assembly and its XML comments by `tests/Data.Postgres/ApiCheck`. Covers provider options, Engine preflight, and the integrated Create/UsePostgreSql data source factories. Exact declarations retain the pinned Design identity in `public-api.expected.json`; the historical B02/B04 ownership slice remains in `downstream-composition.json`.\n\n");
foreach (var entry in expected.OrderBy(e => e.Key, StringComparer.Ordinal))
{
    if (!actual.TryGetValue(entry.Key, out var symbol)) continue;
    var implicitMember = entry.Value.GetProperty("implicit_member").GetBoolean();
    if (!implicitMember && (!docs.TryGetValue(entry.Key, out var doc) || doc.Element("summary") is null || string.IsNullOrWhiteSpace(doc.Element("summary")!.Value))) failures.Add("Missing XML summary: " + entry.Key);
    if (!implicitMember && docs.TryGetValue(entry.Key, out var member))
    {
        foreach (var parameter in Parameters(symbol)) if (!member.Elements("param").Any(e => e.Attribute("name")?.Value == parameter.Name)) failures.Add("Missing XML parameter " + parameter.Name + ": " + entry.Key);
        foreach (var parameter in TypeParameters(symbol)) if (!member.Elements("typeparam").Any(e => e.Attribute("name")?.Value == parameter.Name)) failures.Add("Missing XML type parameter " + parameter.Name + ": " + entry.Key);
        if (symbol is IMethodSymbol { ReturnsVoid: false, MethodKind: not MethodKind.Constructor } && member.Element("returns") is null) failures.Add("Missing XML returns: " + entry.Key);
    }
    output.Append("## `").Append(entry.Key).Append("`\n\n```csharp\n").Append(Declaration(symbol)).Append("\n```\n\n");
    if (implicitMember) output.Append("Compiler-generated record/delegate member; inherits the documented type semantics.\n\n");
    else if (docs.TryGetValue(entry.Key, out var memberDoc))
        foreach (var element in memberDoc.Elements()) output.Append("**").Append(element.Name.LocalName).Append(element.Attribute("name") is { } name ? " " + name.Value : "").Append(":** ").Append(string.Join(" ", element.Value.Split((char[]?)null, StringSplitOptions.RemoveEmptyEntries))).Append("\n\n");
}
if (failures.Count > 0) throw new InvalidOperationException(string.Join("\n", failures));
var destination = Path.Combine(root, "src/Data.Postgres/api-reference.md");
string rendered = output.ToString().TrimEnd() + "\n";
if (args.Contains("--write")) File.WriteAllText(destination, rendered);
else if (!File.Exists(destination) || File.ReadAllText(destination) != rendered) throw new InvalidOperationException("Generated API reference is stale.");
Console.WriteLine(JsonSerializer.Serialize(new { status = "passed", compiled_symbols = actual.Count, exact_pinned_signatures = expected.Count, xml_complete = true, generated_reference = true }));
