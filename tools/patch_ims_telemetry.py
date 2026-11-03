#!/usr/bin/env python3
"""Add the tested MediaTek IMS telemetry compatibility class on the host only."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import tempfile
import zipfile

APK_SHA256 = 'd5847d81ba07f5d1d1d0475e5768f7e675986727fa731608fe4364420f536ec7'
SIGNER_SHA256 = 'c8a2e9bccf597c2fb6dc66bee293fc13f2fc47ec77bc6b2b0d52c11f51192ab8'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def run(arguments):
    result = subprocess.run([str(value) for value in arguments], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError('Build-tool operation failed: ' + str(arguments[0]))
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['apk', 'android-jar', 'd8-jar', 'key', 'cert', 'output']:
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.resolve() == args.apk.resolve():
        raise ValueError('Choose a new output file; the input APK is preserved')
    if sha(args.apk) != APK_SHA256:
        raise ValueError('Input differs from the exact upstream APK tested in this port')
    certificate = run(['apksigner', 'verify', '--print-certs', args.apk])
    if 'certificate SHA-256 digest: ' + SIGNER_SHA256 not in certificate:
        raise ValueError('Unexpected input signing certificate')
    source = Path(__file__).resolve().parents[1] / 'patches/ims/src/com/android/internal/telephony/metrics/TelephonyMetrics.java'
    with tempfile.TemporaryDirectory(prefix='g54-ims-compat-') as directory:
        work = Path(directory)
        classes, dex = work / 'classes', work / 'dex'
        classes.mkdir(); dex.mkdir()
        run(['javac', '--release', '8', '-d', classes, source])
        run(['jar', 'cf', work / 'compat.jar', '-C', classes, '.'])
        run(['java', '-cp', args.d8_jar, 'com.android.tools.r8.D8', '--lib', args.android_jar,
             '--min-api', '33', '--output', dex, work / 'compat.jar'])
        with zipfile.ZipFile(args.apk) as original, zipfile.ZipFile(work / 'unsigned.apk', 'w') as patched:
            if 'classes2.dex' in original.namelist():
                raise ValueError('Unexpected multidex input')
            for entry in original.infolist():
                if re.fullmatch(r'META-INF/(?:MANIFEST\.MF|[^/]+\.(?:SF|RSA|DSA|EC))', entry.filename, re.I):
                    continue
                patched.writestr(entry, original.read(entry.filename))
            patched.write(dex / 'classes.dex', 'classes2.dex')
        run(['zipalign', '-f', '4', work / 'unsigned.apk', work / 'aligned.apk'])
        # Key/certificate paths are explicit inputs. No keys are copied, printed,
        # generated, downloaded, or embedded in this repository or the result.
        run(['apksigner', 'sign', '--key', args.key, '--cert', args.cert,
             '--out', args.output, work / 'aligned.apk'])
        certificate = run(['apksigner', 'verify', '--print-certs', args.output])
        if 'certificate SHA-256 digest: ' + SIGNER_SHA256 not in certificate:
            raise ValueError('Output signer must match the tested GSI platform certificate')
        with zipfile.ZipFile(args.apk) as original, zipfile.ZipFile(args.output) as patched:
            for name in original.namelist():
                if not name.startswith('META-INF/') and original.read(name) != patched.read(name):
                    raise ValueError('Original vendor payload changed')
            if patched.read('classes2.dex') != (dex / 'classes.dex').read_bytes():
                raise ValueError('Compatibility DEX verification failed')
    print(json.dumps({'output_filename': args.output.name, 'sha256': sha(args.output),
                      'signer_sha256': SIGNER_SHA256,
                      'original_manifest_code_and_libraries_preserved': True,
                      'device_operations_performed': False}, indent=2))


if __name__ == '__main__':
    main()
