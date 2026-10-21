# Security Policy

## Reporting a vulnerability

Please do not open a public issue for security problems.

Report privately using GitHub's "Report a vulnerability" button on the
Security tab of this repository. Include what you found, how to reproduce
it, and the impact you expect.

You can expect an acknowledgement within 7 days. Confirmed issues will be
fixed as quickly as practical and credited in the release notes unless you
prefer to stay anonymous.

## Scope

This plugin includes hooks and scripts that run on the user's machine, so
the following are treated as in scope:

- Hooks or scripts that run unexpected commands or access files outside the project
- Network calls or data exfiltration of any kind
- Anything that could be abused to modify a user's code without their consent

## Supported versions

Only the latest release on `main` receives security fixes.

## Contributions

All changes to this repository go through pull requests that are reviewed by
the maintainer before merging. Pull requests that add or change hooks,
scripts or network behaviour receive extra scrutiny.
