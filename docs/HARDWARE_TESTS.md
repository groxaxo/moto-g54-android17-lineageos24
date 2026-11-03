# Hardware checks on r6

The broad matrix was collected on r6; cellular was retested on r7. These bounded tests ran on the same XT2343-2 / `cancunf` with Android 17 / API 37 on 2026-11-02–03 UTC. A temporary on-device app exercised actual APIs and data paths. The [curated machine-readable results](../evidence/hardware-validation.json) contain no credentials, device addresses, nearby names, location coordinates, pictures, or recordings.

**A pass applies to the operation in the table. It does not certify every mode of that feature. A later r7 follow-up verified LTE and IMS registration after restart; real calls/SMS and mobile internet are not established. Several checks require physical input or accessories.**

| Feature | Actual test and result | Remaining boundary |
| --- | --- | --- |
| Bluetooth classic | Discovery started and found 7 devices | Pairing/profile connections untested |
| Bluetooth LE | Scan received 23 advertisers with no scan error; advertising start callback succeeded | Peer reception, GATT transfer and headset audio untested |
| Wi-Fi | Validated network and HTTPS 204; off/on cycle reconnected and revalidated | All bands, roaming and sustained throughput untested |
| Hotspot | Local-only hotspot started; reservation closed; Wi-Fi remained validated | Client association and internet tethering untested |
| Rear/front cameras | Both exposed cameras streamed distinct frames and produced valid 640×480 JPEGs | Full resolution, auxiliary lenses, zoom, stabilization and image quality untested |
| Camera video/audio | A private ~3.1-second 640×480 recording contained H.264 video and AAC audio; file deleted locally | Long recordings, sync/quality and other modes untested |
| H.264 decoder | MTK hardware decoder produced and rendered 24 synthetic test frames | Other codecs, resolutions and rates untested |
| H.264 encoder | MTK hardware encoder produced 8 packets at 640×480 and reached EOS | Other formats and rates untested |
| Microphone | Captured 16,000 non-silent PCM samples | Speech quality, every microphone path and wired/BT microphones untested |
| Speaker path | Wrote 16,000 samples; playback clock advanced; route was built-in speaker | Physical audibility/quality and earpiece need owner confirmation |
| Graphics | PowerVR EGL/GLES context rendered RGB colors with correct pixel readback and no GL error | Physical panel, refresh modes and gaming stability untested |
| Internal storage | 4 MiB write, fsync and SHA256 readback passed | Sustained/endurance tests untested |
| Removable SD card | 1 MiB write, fsync and SHA256 readback passed in the tester's own directory | Other card/filesystem combinations untested |
| Android Keystore | AES-GCM encryption/decryption passed with TEE security level; temporary key deleted | Attestation and all algorithms untested |
| Motion sensors | Accelerometer, gyro, magnetometer and rotation-vector events arrived with variation | Calibration and real-world accuracy untested |
| Light/proximity | Events arrived | Deliberate cover/uncover response unconfirmed |
| Step counter | Present and listener accepted | No walking/counting result in the short static test |
| Pressure sensor | Not exposed | No hardware-absence or ROM-defect conclusion |
| GPS | Callback registered and reported one satellite; no fix within 45 seconds | A clearer-sky fix/navigation test is needed |
| NFC | Enabled adapter and reader-mode test; no tag detected | A tag must be presented; payments untested |
| Fingerprint | Feature declared; authentication returned `BIOMETRIC_ERROR_NONE_ENROLLED` | Owner enrollment and real authentication untested |
| Touch/UI input | Injected gesture delivered 80 events across 12 grid cells | This is not a physical digitizer or multitouch test |
| Vibration/torch | Vibration request accepted; torch-on callback confirmed | Physical feedback/brightness not confirmed by the owner |
| USB/charging | USB ADB control and APK transfers used; battery reported plugged/full | MTP, OTG, charge rate and endurance untested |
| Cellular, r7 follow-up | LTE HOME registration and IMS voice/SMS/UT capabilities verified after restart and PIN unlock | Actual calls/SMS untested; cellular-only HTTPS failed; see [CELLULAR.md](CELLULAR.md) |
| Widevine | Framework reported L1 capability | No protected streaming, provisioning or certification test |

The first encoder probe requested 160×120. The encoder advertised a minimum height of 160, so that configuration was invalid. A follow-up used its advertised color formats and supported 640×480 size and passed. The initial test error should not be reported as a broken encoder.

Camera2/ImageReader checked preview frames and JPEG decoding; MediaRecorder checked a real camera/audio container; MediaCodec checked synthetic H.264 decoding/encoding. AudioRecord and AudioTrack checked I/O, sensor listeners checked delivered events, and private-file SHA256 round trips checked storage. No personal files were accessed by the storage tests.

The temporary APK and its permissions/data were removed afterward. Test media and the temporary keystore key were deleted, original Bluetooth/Wi-Fi/location/NFC settings were preserved, and the temporary display power setting was restored. Android 17 remained booted with Enforcing SELinux and no unexpected restart during the run.

To extend this result, report specific physical/accessory tests rather than “everything works”: a chosen headset's pairing and A2DP/HFP audio, NFC tag reading, owner fingerprint enrollment/unlock, outdoor GNSS fix, physical touch/button coverage, and subjective speaker/vibration/flashlight output. Follow [PRIVACY.md](../PRIVACY.md) before posting diagnostics. No calls, SMS, payment transactions or paid media playback were performed in this run.
