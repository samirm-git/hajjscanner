"""
Audit script: runs the same scrape loop as pipeline.py, but instead of
persisting package data, it checks a set of "suspect" fields for null-ness
across every scraped url, and prints a summary report.

Usage (mirrors pipeline.py's CLI):
    python audit_fields.py hajj
    python audit_fields.py umrah --overridelinkscache
    python audit_fields.py hajj --scrapenewonly

By default it reuses cached urls (useCache=True), same as pipeline.py's
"not args.overridelinkscache" logic, so this doesn't re-scrape provider
homepages unless you pass --overridelinkscache.
"""

import pageScraper
from db import packageUrlQueries
from hajjUmrahEnum import HajjOrUmrahEnum
from utils import getProjectRoot, getSoup
from tqdm import tqdm
import time
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Reuse the existing url-refresh logic from pipeline.py instead of duplicating it
from pipeline import refreshProviderUrls

root = getProjectRoot()
load_dotenv(dotenv_path=root / '.env.')


# ---------------------------------------------------------------------------
# Fields to audit. Add/remove entries here to change what gets checked.
# Each accessor must be defensive: package_core is always present, but
# makkah_hotel / madinah_hotel can be None themselves (not just their
# sub-fields), so a plain attribute chain would raise AttributeError.
# ---------------------------------------------------------------------------
AUDIT_FIELDS = {
    "package_core.departure_city": lambda p: p.package_core.departure_city,
    "makkah_hotel.name": lambda p: p.makkah_hotel.name if p.makkah_hotel is not None else None,
    "madinah_hotel.name": lambda p: p.madinah_hotel.name if p.madinah_hotel is not None else None,
}


def auditFields(hajjOrUmrah: HajjOrUmrahEnum, useCache=True, scrapeNewOnly=False, outputPath=None):
    start = time.time()

    if useCache:
        providerPackageUrls = packageUrlQueries.getAllUrls(hajjOrUmrah.value, scrapeNewOnly)
    else:
        tqdm.write(f"Scrapping {hajjOrUmrah.label} package urls for all providers...")
        providerPackageUrls = refreshProviderUrls(hajjOrUmrah)
        tqdm.write("=================================")

    total_pages = 0
    # non_null[field_label] -> list of (url, value) for every page where the field WAS populated
    non_null = {label: [] for label in AUDIT_FIELDS}
    null_count = {label: 0 for label in AUDIT_FIELDS}

    tqdm.write(f"{sum(len(u) for u in providerPackageUrls.values())} urls")
    tqdm.write(f"Auditing {hajjOrUmrah.label} package info from all urls")

    for companyName, urls in tqdm(providerPackageUrls.items()):
        tqdm.write(f"Now auditing {companyName}...")
        for url in tqdm(urls):
            soup = getSoup(url)
            if soup is None:
                tqdm.write(f"None soup for url: {url}")
                continue
            if pageScraper.isCataloguePage(url, soup, companyName=companyName):
                continue

            packageInfo = pageScraper.scrape(company=companyName, url=url, soup=soup, hajjOrUmrah=hajjOrUmrah)
            if packageInfo is None:
                continue

            total_pages += 1
            for label, accessor in AUDIT_FIELDS.items():
                try:
                    value = accessor(packageInfo)
                except AttributeError:
                    # Defensive fallback in case a schema variant lacks this path entirely
                    value = None

                if value is not None:
                    non_null[label].append((url, value))
                else:
                    null_count[label] += 1

    if outputPath is None:
        outputPath = root / f"field_audit_{hajjOrUmrah.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    writeReport(outputPath, hajjOrUmrah, total_pages, non_null, null_count)
    elapsed = time.time() - start
    tqdm.write(f"time taken: {elapsed}")
    tqdm.write(f"Report written to: {outputPath}")

    return non_null, null_count


def writeReport(outputPath, hajjOrUmrah, total_pages, non_null, null_count):
    lines = []
    lines.append(f"# Field Audit Report — {hajjOrUmrah.label}")
    lines.append("")
    lines.append(f"- Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"- Pages scraped: {total_pages}")
    lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append("| Field | Non-null | Null | % Null |")
    lines.append("|---|---|---|---|")
    for label in AUDIT_FIELDS:
        n_non_null = len(non_null[label])
        n_null = null_count[label]
        pct_null = (n_null / total_pages * 100) if total_pages else 0.0
        lines.append(f"| `{label}` | {n_non_null} | {n_null} | {pct_null:.1f}% |")
    lines.append("")

    for label in AUDIT_FIELDS:
        n_non_null = len(non_null[label])
        lines.append(f"## {label} — non-null instances ({n_non_null})")
        lines.append("")
        if n_non_null:
            lines.append("| Value | URL |")
            lines.append("|---|---|")
            for url, value in non_null[label]:
                # escape pipe characters so they don't break the markdown table
                safeValue = str(value).replace("|", "\\|")
                lines.append(f"| {safeValue} | {url} |")
        else:
            lines.append("_(no non-null instances found)_")
        lines.append("")

    outputPath.parent.mkdir(parents=True, exist_ok=True)
    with open(outputPath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit scraped field completeness (package_core.departure_city, makkah_hotel.name, madinah_hotel.name)")
    parser.add_argument("hajjOrUmrah", choices=['hajj', 'umrah'], help='choose whether to audit hajj or umrah packages')
    parser.add_argument("--overridelinkscache", action='store_true', help="re-scrape provider urls instead of using cached urls")
    parser.add_argument("--scrapenewonly", action="store_true", help="only consider urls not yet marked scraped")
    parser.add_argument("--output", type=str, default=None, help="path to write the .md report to (default: field_audit_<type>_<timestamp>.md in project root)")
    args = parser.parse_args()

    hajjOrUmrah = HajjOrUmrahEnum.HAJJ if args.hajjOrUmrah == 'hajj' else HajjOrUmrahEnum.UMRAH
    outputPath = Path(args.output) if args.output else None

    auditFields(hajjOrUmrah, useCache=not args.overridelinkscache, scrapeNewOnly=args.scrapenewonly, outputPath=outputPath)