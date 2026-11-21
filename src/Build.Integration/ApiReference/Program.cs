// Shared signature formatter adapted from the accepted A02 product checker and pinned Design inventory.
// Assembly bytes supply declarations; source is used only for record/synthesized-member classification.
// This tool imports the actual compiled product assembly. It is not used by Native AOT consumers.
using System.Collections.Immutable;
using System.Text;
using System.Text.Json;
using System.Xml.Linq;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
if (args.Length < 3) throw new ArgumentException("Usage: ApiReference <repo-root> <dotnet-root> <config.json> [--write] [--snapshot]");
var root = Path.GetFullPath(args[0]);
var sdk = Path.GetFullPath(args[1]);
using var config = JsonDocument.Parse(File.ReadAllText(args[2]));
string Resolve(string value) => Path.GetFullPath(value, root);
var assemblyPath = Resolve(config.RootElement.GetProperty("assembly").GetString()!);
var sourceRoots = config.RootElement.GetProperty("sources").EnumerateArray().Select(x => Resolve(x.GetString()!)).ToArray();
var referenceFiles = Directory.GetFiles(Path.Combine(sdk, "packs", "Microsoft.NETCore.App.Ref", "11.0.0", "ref", "net11.0"), "*.dll").ToDictionary(path => Path.GetFileName(path)!, StringComparer.OrdinalIgnoreCase);
foreach (string file in Directory.GetFiles(Path.GetDirectoryName(assemblyPath)!, "*.dll")) referenceFiles.TryAdd(Path.GetFileName(file)!, file);
// Compiler plug-ins deliberately omit Roslyn from their application payload.
// Resolve their public extension types using this pinned compiler tool's actual
// host assemblies, rather than accepting unresolved attribute/type placeholders.
foreach (var hostAssembly in new[] { typeof(Compilation).Assembly, typeof(CSharpCompilation).Assembly })
    referenceFiles.TryAdd(Path.GetFileName(hostAssembly.Location), hostAssembly.Location);
var references = referenceFiles.Values.Select(p => MetadataReference.CreateFromFile(p)).ToList();
var library = references.Single(r => Path.GetFullPath(r.FilePath!) == assemblyPath);
var compilation = CSharpCompilation.Create("NativeWeave.CompiledApi", references: references, options: new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary, metadataImportOptions: MetadataImportOptions.All));
var assembly = (IAssemblySymbol)(compilation.GetAssemblyOrModuleSymbol(library) ?? throw new InvalidOperationException("Cannot import assembly"));
var sourceRecordTypes = new HashSet<string>(StringComparer.Ordinal);
var trees = sourceRoots.SelectMany(path => Directory.GetFiles(path, "*.cs", SearchOption.AllDirectories))
    .Where(path => !path.Split(Path.DirectorySeparatorChar).Any(part => part is "bin" or "obj"))
    .Select(file => CSharpSyntaxTree.ParseText(File.ReadAllText(file), new CSharpParseOptions(LanguageVersion.CSharp15))).ToArray();
foreach (var tree in trees)
    foreach (var record in tree.GetRoot().DescendantNodes().OfType<Microsoft.CodeAnalysis.CSharp.Syntax.RecordDeclarationSyntax>())
    {
        string? ns = record.Ancestors().OfType<Microsoft.CodeAnalysis.CSharp.Syntax.BaseNamespaceDeclarationSyntax>().FirstOrDefault()?.Name.ToString();
        if (ns is not null) sourceRecordTypes.Add(ns + "." + record.Identifier.ValueText);
    }
var sourceCompilation = CSharpCompilation.Create("NativeWeave.SourceShape", syntaxTrees: trees, references: references,
    options: new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary, allowUnsafe: true));
var primaryParameters = new Dictionary<string, string[]>(StringComparer.Ordinal);
foreach (var tree in trees)
    foreach (var declaration in tree.GetRoot().DescendantNodes().OfType<Microsoft.CodeAnalysis.CSharp.Syntax.TypeDeclarationSyntax>())
        if (declaration.ParameterList is { } parameters
            && sourceCompilation.GetSemanticModel(tree).GetDeclaredSymbol(declaration)?.GetDocumentationCommentId() is { } typeId)
            primaryParameters.Add(typeId, parameters.Parameters.Select(p => p.Identifier.ValueText).ToArray());
var implicitIds = new HashSet<string>(StringComparer.Ordinal);
void FindImplicit(INamespaceOrTypeSymbol container)
{
    foreach (var member in container.GetMembers())
    {
        if (member.IsImplicitlyDeclared && member.GetDocumentationCommentId() is { } id) implicitIds.Add(id);
        if (member is INamespaceOrTypeSymbol nested) FindImplicit(nested);
    }
}
FindImplicit(sourceCompilation.Assembly.GlobalNamespace);
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
            TypeKind.Struct => type.IsRecord || sourceRecordTypes.Contains(type.ToDisplayString(typeNameFormat)) ? "record struct" : "struct",
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

var expected = new Dictionary<string, JsonElement>(StringComparer.Ordinal);
foreach (var file in config.RootElement.GetProperty("baselines").EnumerateArray())
{
    using var baseline = JsonDocument.Parse(File.ReadAllText(Resolve(file.GetString()!)));
    foreach (var entry in baseline.RootElement.GetProperty("symbols").EnumerateArray())
        expected.Add(entry.GetProperty("id").GetString()!, entry.Clone());
}
var actual = new Dictionary<string, ISymbol>(StringComparer.Ordinal);
void Add(ISymbol symbol)
{
    if (symbol.DeclaredAccessibility is not (Accessibility.Public or Accessibility.Protected or Accessibility.ProtectedOrInternal)) return;
    if (symbol is IMethodSymbol m && m.MethodKind is MethodKind.PropertyGet or MethodKind.PropertySet or MethodKind.EventAdd or MethodKind.EventRemove or MethodKind.StaticConstructor) return;
    if (symbol is IFieldSymbol f && f.Name == "value__" && f.ContainingType.TypeKind == TypeKind.Enum) return;
    var id = symbol.GetDocumentationCommentId(); if (id is not null) actual.Add(id, symbol);
}
void WalkType(INamedTypeSymbol type)
{
    if (type.DeclaredAccessibility is not (Accessibility.Public or Accessibility.Protected or Accessibility.ProtectedOrInternal)) return;
    Add(type);
    foreach (var member in type.GetMembers())
        if (member is INamedTypeSymbol nested) WalkType(nested); else Add(member);
}
void Walk(INamespaceSymbol ns)
{
    foreach (var child in ns.GetNamespaceMembers()) Walk(child);
    foreach (var type in ns.GetTypeMembers()) WalkType(type);
}
Walk(assembly.GlobalNamespace);
if (args.Contains("--snapshot", StringComparer.Ordinal))
{
    expected.Clear();
    foreach (var pair in actual)
        expected.Add(pair.Key, JsonSerializer.SerializeToElement(new { id = pair.Key, signature = Declaration(pair.Value), implicit_member = implicitIds.Contains(pair.Key) }));
}
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
var output = new StringBuilder("# " + config.RootElement.GetProperty("title").GetString() + "\n\nGenerated from the compiled product assembly and XML by `src/Build.Integration/ApiReference`.\n\n" + config.RootElement.GetProperty("scope").GetString() + "\n\n");
foreach (var entry in expected.OrderBy(e => e.Key, StringComparer.Ordinal))
{
    if (!actual.TryGetValue(entry.Key, out var symbol)) continue;
    var implicitMember = entry.Value.GetProperty("implicit_member").GetBoolean();
    if (!implicitMember && (!docs.TryGetValue(entry.Key, out var doc) || doc.Element("summary") is null || string.IsNullOrWhiteSpace(doc.Element("summary")!.Value))) failures.Add("Missing XML summary: " + entry.Key);
    if (!implicitMember && docs.TryGetValue(entry.Key, out var member))
    {
        var names = (primaryParameters.TryGetValue(entry.Key, out var primaryNames)
            ? primaryNames : Parameters(symbol).Select(p => p.Name)).OrderBy(x => x, StringComparer.Ordinal).ToArray();
        bool HasContent(XElement element) => !string.IsNullOrWhiteSpace(element.Value)
            || element.Descendants().Any(e => (e.Name.LocalName is "see" or "seealso" && !string.IsNullOrWhiteSpace(e.Attribute("cref")?.Value))
                || (e.Name.LocalName is "paramref" or "typeparamref" && !string.IsNullOrWhiteSpace(e.Attribute("name")?.Value)));
        var documented = member.Elements("param").Where(HasContent).Select(e => e.Attribute("name")?.Value).OrderBy(x => x, StringComparer.Ordinal).ToArray();
        if (!names.SequenceEqual(documented)) failures.Add("XML parameter names differ: " + entry.Key);
        bool typeRemarks = symbol.ContainingType?.GetDocumentationCommentId() is { } ownerId
            && docs.TryGetValue(ownerId, out var ownerDoc) && !string.IsNullOrWhiteSpace(ownerDoc.Element("remarks")?.Value);
        // Enum constants have no resource lifetime or execution cost. Their
        // complete summary/value mapping remains mandatory; requiring generic
        // lifetime boilerplate would change the already accepted module contract.
        bool enumValue = symbol is INamedTypeSymbol { TypeKind: TypeKind.Enum }
            || symbol.ContainingType?.TypeKind == TypeKind.Enum;
        if (!enumValue && string.IsNullOrWhiteSpace(member.Element("remarks")?.Value) && !typeRemarks)
            failures.Add("Missing member or inherited type lifetime/cost remarks: " + entry.Key);
        foreach (var parameter in TypeParameters(symbol)) if (!member.Elements("typeparam").Any(e => e.Attribute("name")?.Value == parameter.Name && HasContent(e))) failures.Add("Missing XML type parameter " + parameter.Name + ": " + entry.Key);
        bool returnsValue = symbol is IMethodSymbol { ReturnsVoid: false, MethodKind: not MethodKind.Constructor }
            || symbol is INamedTypeSymbol { DelegateInvokeMethod: { ReturnsVoid: false } };
        if (returnsValue && (member.Element("returns") is not { } returns || !HasContent(returns))) failures.Add("Missing XML returns: " + entry.Key);
    }
    output.Append("## `").Append(entry.Key).Append("`\n\n```csharp\n").Append(Declaration(symbol)).Append("\n```\n\n");
    if (implicitMember) output.Append("Compiler-generated record/delegate member; inherits the documented type semantics.\n\n");
    else if (docs.TryGetValue(entry.Key, out var memberDoc))
        foreach (var element in memberDoc.Elements())
        {
            string content = string.Join(" ", element.Value.Split((char[]?)null, StringSplitOptions.RemoveEmptyEntries));
            output.Append("**").Append(element.Name.LocalName).Append(element.Attribute("name") is { } name ? " " + name.Value : "").Append(":**");
            if (content.Length != 0) output.Append(' ').Append(content);
            output.Append("\n\n");
        }
    if (symbol.ContainingType?.GetDocumentationCommentId() is { } typeId && docs.TryGetValue(typeId, out var typeDoc)
        && typeDoc.Element("remarks") is { } policy)
        output.Append("**Inherited type policy:** ").Append(string.Join(" ", policy.Value.Split((char[]?)null, StringSplitOptions.RemoveEmptyEntries))).Append("\n\n");
}
if (failures.Count > 0) throw new InvalidOperationException(string.Join("\n", failures));
var destination = Resolve(config.RootElement.GetProperty("output").GetString()!);
Directory.CreateDirectory(Path.GetDirectoryName(destination)!);
if (args.Contains("--snapshot", StringComparer.Ordinal))
{
    var snapshot = new { assembly = assembly.Identity.ToString(), symbols = expected.OrderBy(e => e.Key, StringComparer.Ordinal).Select(e => e.Value).ToArray() };
    File.WriteAllText(Path.ChangeExtension(destination, ".json"), JsonSerializer.Serialize(snapshot, new JsonSerializerOptions { WriteIndented = true }) + "\n");
}
string rendered = output.ToString().TrimEnd() + "\n";
if (args.Contains("--write") || args.Contains("--snapshot")) File.WriteAllText(destination, rendered);
else if (!File.Exists(destination) || File.ReadAllText(destination) != rendered) throw new InvalidOperationException("Generated API reference is stale.");
Console.WriteLine(JsonSerializer.Serialize(new { status = "passed", compiled_symbols = actual.Count, exact_pinned_signatures = expected.Count, xml_complete = true, generated_reference = true }));
