# Scope of the published patches

The files here make the successful configuration reviewable. They are not a complete reproducible r6 build pipeline and are not a flashable release. No handset-specific boot image, proprietary trustlet, recovery image, or signing key is distributed.

| File | Purpose |
| --- | --- |
| `patches/vintf/compatibility_matrix.6.xml` | Legacy FCM6 requirements used in the preparation stage |
| `patches/vintf/compatibility_matrix.g54.xml` | Exact additional G54 HAL instances from the tested native contract |
| `patches/selinux/202504-camera-compat.cil` | Three native camera-property compatibility declarations |
| `patches/selinux/trustonic-mount.cil` | Scoped init permission needed for the registry mount |
| `patches/init/00-g54-trustonic-registry.rc` | Tested two-stage r6 registry and persistent-storage setup |
| `tools/patch_vintf_candidate.py` | Host-only VINTF preparation stage; **not the final r6 builder** |
| `evidence/validation.json` | Curated, non-identifying result summary |

The `.rc` file refers to native trustlet filenames. These are common software identifiers for that vendor set, not per-device secrets. Supply your own matching vendor files locally; the repository contains none of their binary contents.

## Pinned inputs

Upstream release: [eyzner/LineageOS-GSI, lineage-24.0-20261029](https://github.com/eyzner/LineageOS-GSI/releases/tag/lineage-24.0-20261029).

Asset: `lineage-24.0-20261029-UNOFFICIAL-arm64_bvN.img.xz`.

The public checksums are in [checksums.json](../evidence/checksums.json). The raw base size is 2,400,296,960 bytes. Use the non-EROFS asset matching those checksums. Do not silently substitute a newer base: its libraries, policy, compatibility requirements, and patch offsets need separate review.

The VINTF preparation tool requires Python 3, `debugfs`, `e2fsck`, AOSP `avbtool`, the matching FEC tool, and the upstream **publicly distributed development test key**. Supply that key locally from AOSP; no key file is included here. This is development signing, not an OEM signature.

For that preparation stage only:

```sh
python3 tools/patch_vintf_candidate.py \
  --base /path/to/upstream-system.img \
  --matrix patches/vintf/compatibility_matrix.6.xml \
  --device-matrix patches/vintf/compatibility_matrix.g54.xml \
  --avbtool /path/to/avbtool.py \
  --test-key /path/to/aosp-development-test-key.pem \
  --fec /path/to/fec \
  --output /path/to/vintf-stage-only.img
```

The script operates on regular local files, pins the upstream base and patch inputs, preserves build-version properties, and verifies file readback, contexts, filesystem, and rebuilt AVB data. It does not contact a phone or flash partitions. Its output is an intermediate; do not install it as the working r6 port.

## Remaining integration stages

The successful system also integrated the camera compatibility mapping and Trustonic configuration/policy, updated the policy cache stamp to match the actual inputs, preserved relevant filesystem metadata, and rebuilt/verified AVB and FEC. The early kernel control and paired boot integration were separate requirements. The tested image retained bounded init diagnostics.

Those stages must be implemented and validated against the owner's actual system and boot chain. Adding a CIL fragment without regenerating matching policy metadata is insufficient. So is applying the kernel control after the guest linker has already failed. The small files in this repository do not capture every diagnostic binary modification used in the experiment; consequently no byte-identical rebuild claim is made.

For an inactive DSU system update, use the native image-manager API, verify the exact image name/size and disabled state, and leave the guest userdata image unmapped. Back up the existing system, verify the full write and a remap readback, and verify unchanged DSU LP metadata before enabling it. Do not reuse another handset's device-mapper path; it is allocated dynamically.

See [PORTING_NOTES.md](PORTING_NOTES.md) for the evidence behind each change and [INSTALLATION.md](INSTALLATION.md) for the actual validation boundary.
