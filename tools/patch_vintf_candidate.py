#!/usr/bin/env python3
"""Build a G54 compatibility candidate from a checksum-pinned LineageOS 24 GSI.

This operates on regular image files only. It does not communicate with a phone,
flash partitions, change Android's reported version, or modify vendor firmware.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

BASE_SHA256 = 'b200c87fa58aaa24bb1299b0e3c624a0a7421d9b86872f2476722f95f67c9df0'
MATRIX_SHA256 = 'a58b9c5a7611b7547ee79ed04a11317160b067488c072ba42efdd9c2f6f0f583'
DEVICE_MATRIX_SHA256 = 'b067a730489d830921d84f7e25fa7bf3e60f6de320b1457a257a9e7d6f8d768c'
PUBLIC_KEY_SHA1 = 'cdbb77177f731920bbe0a0f94f84d9038ae0617d'
PARTITION_SIZE = 2400296960
MATRIX_PATH = '/system/etc/vintf/compatibility_matrix.6.xml'
DEVICE_MATRIX_PATH = '/system/etc/vintf/compatibility_matrix.g54.xml'
META_PATH = '/system/etc/g54-lineage24-port.json'

def digest(path, algorithm='sha256'):
    h = hashlib.new(algorithm)
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()

def dq(path):
    value = str(path)
    if any(c in value for c in '\\"\n\r'):
        raise ValueError('Unsupported character in a debugfs path')
    return '"' + value + '"'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--matrix', type=Path, default=Path(__file__).with_name('compatibility_matrix.6.xml'))
    parser.add_argument('--device-matrix', type=Path, default=Path(__file__).with_name('compatibility_matrix.g54.xml'))
    parser.add_argument('--avbtool', type=Path, required=True)
    parser.add_argument('--test-key', type=Path, required=True)
    parser.add_argument('--fec', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    for name in ['base', 'matrix', 'device_matrix', 'avbtool', 'test_key', 'fec']:
        path = getattr(args, name).resolve(strict=True)
        if not stat.S_ISREG(path.stat().st_mode):
            raise ValueError('All inputs must be regular files')
        setattr(args, name, path)
    output = args.output.resolve()
    if output.exists() or output.with_suffix(output.suffix + '.json').exists():
        raise FileExistsError('Refusing to overwrite an existing output')
    if args.base.stat().st_size != PARTITION_SIZE or digest(args.base) != BASE_SHA256:
        raise ValueError('Base image does not match the verified Android 17 release')
    if digest(args.matrix) != MATRIX_SHA256:
        raise ValueError('Legacy matrix does not match the reviewed G54/LineageOS data')
    if digest(args.device_matrix) != DEVICE_MATRIX_SHA256:
        raise ValueError('Device matrix does not match the reviewed exact G54 HAL instances')
    matrix = ET.parse(args.matrix).getroot()
    if matrix.get('type') != 'framework' or matrix.get('level') != '6' or not matrix.findall('kernel'):
        raise ValueError('Missing authentic FCM6/kernel requirements')
    device_matrix = ET.parse(args.device_matrix).getroot()
    if device_matrix.get('type') != 'framework' or len(device_matrix.findall('hal')) != 24:
        raise ValueError('Expected 24 exact native G54 HAL declarations')
    if args.fec.name != 'fec' or not os.access(args.fec, os.X_OK):
        raise ValueError('A working upstream fec executable is required')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.g54-port-', dir=output.parent) as temporary:
        work = Path(temporary)
        image = work / 'system.img'
        env = dict(os.environ)
        env['PATH'] = str(args.fec.parent) + os.pathsep + env['PATH']
        env['TMPDIR'] = str(work)

        def run(command):
            result = subprocess.run(command, env=env, capture_output=True, text=True, check=True)
            return result.stdout

        def avb(*arguments):
            return run([sys.executable, str(args.avbtool), *arguments])

        def debug(command, write=False):
            return run(['debugfs', *(['-w'] if write else []), '-R', command, str(image)])

        public_key = work / 'test-key.avbpubkey'
        avb('extract_public_key', '--key', str(args.test_key), '--output', str(public_key))
        if digest(public_key, 'sha1') != PUBLIC_KEY_SHA1:
            raise ValueError('The development signing key must match the base image public key')
        shutil.copyfile(args.base, image)
        print(avb('verify_image', '--image', str(image)), flush=True)
        build_prop = debug('cat /system/build.prop')
        for key, expected in [('ro.system.build.version.release', '17'), ('ro.system.build.version.sdk', '37')]:
            if not re.search(r'^' + re.escape(key) + '=' + expected + r'$', build_prop, re.M):
                raise ValueError('The actual framework is not Android 17 / API 37')
        if debug('stat ' + MATRIX_PATH).strip():
            raise ValueError('Base already contains an FCM6 file; review this new base separately')
        if debug('stat ' + DEVICE_MATRIX_PATH).strip():
            raise ValueError('Base already contains a G54 fragment; review this new base separately')
        label = work / 'system-file.selinux'
        debug('ea_get -f ' + dq(label) + ' /system/etc/vintf/compatibility_matrix.7.xml security.selinux')
        if label.read_bytes() != b'u:object_r:system_file:s0\0':
            raise ValueError('Unexpected existing SELinux context')
        metadata = {
            'patch': 'g54-lineage24-fcm6-r2', 'created_utc': datetime.now(timezone.utc).isoformat(),
            'target': {'device': 'cancunf', 'sku': 'XT2343-2'},
            'base': 'eyzner/LineageOS-GSI lineage-24.0-20261029 arm64_bvN',
            'android': 17, 'sdk': 37, 'base_raw_sha256': BASE_SHA256,
            'matrix_sha256': MATRIX_SHA256,
            'device_matrix_sha256': DEVICE_MATRIX_SHA256,
            'device_hal_packages': 24, 'device_hal_instances': 70,
            'hardware_policy': 'G54 kernel, vendor drivers, radio and calibration are retained',
            'upstream_legacy_requirements': 'LineageOS/android_hardware_interfaces lineage-23.2 FCM6',
            'reference_android17_device': 'LineageOS Google Pixel 4 XL / coral 24.0',
            'reference_commit': '54913ec2b6e46e9d8d09ae21a15a3d1f7ca634dc',
            'device_boot_verified': False,
        }
        metadata_file = work / 'port.json'
        metadata_file.write_text(json.dumps(metadata, indent=2) + '\n')
        avb('erase_footer', '--image', str(image))
        for source, target in [(args.matrix, MATRIX_PATH), (args.device_matrix, DEVICE_MATRIX_PATH), (metadata_file, META_PATH)]:
            debug('write ' + dq(source) + ' ' + target, write=True)
            for field, value in [('uid', '0'), ('gid', '0'), ('mode', '0100644')]:
                debug(f'set_inode_field {target} {field} {value}', write=True)
            debug('ea_set -f ' + dq(label) + ' ' + target + ' security.selinux', write=True)
            readback = work / (source.name + '.readback')
            debug('dump ' + target + ' ' + dq(readback))
            if digest(readback) != digest(source):
                raise ValueError('Filesystem readback differs from the reviewed input')
            context = work / (source.name + '.context')
            debug('ea_get -f ' + dq(context) + ' ' + target + ' security.selinux')
            if context.read_bytes() != label.read_bytes():
                raise ValueError('SELinux file context was not preserved')
        if debug('cat /system/build.prop') != build_prop:
            raise ValueError('Framework version/build properties changed unexpectedly')
        run(['e2fsck', '-f', '-n', str(image)])
        print('Filesystem and exact file-label/readback checks passed; rebuilding AVB and FEC.', flush=True)
        avb('add_hashtree_footer', '--image', str(image), '--partition_name', 'system',
            '--partition_size', str(PARTITION_SIZE), '--algorithm', 'SHA256_RSA2048',
            '--key', str(args.test_key), '--hash_algorithm', 'sha256', '--fec_num_roots', '2',
            '--salt', '422ce824bc4f88238f6e896edb329f8c61b8884436dffe44a25b5c8f62bc0baa',
            '--rollback_index', '1790812800', '--rollback_index_location', '0',
            '--prop', 'com.android.build.system.os_version:17',
            '--prop', 'com.android.build.system.fingerprint:google/generic_system/generic:17/CP2A.260605.016/eng.michae:userdebug/test-keys',
            '--prop', 'com.android.build.system.security_patch:2026-10-01')
        print(avb('verify_image', '--image', str(image)), flush=True)
        if image.stat().st_size != PARTITION_SIZE:
            raise ValueError('The DSU partition size changed')
        metadata['output_raw_sha256'] = digest(image)
        metadata['filesystem_and_avb_verified'] = True
        metadata['signing'] = 'Existing public AOSP development key; not an OEM release signature'
        os.chmod(image, 0o600)
        os.link(image, output)
        with output.with_suffix(output.suffix + '.json').open('x') as receipt:
            json.dump(metadata, receipt, indent=2)
            receipt.write('\n')
        print(json.dumps({'image': str(output), 'sha256': metadata['output_raw_sha256']}), flush=True)

if __name__ == '__main__':
    main()
