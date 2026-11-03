# What changed

These observations came from one XT2343-2 running an existing Android 16 system and a 5.10.240-DragonHeart kernel. They are not evidence that every Moto G54 needs the same changes.

## Existing kernel and Android 17's loader

Executing the Android 17 linker against guest-backed libraries reproducibly caused a restart. Identical copied library bytes executed successfully. The failure was narrowed to optional ELF-padding `madvise(MADV_DONTNEED)` behavior with page-size migration enabled.

Writing `0` to `/sys/kernel/mm/pgsize_migration/enabled` made the guest-backed linker and SELinux compiler complete on the tested kernel. This is a real kernel control, described in [Android common kernel source](https://android.googlesource.com/kernel/common/+/f95a7a078f33019fff405218e8bb5eb35b4df54e/mm/pgsize_migration.c). Its presence and behavior must be checked on a different kernel.

The working boot integration applied the control before the guest linker started. A short-lived child used a private mount namespace; the parent that became PID 1 retained its original namespace. An earlier wrapper that altered PID 1's mount environment was unsuitable. A guest init `.rc` command alone runs too late to fix an earlier linker failure.

The tested boot image also retained bounded diagnostic hooks. Its binary offsets and boot metadata are specific to that original image. Neither the image nor a universal boot patcher is distributed here. The compressed kernel itself was unchanged.

## VINTF compatibility

The generic Android 17 framework lacked the older FCM level 6 requirements needed by the existing G54 vendor stack. The preparation stage restored genuine legacy requirements and added a device fragment containing 24 HAL packages and 70 exact instances derived from the working native device matrix.

The included matrices preserve named requirements rather than replacing the hardware contract with wildcard acceptance. `checkvintf` was evaluated with the actual vendor/ODM manifests, kernel configuration, and package-derived APEX metadata. It reported compatible for that combination. This is a contract check, not a functional test of each HAL.

## Camera property mapping and SELinux

The guest was missing the native `vendor_persist_camera_prop_202504` compatibility mapping. Restoring the three declarations in `patches/selinux/202504-camera-compat.cil` allowed init to pass all 621 checked property accesses with zero remaining denials in that check.

The runtime policy compiled with the actual vendor policy and the options used by Android init. A stricter neverallow check **did not pass**: baseline and patched policy had the same inherited failures, with no new violations in the comparison. Do not describe this as a clean strict-policy result. No permissive domain was added, and the running device remained Enforcing.

## AVB and boot pairing

An edited boot image must have matching boot descriptors and a valid matching vbmeta signature for that boot chain. Editing verification flags without repairing authentication and descriptors was insufficient. The tested device was already unlocked and used development signing material; existing flags and rollback values were retained.

No OEM production signature was created. Enforcing SELinux does not imply stock Verified Boot, CTS, or Play Integrity. The tested bootloader rejected `fastboot boot`, so recovery required an already-verified pair flashed to the active boot/vbmeta partitions. Other owners must prepare their own recovery pair.

## Trustonic registry and persistent credentials

On this combination of secure hardware and GSI test-key build tags, the native daemon looked for trustlets and fallback storage under `/mnt/vendor/tzapp`. The usable native code was under `/vendor/app/mcRegistry`.

Revision r4 exposed the native registry with a read-only bind. Android 17 booted, but PIN enrollment failed when the daemon tried to create `TbStorage/Store_0.tf` on that read-only filesystem.

Revision r5 supplied links on tmpfs and put `TbStorage` in guest userdata. That still failed: the daemon checks the parent filesystem and explicitly rejects `TMPFS_MAGIC` (`0x01021994`). The native check was confirmed by logs and offline inspection; the daemon binary was not modified.

The successful **r6** configuration is `patches/init/00-g54-trustonic-registry.rc`:

1. At `post-fs`, make native code available through links on an early temporary mount.
2. At `post-fs-data`, prepare the registry and secure storage in private guest F2FS userdata.
3. Unmount the early tmpfs and bind the private disk-backed registry to `/mnt/vendor/tzapp`.
4. Relabel the individual code/storage links through the target path while retaining the writable data labels on the actual secure-storage directory.

The daemon then saw F2FS, PIN enrollment succeeded, and the same credential unlocked guest encrypted data after a normal reboot. Native trustlet contents and vendor firmware were unchanged. The scoped `init` mount permission included here was inherited from the registry fix; r6 required no additional policy permission.

The native code names in the init file are software identifiers, not unique device identifiers. This list is specific to the tested vendor set. Verify your own files and policy before reusing it.

## Data and verification

System-only revisions used Android's native image manager to map only the inactive `system_gsi` image. Guest userdata was not recreated. Independent backups, complete write/readback hashes, remap readback, and unchanged DSU LP metadata were checked before booting.

DSU's credential user-ID separation was preserved. AOSP notes that a GSI adds an offset to Gatekeeper user IDs; an empty shell read of a restricted GSI property is not proof that this separation is absent. Do not disable the isolation or reset shared secure storage to work around a credential failure.

The final result is limited to [the published validation summary](../evidence/validation.json). The later [cellular follow-up](CELLULAR.md) verifies LTE and IMS voice/SMS registration after restart; real calls/SMS remain untested and cellular HTTPS has not passed.
