# Shared host search and ownership files

Minimal host portal for CareerPick and SupportPick, authorized in the integrated search and AdSense task on 2026-11-04. The two project repositories and their deployment workflows remain independent.

Only the allowlisted 8 public files are deployed. Ownership metadata and ads.txt identify the existing publisher account; there are no advertisement, tracking or form scripts. Real Google/Naver processing and AdSense review remain external outcomes.

Build: `python tools/build.py`. The root sitemap index references each project's dynamically maintained sitemap without copying its contents or inventing lastmod dates. No private credentials or user records belong in this repository.

Rollback by reverting the relevant commit and redeploying; never reset project repositories or browser storage.
