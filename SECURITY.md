# Security policy

## Safe downloads

Download ExamReadyTimer only from the official repository's [GitHub Releases](https://github.com/yashinirwan2014/ExamReadyTimer/releases) page. Release ZIP files are accompanied by `SHA256SUMS.txt`. Verify the hash for the archive you downloaded before extracting it.

A SHA-256 match confirms that the archive is identical to the file published with that checksum. It does not establish that the application is harmless, malware-free, digitally signed, or approved by Microsoft.

## Windows warnings and false positives

The Windows executable is currently unsigned with a trusted code-signing certificate. Browser download warnings or Microsoft Defender SmartScreen reputation warnings may therefore occur. Do not disable antivirus protection to run the application, and do not bypass a warning if you are unsure about the file's origin.

If Microsoft Defender detects the official release and you believe it is a false positive, submit the file to [Microsoft Security Intelligence](https://www.microsoft.com/en-us/wdsi/filesubmission) for review. Include the exact release URL and the detection name. Do not submit private study data.

## Reporting a project security issue

For a suspected vulnerability in the application, open a GitHub issue in the official repository with a clear description and steps to reproduce. Do not include passwords, private data, or personal study records.

## Platform signing status

- Windows: no trusted publisher code-signing certificate is currently used.
- macOS: the community build is ad-hoc signed for bundle integrity only; it is not Developer ID signed or Apple-notarized.
- Linux: distributed as a ZIP archive; package trust is not implied by the checksum.

The project does not claim Microsoft certification, Apple approval, or a malware-free guarantee.
