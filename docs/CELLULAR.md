# LTE and IMS follow-up

On the tested XT2343-2, the original “No service” result was fixed. LTE registration and IMS registration with voice, SMS and UT capabilities survived a normal Android 17 restart and PIN unlock. This is narrower than a completed call or SMS test: neither was performed. Mobile internet remains unresolved; cellular-only DNS-based and fixed-IP HTTPS tests failed despite receiving a cellular network with routes and DNS servers. A reversible IPv4/IPv6 trial on the existing internet APN also failed; its original IPv4 protocol was restored. The active SIM's user-data enable setting was verified during that test.

The wider hardware matrix was collected on r6. This follow-up uses r7, which adds one system configuration file, plus a separately installed IMS APK and saved Treble settings. No new kernel, modem, vendor partition, radio identity or SELinux policy change was needed for this follow-up. The original Android 16 profile and the existing Android 17 guest data were retained.

## 1. The saved network preference excluded LTE

The active SIM's effective user network types contained GSM and WCDMA families, with no LTE or NR. Enabling LTE changed both voice and packet registration from out of service to HOME and cleared the recorded network rejection codes. The change persisted after restart.

Check the preferred network type in Android's SIM settings. Select a mode appropriate to your hardware and carrier that includes LTE. A 5G-capable setting does not establish that NR attachment has been tested: this experiment verified LTE only.

For a local diagnostic, the supported shell query is:

```sh
adb -s "$SERIAL" shell cmd phone get-allowed-network-types-for-users -s 0
```

Here `0` means the first physical slot. Determine the active slot on your own device. Do not copy a numerical network mask from another device or replace carrier restrictions with guesses.

## 2. The configured MediaTek IMS package was absent

The framework selected `com.mediatek.ims`, but that package was not installed. The native vendor exposed MediaTek `mtkradioex@3.0` IMS interfaces, and the MediaTek telephony overlay was already enabled.

[TrebleDroid's installer](https://github.com/TrebleDroid/treble_app/blob/master/app/src/main/java/me/phh/treble/app/ImsSettings.kt) selects `ims-mtk-u.apk` for a MediaTek R-or-newer vendor on Android 14 or later. The standard APK's signing certificate matched this unofficial GSI. The alternative PHH-resigned APK did not match this build's platform certificate and was not used.

The tested upstream artifact was obtained from `https://treble.phh.me/ims-mtk-u.apk`:

- Package: `com.mediatek.ims`, version code 33.
- APK SHA256: `d5847d81ba07f5d1d1d0475e5768f7e675986727fa731608fe4364420f536ec7`.
- Signing-certificate SHA256: `c8a2e9bccf597c2fb6dc66bee293fc13f2fc47ec77bc6b2b0d52c11f51192ab8`.

These identify the tested artifact, not every file that may later be served at that URL. Do not use the Qualcomm IMS packages for this MediaTek device.

## 3. Android required an explicit shared-UID entry

Normal installation initially returned `INSTALL_PARSE_FAILED_BAD_SHARED_USER_ID`: a non-preloaded platform-signed package was trying to join `android.uid.phone` without an explicit entry.

r7 adds [package-shareduid-g54-ims.xml](../patches/ims/package-shareduid-g54-ims.xml) to `/system/etc/sysconfig/`. It permits only `com.mediatek.ims` to join `android.uid.phone`. Signature verification remains enabled. The mechanism is documented in [AOSP's platform-signed shared UID guidance](https://source.android.com/docs/core/permissions/platform-signed-shared-uid-allowlist).

The system image was checked and its AVB metadata regenerated, then updated using the established data-preserving maintenance procedure. The exact installed image was independently backed up and hashed first. DSU had resized its ext4 filesystem during boot, so its raw bytes differed from the pre-install image; the first update guard correctly refused that mismatch before any write. A revised delta was verified in both directions against the actual backup, and complete system readback hashes were checked before and after remapping. Guest userdata was never mapped or recreated.

This repository does not provide that device-specific block updater. Its payloads are tied to exact private image hashes and must not be applied to another phone. See [INSTALLATION.md](INSTALLATION.md) for the existing boot-chain and recovery constraints.

## 4. The prebuilt IMS app referenced a removed logging class

After installation, startup failed with `NoClassDefFoundError` for `com.android.internal.telephony.metrics.TelephonyMetrics`. Inspection of the APK found five required entry points: `getInstance`, `writeOnRilSolicitedResponse`, `writeOnRilTimeoutResponse`, `writeRilSendSms`, and `writeRilAnswer`.

The [small compatibility class](../patches/ims/src/com/android/internal/telephony/metrics/TelephonyMetrics.java) supplies those legacy telemetry calls. Its logging operations are no-ops. It does not implement radio operations or change the vendor IMS logic. The same compatibility approach is documented in a [separate MediaTek Motorola port](https://github.com/SzponerZoli/crdroid-vienna/blob/main/patches/frameworks-opt-telephony-telephonymetrics-stub.patch); the exact signatures here were independently verified against the tested APK.

[patch_ims_telemetry.py](../tools/patch_ims_telemetry.py) is a host-only helper for this stage. It adds a new DEX containing the compatibility class, preserves the original manifest, DEX and native-library bytes, aligns the APK, and signs it with an explicitly supplied matching development key/certificate. The tested GSI uses the public AOSP platform development certificate. No owner or OEM production key is included or required by this experiment. A differently signed ROM needs its own matching integration; the tool does not disable signature checking.

Example host invocation, with local Android build-tool paths supplied explicitly:

```sh
python3 tools/patch_ims_telemetry.py \
  --apk ims-mtk-u.apk \
  --android-jar "$ANDROID_JAR" --d8-jar "$D8_JAR" \
  --key "$AOSP_PLATFORM_PK8" --cert "$AOSP_PLATFORM_CERT" \
  --output ims-mtk-u-api37-compat.apk
```

The helper builds only the IMS APK compatibility stage. It does not produce a complete r7 ROM, modify a phone, or add the required shared-UID system configuration.

## 5. Enable the built-in IMS settings

In the existing Treble settings app, under **IMS features**:

1. Enable **Force the presence of 4G Calling setting**.
2. Enable **Request IMS network**.

The first setting made VoLTE available to the framework; the second requested an IMS bearer. An IMS APN already existed, so no duplicate was added. Wi-Fi Calling remained disabled by the user setting, and no Wi-Fi Calling test was performed.

After these changes the service remained running, MMTEL registration became `2` (registered), and voice, SMS and UT capabilities became available. This result persisted after a normal reboot and PIN unlock. The empty second slot remained unregistered, as expected.

## Verification boundaries

- LTE HOME registration: verified before and after normal restarts.
- IMS registration and voice/SMS/UT capabilities: verified after restart and unlock.
- Actual outgoing/incoming calls, call audio, emergency calling and SMS delivery: untested.
- Mobile internet: cellular network obtained, but HTTPS/validation failed; not claimed working. The dual-stack APN trial also failed and was reverted. The temporary test restored the original mobile-data setting and was removed.
- 5G attachment, VoNR, Wi-Fi Calling and dual active SIMs: untested.

The [curated result record](../evidence/cellular-validation.json) excludes subscriber identities, phone numbers, operator identifiers, cell locations and raw telephony logs. Raw `dumpsys` output can contain private information; follow [PRIVACY.md](../PRIVACY.md) before sharing diagnostics.
