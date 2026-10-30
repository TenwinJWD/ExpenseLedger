#!/usr/bin/env bash
# Builds the whole release (tests, PyInstaller, MSI files, setup EXE, signing) by running build.ps1.
# Run it from Git Bash on Windows:   ./build.sh --skip-sign        (unsigned test build)
#                                    ./build.sh --thumbprint <sha1> --version 1.1.0   (signed release build)
# Options:
#   --skip-sign              build without signing
#   --thumbprint <sha1>      sign with a certificate in the Windows certificate store
#   --pfx <file> --pfx-password <password>
#                            sign with a .pfx file
#   --azure-dlib <file> --azure-metadata <file>
#                            sign with Azure Trusted Signing
#   --version <x.y.z>        build this version: it is written to app/core/config.py, version_info.txt and
#                            (as a stub entry, if missing) CHANGELOG.md, then used for the installers
#   --setup                  first create .venv and install requirements-dev.txt
#   -h, --help               show this help
set -euo pipefail
cd "$(dirname "$0")"

usage() { sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'; }

args=()
setup=0
signing=0
while [ $# -gt 0 ]; do
    case "$1" in
        --skip-sign)      args+=("-SkipSign"); signing=1 ;;
        --thumbprint)     args+=("-Thumbprint" "$2"); signing=1; shift ;;
        --pfx)            args+=("-PfxPath" "$2"); signing=1; shift ;;
        --pfx-password)   args+=("-PfxPassword" "$2"); shift ;;
        --azure-dlib)     args+=("-AzureDlib" "$2"); signing=1; shift ;;
        --azure-metadata) args+=("-AzureMetadata" "$2"); shift ;;
        --version)        args+=("-Version" "$2"); shift ;;
        --setup)          setup=1 ;;
        -h|--help)        usage; exit 0 ;;
        *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
    esac
    shift
done

if [ "$signing" -eq 0 ]; then
    echo "Choose how to sign: --skip-sign, --thumbprint, --pfx or --azure-dlib. Use --help for details." >&2
    exit 2
fi

if [ "$setup" -eq 1 ] || [ ! -x ".venv/Scripts/python.exe" ]; then
    echo "== Creating .venv and installing build requirements"
    python -m venv .venv
    ./.venv/Scripts/python.exe -m pip install --quiet --upgrade pip
    ./.venv/Scripts/python.exe -m pip install --quiet -r requirements-dev.txt
fi

if ! command -v wix >/dev/null 2>&1 && [ ! -x "$HOME/.dotnet/tools/wix.exe" ]; then
    echo "WiX is not installed. Run: dotnet tool install --global wix" >&2
    exit 1
fi

powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./build.ps1 "${args[@]}"

echo
version=$(sed -n 's/^APP_VERSION = "\(.*\)"/\1/p' app/core/config.py)
echo "Done. The build created installer/output/$version with the installers (build files are in its work folder); a rebuild of the same version replaces that folder:"
ls -1 "installer/output/$version"/ExpenseLedger-Setup-*.exe "installer/output/$version"/*.msi 2>/dev/null || true
