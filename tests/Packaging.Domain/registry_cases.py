"""Local NuGet V3 readback regression over the actual database candidate bytes.

This loopback verification fixture is not a NativeWeave application server or a
registry publication. An unlisted version must remain restorable by exact ID.
"""
from __future__ import annotations

import functools
import http.server
import shutil
import threading
import xml.etree.ElementTree as ET

from model import save, sha

FLAGS = ["-p:UseSharedCompilation=false", "-nr:false", "-m:1"]


def restore_unlisted(consumer, root, record):
    c = consumer
    webroot = root / "unlisted-v3"
    webroot.mkdir()
    for item in c.release["packages"]:
        name, version = item["id"].lower(), item["version"].lower()
        folder = webroot / "flat" / name / version
        folder.mkdir(parents=True)
        shutil.copyfile(c.packages[item["id"]], folder / f"{name}.{version}.nupkg")
        save(webroot / "flat" / name / "index.json", {"versions": [version]})
    requests = []

    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            requests.append(self.path)

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Handler, directory=str(webroot)))
    base = f"http://127.0.0.1:{server.server_port}/"
    save(webroot / "index.json", {"version": "3.0.0", "resources": [
        {"@id": base + "flat/", "@type": "PackageBaseAddress/3.0.0"},
        {"@id": base + "registration/", "@type": "RegistrationsBaseUrl/3.6.0"}]})
    for item in c.release["packages"]:
        name, version = item["id"].lower(), item["version"].lower()
        save(webroot / "registration" / name / "index.json", {"count": 1, "items": [{"count": 1, "items": [{
            "catalogEntry": {"id": item["id"], "version": version, "listed": False},
            "packageContent": base + f"flat/{name}/{version}/{name}.{version}.nupkg"}]}]})
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        directory = c.work / "unlisted-known-version"
        c.template("combined", directory)
        configuration = ET.Element("configuration")
        sources = ET.SubElement(configuration, "packageSources")
        ET.SubElement(sources, "clear")
        ET.SubElement(sources, "add", key="unlisted-loopback", value=base + "index.json", allowInsecureConnections="true")
        ET.SubElement(sources, "add", key="nuget.org", value="https://api.nuget.org/v3/index.json")
        mappings = ET.SubElement(configuration, "packageSourceMapping")
        local = ET.SubElement(mappings, "packageSource", key="unlisted-loopback")
        ET.SubElement(local, "package", pattern="NativeWeave.*")
        external = ET.SubElement(mappings, "packageSource", key="nuget.org")
        ET.SubElement(external, "package", pattern="*")
        # Keep auditing enabled while the protocol fixture serves only packages.
        # https://learn.microsoft.com/nuget/reference/nuget-config-file#auditsources
        audit = ET.SubElement(configuration, "auditSources")
        ET.SubElement(audit, "clear")
        ET.SubElement(audit, "add", key="nuget.org", value="https://api.nuget.org/v3/index.json")
        config = directory / "NuGet.Config"
        ET.ElementTree(configuration).write(config, encoding="utf-8", xml_declaration=True)
        c.run("unlisted-domain-known-version-restore", ["dotnet", "restore", directory / "Consumer.csproj",
              "--configfile", config, *FLAGS], cwd=directory, env=c.environment_for(directory))
        selected = c.validate_graph("combined", directory)
        archives = {}
        for item in c.release["packages"]:
            name, version = item["id"].lower(), item["version"].lower()
            archives[item["id"]] = sha(directory / "cache" / name / version / f"{name}.{version}.nupkg")
        if not any(path.endswith(".nupkg") for path in requests):
            raise ValueError("The exact database archives were not fetched from the loopback V3 fixture")
        record("unlisted-domain-known-version-restore", actualNuGetRestore=True, freshRestoreCache=True,
               selectedPackages=selected, packages=archives, nugetAuditEnabled=True,
               scope="Exact known versions restored from a loopback V3 fixture configured listed=false; no public catalog or package was changed.")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        if thread.is_alive():
            raise RuntimeError("The local NuGet verification server did not stop")
        save(c.evidence / "unlisted-http-requests.json", requests)
