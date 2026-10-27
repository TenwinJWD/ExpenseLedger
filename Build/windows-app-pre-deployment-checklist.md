# Windows App Pre-Deployment Checklist

Complete every item below before releasing your Windows application.

**App name:** ____________________  **Version:** ____________  **Date:** ____________  **Reviewer:** ____________

---

## 1. Packaging
- [ ] Choose a format: MSIX, MSI, EXE installer, or portable zip
- [ ] Installer supports clean install, upgrade, repair and uninstall
- [ ] Silent install switch works (e.g. `/quiet`) if targeting enterprise

## 2. Code Signing
- [ ] Obtain a certificate (EV, OV, or Azure Trusted Signing)
- [ ] Sign the installer
- [ ] Sign all exes and DLLs inside it
- [ ] Add a timestamp to signatures
- [ ] Confirm no SmartScreen warning on a fresh machine

## 3. Dependencies and Compatibility
- [ ] Decide .NET approach: framework-dependent or self-contained
- [ ] Bundle or check for the VC++ Redistributable
- [ ] Bundle or check for WebView2 (if used)
- [ ] Confirm supported Windows versions (10 / 11)
- [ ] Confirm architecture builds: x64, x86, ARM64

## 4. Install Location and Permissions
- [ ] Choose per-machine (`Program Files`) or per-user (`%LocalAppData%`) install
- [ ] User data and settings go in `%AppData%` / `%LocalAppData%`, not the install folder
- [ ] Manifest requests the minimum privileges (`asInvoker` unless admin is required)
- [ ] App runs correctly as a standard user

## 5. Updates
- [ ] Update mechanism chosen (MSIX, Squirrel, ClickOnce, or custom)
- [ ] Version numbers consistent across assemblies and installer
- [ ] Upgrades preserve user data
- [ ] Rollback path tested

## 6. Security and Antivirus
- [ ] Scanned with Windows Defender
- [ ] No packers or obfuscators that trigger false positives
- [ ] False positives submitted to Microsoft, if any
- [ ] No hard-coded secrets
- [ ] Dependencies checked for known vulnerabilities

## 7. Testing
- [ ] Tested on a clean VM (Windows Sandbox / Hyper-V) with no dev tools
- [ ] Install, upgrade, repair and uninstall tested
- [ ] Uninstall leaves no leftovers
- [ ] Tested on high-DPI and multi-monitor setups
- [ ] Tested with non-English locale and paths containing spaces or Unicode

## 8. Distribution
- [ ] Distribution channel chosen: Microsoft Store, winget, website/CDN, or internal portal
- [ ] Download hosted over HTTPS
- [ ] Checksums published
- [ ] Enterprise compatibility verified (GPO / Intune / SCCM), if relevant

## 9. Operations
- [ ] Logging to a user-accessible file
- [ ] Crash reporting set up
- [ ] Telemetry has a privacy policy and user consent (GDPR etc.)
- [ ] EULA / licensing in place

## 10. Rollout
- [ ] Staged rollout planned: internal, then beta, then everyone
- [ ] Way to pull or revert a bad release
- [ ] Support channel ready

---

## Final Pre-Release Gate
- [ ] Binaries signed
- [ ] Clean-VM install passed
- [ ] Upgrade and uninstall passed
- [ ] Standard-user run passed
- [ ] AV scan clean
- [ ] Update mechanism verified
- [ ] Logging and crash reporting working

**Approved for release:** [ ] Yes  [ ] No  **Signature:** ____________________
