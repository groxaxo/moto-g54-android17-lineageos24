# Installation and recovery notes

This is the workflow used in the experiment, not a stock-to-Android-17 installer. There is no flashable r6 download in this repository. The included VINTF tool stops at an earlier preparation stage; it does not assemble the working boot chain or final system image.

## Establish your own baseline

The tested device was XT2343-2 / `cancunf`, already rooted and unlocked, running Android 16 with a custom 5.10.240-DragonHeart kernel. Stock firmware, other kernels, and other variants have not been validated.

Use your own USB serial locally. These commands read identity and state; do not post their full output publicly:

```sh
adb -s "$G54_SERIAL" shell getprop ro.boot.hardware.sku
adb -s "$G54_SERIAL" shell getprop ro.product.device
adb -s "$G54_SERIAL" shell getprop ro.build.version.release
adb -s "$G54_SERIAL" shell getprop ro.build.version.sdk
adb -s "$G54_SERIAL" shell getprop ro.boot.slot_suffix
adb -s "$G54_SERIAL" shell uname -r
adb -s "$G54_SERIAL" shell getenforce
```

Resolve a hardware mismatch before proceeding. In particular, `kiev` installation instructions and firmware do not describe this `cancunf` target.

Back up personal data independently and keep your own verified recovery boot chain. Preserve both slots' relevant boot metadata and the original system/vendor layout. A firmware backup is not a personal-data backup. Ensure USB ADB and bootloader access work before changing boot images. Network-only access can disappear when a separate guest profile starts.

## Prepare the compatible images

Use the checksum-pinned upstream base and the stages described in [BUILDING.md](BUILDING.md) and [PORTING_NOTES.md](PORTING_NOTES.md). Preserve the G54's vendor, radio, calibration, and kernel. A different phone's firmware is not a replacement for these components.

Review the kernel control, legacy hardware contract, camera mapping, Trustonic storage, and matching boot/vbmeta chain together. Updating only one of these was insufficient in the failed trials. Do not copy boot images from the test handset or assume its binary patch offsets, rollback values, or signing state match yours.

Verify filesystem integrity, AVB descriptors/signatures/hashtree, expected file contexts, and full image hashes before staging. Passing those checks does not establish complete hardware compatibility.

## Stage through DSU

The successful installation used a non-sparse ext4 system image and a separate 8 GiB guest data allocation in the standard DSU slot `dsu`. Follow [AOSP's DSU documentation](https://source.android.com/docs/core/ota/dynamic-system-updates) for the supported frontend and allocation requirements on your starting system. Install only an image you have finished reviewing; the upstream unpatched base and the VINTF-only intermediate are not the successful r6 image.

The experiment required an early boot integration for the existing kernel and a matching active-slot boot/vbmeta pair. It therefore involved more than selecting a GSI in DSU Loader. The bootloader did not implement temporary `fastboot boot`; another owner's recovery route may differ.

Once a compatible guest is installed and running, the tested build supports:

```sh
adb -s "$G54_SERIAL" shell gsi_tool status
adb -s "$G54_SERIAL" shell gsi_tool enable --dsuslot dsu
```

Enabling the installed guest persistently makes normal restarts enter it. It does not repair an incompatible image. Review the local tool's help and current slot before changing its state.

## Verify the result

Complete setup and choose your own credential on the phone. Then perform a normal restart and unlock it again. Check:

```sh
adb -s "$G54_SERIAL" shell getprop ro.build.version.release
adb -s "$G54_SERIAL" shell getprop ro.build.version.sdk
adb -s "$G54_SERIAL" shell getprop sys.boot_completed
adb -s "$G54_SERIAL" shell settings get global device_provisioned
adb -s "$G54_SERIAL" shell settings get secure user_setup_complete
adb -s "$G54_SERIAL" shell am get-started-user-state 0
adb -s "$G54_SERIAL" shell gsi_tool status
adb -s "$G54_SERIAL" shell getenforce
```

The observed values were `17`, `37`, three setup/boot values of `1`, `RUNNING_UNLOCKED`, an enabled/running DSU, and `Enforcing`. A normal restart, successful credential entry, and unlocked encrypted data are stronger checks than reaching the setup screen once.

The lock screen used a short display-on interval during automation. Shared storage was unavailable before the first credential unlock. Those conditions interrupted UI inspection; they were not proof of another firmware boot failure. Enter credentials directly on the device and keep them out of terminal commands and reports.

## Recover

Keep DSU's guest data distinct from the original profile. In the tested arrangement, disabling DSU before returning to the original system was important. Restore only your own verified matching boot/vbmeta pair if boot changes need to be reversed. Use the appropriate active slot and device-specific procedure; no generic flashing loop is provided here.

Discarding a DSU installation removes its separate guest data. Do not discard it as a troubleshooting shortcut when preserving that data matters. Do not erase userdata, reset hardware credential storage, overwrite vendor/radio/calibration partitions, or relock the bootloader to work around these failures.
