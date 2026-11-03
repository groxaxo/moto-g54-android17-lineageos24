# Sources and licensing

The guest image is [eyzner/LineageOS-GSI, lineage-24.0-20261029](https://github.com/eyzner/LineageOS-GSI/releases/tag/lineage-24.0-20261029). Credit for the underlying Android and LineageOS work belongs to those projects and the GSI maintainer. This repository is an independent experiment and is not an official LineageOS device release.

Primary technical references:

- [TrebleDroid IMS selection and settings](https://github.com/TrebleDroid/treble_app/blob/master/app/src/main/java/me/phh/treble/app/ImsSettings.kt). The upstream MediaTek IMS APK is obtained separately; its binaries are not redistributed.
- [AOSP platform-signed shared UID configuration](https://source.android.com/docs/core/permissions/platform-signed-shared-uid-allowlist).
- [SzponerZoli/crdroid-vienna TelephonyMetrics compatibility approach](https://github.com/SzponerZoli/crdroid-vienna/blob/main/patches/frameworks-opt-telephony-telephonymetrics-stub.patch). Required method signatures were independently checked against the tested APK.

- [AOSP Dynamic System Updates](https://source.android.com/docs/core/ota/dynamic-system-updates): separate guest storage, installation requirements, and Gatekeeper user-ID separation.
- [LineageOS legacy FCM6 source](https://github.com/LineageOS/android_hardware_interfaces/blob/lineage-23.2/compatibility_matrices/compatibility_matrix.6.xml): genuine compatibility requirements used in the VINTF preparation stage. The included generated matrix also merges corresponding Android kernel-configuration requirements; its original build-relative input comment is preserved.
- [Android common kernel page-size migration control](https://android.googlesource.com/kernel/common/+/f95a7a078f33019fff405218e8bb5eb35b4df54e/mm/pgsize_migration.c): definition of the sysfs control used with the tested kernel.
- [AOSP AVB](https://android.googlesource.com/platform/external/avb/): image descriptors, verification tools, and development test data.
- [AOSP init language](https://android.googlesource.com/platform/system/core/+/refs/heads/main/init/README.md): init actions and mount ordering.

The device-specific HAL fragment was generated from the tested native G54 hardware contract. The three camera mapping declarations were recovered from its working native compatibility mapping. Native binaries are not redistributed. The Trustonic analysis concerns observed behavior on the tested combination; the vendor daemon was not modified or published.

New documentation, the host-only preparation tool, and newly authored configuration are licensed under [MIT](LICENSE). The generated legacy matrix at `patches/vintf/compatibility_matrix.6.xml` incorporates AOSP/LineageOS hardware-interface material under [Apache License 2.0](LICENSES/Apache-2.0.txt); that exception is not relicensed by this repository's MIT license. The newly authored `patches/ims/src/.../TelephonyMetrics.java` compatibility class is also provided under Apache-2.0 as marked by its SPDX identifier. Original upstream notices and licenses continue to apply to software obtained separately for a build.

There are no OEM production keys, personal signing keys, proprietary trustlet binaries, original handset boot images, or recovery backups in this repository.
