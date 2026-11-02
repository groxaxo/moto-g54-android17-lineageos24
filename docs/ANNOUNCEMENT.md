An experimental Android 17 / LineageOS 24 GSI result is now documented for **Moto G54 5G XT2343-2 (`cancunf`)**.

On one handset, persistent DSU reached setup and the home screen, retained the original Android 16 system/data, and successfully unlocked its separate encrypted guest data with a PIN after a normal reboot. Android 17 / API 37, Enforcing SELinux, and validated Wi-Fi were observed.

The notes explain the legacy VINTF requirements, the early page-size migration workaround on the tested custom kernel, the missing camera property mapping, AVB pairing, and the Trustonic storage fixes needed for persistent credentials. Small reusable configuration patches and a VINTF-only host preparation tool are included.

**This release contains documentation and patch fragments, not flashable ROM or boot images.** It is not a complete r6 build pipeline or official G54 support. The tested starting system was already rooted/unlocked and used a custom kernel. Other variants and stock kernels are unverified. `kiev` firmware is for a different device.

**Cellular remains unresolved: the device shows “No service.”** Calls, mobile data, camera, media, biometrics and other hardware are not claimed fully working. Please include the exact hardware/build combination when reporting further results, and follow the repository's privacy guidance before sharing diagnostics.
