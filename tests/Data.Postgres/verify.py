#!/usr/bin/env python3
"""B02 Linux component verification. All ephemeral PG processes share this lifetime."""
import argparse, datetime, hashlib, json, os, shutil, socket, subprocess, sys, time
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
ROOT = Path(__file__).resolve().parents[2]
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def certificates(directory):
    directory.mkdir()
    now = datetime.datetime.now(datetime.timezone.utc)
    def ca(name):
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, name)])
        cert = x509.CertificateBuilder().subject_name(subject).issuer_name(subject).public_key(key.public_key()).serial_number(x509.random_serial_number()).not_valid_before(now-datetime.timedelta(days=1)).not_valid_after(now+datetime.timedelta(days=10)).add_extension(x509.BasicConstraints(ca=True,path_length=0),True).add_extension(x509.KeyUsage(False,False,False,False,False,True,True,False,False),True).sign(key,hashes.SHA256())
        return key, cert
    ca_key, root = ca('B02 ephemeral trusted root'); _, untrusted = ca('B02 ephemeral unrelated root')
    (directory/'root.pem').write_bytes(root.public_bytes(serialization.Encoding.PEM))
    (directory/'untrusted.pem').write_bytes(untrusted.public_bytes(serialization.Encoding.PEM))
    for name, expired in [('valid',False),('expired',True)]:
        key = rsa.generate_private_key(public_exponent=65537,key_size=2048)
        before = now-datetime.timedelta(days=3)
        after = now-datetime.timedelta(days=1) if expired else now+datetime.timedelta(days=3)
        cert = x509.CertificateBuilder().subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'localhost')])).issuer_name(root.subject).public_key(key.public_key()).serial_number(x509.random_serial_number()).not_valid_before(before).not_valid_after(after).add_extension(x509.BasicConstraints(ca=False,path_length=None),True).add_extension(x509.SubjectAlternativeName([x509.DNSName('localhost')]),False).add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),False).sign(ca_key,hashes.SHA256())
        (directory/f'{name}.pem').write_bytes(cert.public_bytes(serialization.Encoding.PEM))
        path=directory/f'{name}.key';path.write_bytes(key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()));path.chmod(0o600)
    return {'root_sha256':sha(directory/'root.pem'),'server_sha256':sha(directory/'valid.pem'),'expired_sha256':sha(directory/'expired.pem'),'generated_utc':now.isoformat(),'server_dns_san':['localhost']}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--postgres-bin',type=Path,required=True);parser.add_argument('--offline-config',type=Path);parser.add_argument('--native-only',action='store_true');parser.add_argument('--write-reference',action='store_true');parser.add_argument('--update-locks',action='store_true');parser.add_argument('--design-root',type=Path,default=ROOT.parent.parent/'Task-02-linux/NativeWeave-Design')
    args=parser.parse_args();output=args.output.resolve();output.mkdir(parents=True,exist_ok=False)
    env=os.environ.copy();inputs=[];env.update(DOTNET_CLI_USE_MSBUILD_SERVER='0',MSBUILDUSESERVER='0');records=[];servers=[];status='failed';host_preflight=False
    for name in list(env):
        if name.startswith('PG'): del env[name]
    def run(label,command,extra=None):
        log=output/(label+'.stdout.log');err=output/(label+'.stderr.log');start=time.monotonic()
        with log.open('w') as stdout,err.open('w') as stderr:
            result=subprocess.run([str(x) for x in command],cwd=ROOT,env=env| (extra or {}),stdout=stdout,stderr=stderr)
        records.append({'label':label,'command':[str(x) for x in command],'exit_code':result.returncode,'seconds':round(time.monotonic()-start,3),'stdout_sha256':sha(log),'stderr_sha256':sha(err)})
        (output/'commands.json').write_text(json.dumps(records,indent=2)+'\n')
        print(f'{label}: {result.returncode}',flush=True)
        if result.returncode: raise RuntimeError(f'{label} failed; see {err}')
    try:
        pinned=json.loads((ROOT/'src/Data.Postgres/design-inputs.json').read_text())
        design=args.design_root.resolve()
        actual_commit=subprocess.check_output(['git','-C',str(design),'rev-parse','HEAD'],text=True).strip()
        if actual_commit!=pinned['commit']:raise RuntimeError('Design checkout is not the exact pinned commit.')
        for item in pinned['inputs']:
            if sha(design/item['path'])!=item['sha256']:raise RuntimeError('Pinned Design input mismatch: '+item['path'])
        canonical=json.loads((design/'docs/api/public-api.json').read_text())['symbols']
        expected=[item for item in canonical if 'NativeWeave.Database.PostgreSql.' in item['id']]
        local=json.loads((ROOT/'src/Data.Postgres/public-api.expected.json').read_text())['symbols']
        local_by_id={x['id']:x for x in local}
        if len(local)!=len(expected) or {x['id']:x for x in expected}!=local_by_id:raise RuntimeError('The complete integrated provider API differs from pinned Design.')
        historical=json.loads((ROOT/'src/Data.Postgres/downstream-composition.json').read_text())['symbols']
        if any(item!=local_by_id.get(item['id']) for item in historical):raise RuntimeError('The historical B04 ownership slice differs from the integrated provider API.')
        prefixes=['src/Data.Postgres/','tests/Data.Postgres/','samples/api/data-postgres/','src/Data.NativeHost/','native/database/host/','native/database/postgres/','native/database/codecs/','native/database/interfaces/','native/database/transactions/','native/interop/abi/','src/Interop.Abi/','src/Interop.Negotiation/','src/Interop.Errors/','src/NativeWeave.Core/','src/Data.Abstractions/']
        shared={'Cargo.toml','Cargo.lock','Directory.Build.props','global.json','rust-toolchain.toml','docs/guides/data-postgres.md','tests/ProviderProfileChecks.cs'}
        paths=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
        inputs=[{'path':p,'sha256':sha(ROOT/p)} for p in paths if p and (p in shared or any(p.startswith(prefix) for prefix in prefixes))]
        (output/'source-inputs.json').write_text(json.dumps({'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'git_status':subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True),'inputs':inputs,'preparation':args.write_reference or args.update_locks},indent=2)+'\n')
        run('rust-toolchain',['rustc','--version','--verbose'])
        run('dotnet-toolchain',['dotnet','--info'])
        run('native-features',['cargo','tree','-p','nativeweave-data-postgres','-e','features','--locked','--offline'])
        run('native-metadata',['cargo','metadata','--format-version','1','--no-deps','--locked','--offline'])
        certs=output/'certificates';(output/'tls-identities.json').write_text(json.dumps(certificates(certs),indent=2)+'\n')
        pg=args.postgres_bin.resolve();urls={}
        for name,tls in [('valid',True),('expired',True),('plain',False)]:
            data=output/f'pg-{name}';run(f'pg-init-{name}',[pg/'initdb','-D',data,'-U','nativeweave','--auth=trust','--no-locale','--encoding=UTF8'])
            with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
            with (data/'postgresql.conf').open('a') as conf:
                conf.write("\nfsync=on\nssl="+('on' if tls else 'off')+'\n')
                if tls:conf.write(f"ssl_cert_file='{certs/name}.pem'\nssl_key_file='{certs/name}.key'\n")
            logfile=(output/f'pg-{name}.log').open('w')
            process=subprocess.Popen([str(pg/'postgres'),'-D',str(data),'-h','127.0.0.1','-p',str(port),'-k',''],env=env,stdout=logfile,stderr=subprocess.STDOUT)
            servers.append((process,data,logfile))
            for _ in range(200):
                if process.poll() is not None:raise RuntimeError(f'{name} server exited')
                if subprocess.run([str(pg/'pg_isready'),'-h','127.0.0.1','-p',str(port)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:break
                time.sleep(.05)
            else:raise RuntimeError(f'{name} server startup timeout')
            urls[name]=f'postgresql://nativeweave@localhost:{port}/postgres'
        (output/'server-topology.json').write_text(json.dumps({'endpoints':urls,'postgres_binary_sha256':sha(pg/'postgres'),'postgres_bin':str(pg),'transport':'TCP loopback; actual PostgreSQL18, ephemeral test-only trust authentication'},indent=2)+'\n')
        native_env={'NW_PG_URL':urls['valid'],'NW_PG_EXPIRED_URL':urls['expired'],'NW_PG_PLAIN_URL':urls['plain'],'NW_PG_ROOT':str(certs/'root.pem'),'NW_PG_UNTRUSTED_ROOT':str(certs/'untrusted.pem')}
        run('rust-oracles',['cargo','test','--manifest-path','tests/Data.Postgres/native/Cargo.toml','--locked','--offline','--','--nocapture'],native_env|{'NW_PG_REPORT':str(output/'native-report.json')})
        if not args.native_only:
            run('component-release',['cargo','build','-p','nativeweave-data-postgres','--release','--locked','--offline'])
            run('component-link-command',['cargo','rustc','-p','nativeweave-data-postgres','--release','--locked','--offline','--','--print=link-args'])
            run('fixture-release',['cargo','build','--manifest-path','tests/Data.Postgres/native/Cargo.toml','--release','--locked','--offline'])
            run_managed(args,output,run,native_env)
            host_preflight=True
        if not (args.write_reference or args.update_locks):
            for item in inputs:
                if sha(ROOT/item['path'])!=item['sha256']:raise RuntimeError('Source/lock changed during verification: '+item['path'])
        status='passed'
    except Exception as exc:
        (output/'failure.txt').write_text(str(exc)+'\n');print(str(exc),file=sys.stderr,flush=True)
    finally:
        for process,data,logfile in reversed(servers):
            subprocess.run([str(args.postgres_bin.resolve()/'pg_ctl'),'-D',str(data),'stop','-m','fast'],stdout=logfile,stderr=subprocess.STDOUT,env=env)
            try:process.wait(timeout=20)
            except subprocess.TimeoutExpired:process.kill();process.wait()
            logfile.close()
        result={'task':'B02','platform':'linux-x64','status':status,'commands':len(records),'native_only':args.native_only,'component_only':True,'host_preflight':host_preflight,'full_b04_host':False,'other_platforms_executed':[],'source_manifest_sha256':sha(output/'source-inputs.json') if (output/'source-inputs.json').exists() else None}
        (output/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
    return 0 if status=='passed' else 1

def run_managed(args,output,run,native_env):
    component=ROOT/'target/release/libnativeweave_data_postgres.so'
    asset=ROOT/'target/release/libnw_database_postgresql.so'
    if not asset.is_file():raise RuntimeError('Build the actual PostgreSQL Database Host before component/preflight verification.')
    fixture=ROOT/'tests/Data.Postgres/native/target/release/libnativeweave_postgres_fixture.so'
    msbuild=['-p:UseSharedCompilation=false','-nr:false','-m:1',f'-p:NativeWeavePostgresAssetPath={asset}']
    restore=(['--configfile',str(args.offline_config.resolve())] if args.offline_config else []) + ([] if args.update_locks else ['--locked-mode'])
    test='tests/Data.Postgres/NativeWeave.Database.PostgreSql.Tests.csproj'
    checker='tests/Data.Postgres/ApiCheck/ApiCheck.csproj'
    sample='samples/api/data-postgres/PostgresExample.csproj'
    for label,project in [('test',test),('api',checker),('sample',sample)]:
        run(label+'-restore',['dotnet','restore',project,*restore,*msbuild])
        run(label+'-build',['dotnet','build',project,'-c','Release','--no-restore',*msbuild])
    run('managed-whitespace',['dotnet','format','whitespace','.', '--folder','--verify-no-changes','--include',
                             'tests/Data.Postgres/Program.cs','tests/ProviderProfileChecks.cs','samples/api/data-postgres/Program.cs','--verbosity','quiet'])
    run('exact-api-xml-reference',['dotnet',str(ROOT/'tests/Data.Postgres/ApiCheck/bin/Release/net11.0/ApiCheck.dll'),str(ROOT),os.environ['DOTNET_ROOT'],str(ROOT/'src/Data.Postgres/bin/Release/net11.0/NativeWeave.Database.PostgreSql.dll'),*(['--write'] if args.write_reference else [])])
    native_env=native_env|{'NW_PG_COMPONENT_ASSET':str(component),'NW_PG_HOST_ASSET':str(asset),'LD_LIBRARY_PATH':str(fixture.parent)+':'+os.environ.get('LD_LIBRARY_PATH','')}
    run('managed-jit',['dotnet',str(ROOT/'tests/Data.Postgres/bin/Release/net11.0/NativeWeave.Database.PostgreSql.Tests.dll')],native_env|{'NW_PG_REPORT':str(output/'jit-report.json'),'NW_PG_OPTION_RECORD':str(output/'jit-options.bin')})
    run('sample-jit',['dotnet',str(ROOT/'samples/api/data-postgres/bin/Release/net11.0/PostgresExample.dll')],native_env)
    for label,project,name in [('test',test,'NativeWeave.Database.PostgreSql.Tests'),('sample',sample,'PostgresExample')]:
        destination=output/(label+'-aot')
        run(label+'-aot-restore',['dotnet','restore',project,'-r','linux-x64','-p:PublishAot=true',*restore,*msbuild])
        if label=='test':
            run('aot-linker-selection',['dotnet','msbuild',test,'-nologo','-t:ResolveReferences,SetupOSSpecificProps','-p:Configuration=Release','-p:RuntimeIdentifier=linux-x64','-p:PublishAot=true','-getProperty:CppCompilerAndLinker,CppLinker,LinkerFlavor',*msbuild])
        run(label+'-aot-publish',['dotnet','publish',project,'-c','Release','-r','linux-x64','-p:PublishAot=true','--no-restore','-o',destination,*msbuild])
        run(label+'-aot-run',[destination/name,*(['--require-aot'] if label=='test' else [])],native_env|{'NW_PG_REPORT':str(output/(label+'-aot-report.json')),'NW_PG_OPTION_RECORD':str(output/(label+'-aot-options.bin'))})
    generated=[]
    for path in (ROOT/'src/Data.Postgres/obj').rglob('*'):
        if path.is_file() and (path.name=='PostgreSqlAssetIdentity.g.cs' or path.name=='NativeWeave.database.postgresql.assets.json'):
            generated.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path),'content':path.read_text()})
    (output/'generated-asset-inputs.json').write_text(json.dumps(generated,indent=2)+'\n')
    for location in [ROOT/'tests/Data.Postgres/bin/Release/net11.0',output/'test-aot',output/'sample-aot']:
        record=json.loads((location/'NativeWeave.database.postgresql.assets.json').read_text())
        if (record['engineId']!='database.postgresql' or record['packageId']!='NativeWeave.Database.PostgreSql'
            or record['sourcePath']!=record['outputPath'] or record['outputPath']!='runtimes/linux-x64/native/libnw_database_postgresql.so'
            or record['sha256']!=sha(asset) or sha(location/record['outputPath'])!=sha(asset)):
            raise RuntimeError('Actual PostgreSQL Host asset record/hash differs from the staged Host.')
    paths=[component,asset,fixture,ROOT/'src/Data.Postgres/bin/Release/net11.0/NativeWeave.Database.PostgreSql.dll',output/'test-aot/NativeWeave.Database.PostgreSql.Tests',output/'sample-aot/PostgresExample']
    (output/'artifacts.json').write_text(json.dumps([{'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size} for p in paths],indent=2)+'\n')
if __name__=='__main__':raise SystemExit(main())
