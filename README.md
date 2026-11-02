# Android 17 / LineageOS 24 on Moto G54 5G

Experimental port notes and reusable configuration patches for **Moto G54 5G, XT2343-2, codename `cancunf`**.

One device booted the unofficial LineageOS 24 Android 17 GSI, completed setup, saved a PIN, and unlocked its encrypted guest data after a normal restart. The installation uses **persistent Dynamic System Updates (DSU)** with **8 GiB of separate guest userdata**. The existing Android 16 system and data were retained.

**This is a research and documentation release, not a downloadable ROM or a universal installer. Cellular service is unresolved: the tested device shows “No service.”** Compatibility with other G54 variants and stock kernels is unverified. Do not use `kiev` firmware: it is a different device.

| Item | Observed result |
| --- | --- |
| Tested hardware | XT2343-2 / `cancunf` only |
| Starting system | Existing rooted Android 16 installation |
| Retained kernel | 5.10.240-DragonHeart; compressed kernel bytes unchanged |
| Guest | Unofficial LineageOS `24.0-20261029`, Android 17 / API 37 |
| Installation | Persistent DSU, slot `dsu`, separate 8 GiB guest data |
| Boot and setup | Completed; setup flags both `1` |
| Normal restart | Returned to Android 17 with setup and guest app retained |
| PIN and encrypted data | PIN saved; post-restart unlock reached `RUNNING_UNLOCKED` |
| SELinux | Enforcing |
| Wi-Fi | Connected and validated |
| Cellular | SIM loaded, **No service**; prior service baseline unknown |
| Calls / mobile data / IMS | Not validated |
| Camera / media / biometrics / Bluetooth / NFC | Not fully validated |
| CTS / VTS / Play Integrity | Not validated |

The base is [eyzner's LineageOS-GSI release dated 2026-10-29](https://github.com/eyzner/LineageOS-GSI/releases/tag/lineage-24.0-20261029), asset `lineage-24.0-20261029-UNOFFICIAL-arm64_bvN.img.xz`. This project does not claim official LineageOS support for the G54.

Read these before attempting a port:

- [Installation and recovery](docs/INSTALLATION.md): prerequisites, DSU workflow, and verification.
- [What fixed the boot and PIN failures](docs/PORTING_NOTES.md): kernel control, VINTF, SELinux mapping, AVB, and Trustonic storage.
- [Using the published patches](docs/BUILDING.md): exact scope of the included files and the incomplete build stages.
- [Privacy and bug reports](PRIVACY.md): what to keep out of public reports.
- [Sources and licensing](CREDITS.md).

The repository includes the tested init configuration, small CIL patches, VINTF matrices, a host-only VINTF preparation tool, and an allowlisted result summary. It excludes boot/vbmeta images, ROM binaries, vendor trustlet binaries, raw logs, screenshots, backups, and credentials. The VINTF tool alone does **not** produce the successful final image.

The retained original system is a recovery option, not a guarantee against data loss. This experiment also changed the active boot/vbmeta pair to support the existing kernel and the guest. DSU's separate userdata does not remove the need for device-specific boot-chain review and independent backups. [AOSP documents DSU's design and requirements](https://source.android.com/docs/core/ota/dynamic-system-updates).

For reports from other owners, state the exact model/SKU, codename, starting firmware, kernel, and GSI version. Report boot success separately from cellular and hardware functionality. Follow [PRIVACY.md](PRIVACY.md) before attaching any diagnostic information.
