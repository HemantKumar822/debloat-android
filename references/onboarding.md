# Friendly onboarding and connection troubleshooting

## Suggested conversation flow

Agent: "We'll check what's installed and make you a clear Markdown report. This is read-only; it won't remove or disable anything. Is this a phone you own or are authorized to inspect, and are you happy for the tool to read installed app names?"

Once authorized:

1. Install Google's official [Platform Tools](https://developer.android.com/tools/releases/platform-tools). Confirm `adb` is on PATH.
2. On phone: Settings → About phone → Build number; tap seven times. The route varies by device maker.
3. Open Developer options and enable USB debugging.
4. Connect using a data-capable USB cable, unlock phone, check USB connection/authorization prompt, approve only a trusted computer.
5. Run `python scripts/android_care.py doctor`; it explains whether ready, unauthorized, offline, or no device, without reading installed apps. Use `devices` when identifiers are needed to select a phone.
6. After inventory consent, run `python scripts/android_care.py audit --consent`. Explain what the output means, link or locate the Markdown report. For several phones, add `--serial ID` to both commands.
7. Turn off USB debugging or revoke trusted debugging computers when finished.

## Recovery of connection states

- **No phone**: use another USB data cable or port; check drivers on Windows; select appropriate USB mode if necessary.
- **Unauthorized**: unlock phone, watch for "Allow USB debugging"; approve only if this is a trusted host.
- **Offline**: disconnect/reconnect, unlock, recheck ADB connection.
- **Multiple devices**: tool requires explicit `--serial`; never silently choose one.
- **ADB unavailable**: install official Platform Tools; don't download random driver or ADB bundles from unknown sites.

## Important privacy detail

The local scripts perform no network access. The Markdown report contains a local list of installed app package IDs and device properties. This information may reveal private interests. Agents using cloud models may transmit observations to their provider as part of their normal operation. Ask permission before adding detailed package lists to a cloud agent context, uploading logs, attaching reports, or using public online lookups. Reports are not anonymized simply because they omit the serial number.

