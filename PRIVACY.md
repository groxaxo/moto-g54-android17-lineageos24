# Privacy of this publication

The public repository is assembled from an explicit allowlist. It contains newly written documentation, small configuration patches, a generic host-only tool, public upstream hashes, and a curated result summary.

It excludes credentials and PIN values; account/session tokens; SSH/ADB keys; handset serials, IMEI/IMSI and phone numbers; Wi-Fi names, addresses and private network details; owner-specific app identifiers; local hostnames and home paths; raw transcripts, logs and screenshots; boot/vbmeta dumps, vendor binaries, userdata and recovery backups.

No private signing material is included. References to AOSP development signing identify a publicly distributed upstream test key, not a private owner credential. SHA256 hashes of the public base and clean system candidate are integrity references. Native trustlet filenames and hardware SKU/codename are software/model identifiers rather than unique handset identities.

Before submitting an issue, describe the symptom and exact hardware/build combination first. Do not attach a whole `getprop`, `logcat`, `bugreport`, partition dump or screenshot collection. Extract only the relevant event, inspect it locally, and remove credentials, tokens, keys, identifiers, network details and unrelated personal information. A secret scanner cannot recognize every device-specific value.

Never publish a screen-lock credential, SIM PIN, recovery code, authentication token or key blob to reproduce an authentication problem. A statement that PIN enrollment or post-reboot unlock failed is sufficient to begin a report. Firmware or ROM images also need a separate content and licensing review; keeping userdata out of an archive alone does not establish that it is safe to upload.
