from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import pickle
from utils import createSoup 
from HajjUmrahEnum import HajjOrUmrahEnum
from pageScraper.schema.fields import BaseField
from pageScraper.scrapePage import scrapePage


DATA_ROOT = Path(__file__).parent/ "data" 

def discover_cases(package_type: HajjOrUmrahEnum) -> list[Path]:
    pattern = f"*/{package_type.value}/expected.json"

    expected_files = DATA_ROOT.glob(pattern)

    case_directories = []

    for expected_file in expected_files:
        case_directory = expected_file.parent
        case_directories.append(case_directory)

    case_directories.sort()

    return case_directories

def case_id(case_directory: Path) -> str:
    """
    Produce readable pytest IDs such as:

        company-a-hajj-standard-package
    """
    relative_path = case_directory.relative_to(DATA_ROOT)
    return "-".join(relative_path.parts)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonicalise_result(result: dict[str, Any]) -> dict[str, Any]:
    # Also converts StrEnum dictionary keys into ordinary JSON strings,
    # making pytest's diff easier to read.
    normalised = json.loads(json.dumps(result))

    for hotel_key in ("makkah_hotel", "madinah_hotel"):
        hotel = normalised.get(hotel_key)

        if hotel is not None and "images" in hotel and hotel["images"] is not None:
            # Sorting retains duplicate counts, unlike converting to a set.
            hotel["images"] = sorted(hotel["images"])

    return normalised


def assert_golden_case(
    case_directory: Path,
    package_type: HajjOrUmrahEnum,
) -> None:
    # soup_pkl_path = case_directory / "soup.pkl"
    page_html_path = case_directory / "page.html"
    expected_path = case_directory / "expected.json"

    # assert soup_pkl_path.exists(), f"Missing Soup pkl fixture: {soup_pkl_path}"
    assert page_html_path.exists(), f"Missing page html fixture: {page_html_path}"
    assert expected_path.exists(), f"Missing expected fixture: {expected_path}"

    expected = load_json(expected_path)

    assert BaseField.COMPANY in expected, (
        f"{expected_path} must contain "
        f"{BaseField.COMPANY.value!r}"
    )
    assert BaseField.URL in expected, (
        f"{expected_path} must contain "
        f"{BaseField.URL.value!r}"
    )

    # with open(soup_pkl_path, "rb") as f:
    #     soup = pickle.load(f)

    with open(page_html_path, "r", encoding='utf-8', newline="") as f:
        soup = createSoup(f)

    actual = scrapePage(
        company=expected[BaseField.COMPANY],
        url=expected[BaseField.URL],
        soup=soup,
        hajjOrUmrah=package_type,
    )

    assert actual is not None, (
        f"scrapePage returned None for {case_directory}. "
        "The scraped data probably failed schema validation."
    )

    assert canonicalise_result(actual) == canonicalise_result(expected)


HAJJ_CASES = discover_cases(HajjOrUmrahEnum.HAJJ)
UMRAH_CASES = discover_cases(HajjOrUmrahEnum.UMRAH)

HAJJ_XFAIL_CASE_IDS = {
    "alkhairtravel-hajj",
    "cheaphajjandumrah-hajj",
    "haramainhajjtours-hajj",
    "islamictravel-hajj",
    "makkahtour-hajj",
    "umrah-alamanah-hajj",
}

UMRAH_XFAIL_CASE_IDS = {
    "alamanahtravel-umrah", #MULTIPLE HOTELS MENTIONED. SCRAPPING ANY IS FINE
    "alharamtravel-umrah", #CATALOGUE PAGE
    "duatravels-umrah", #BAD MAKKAH / MADINAH SECTION PARTITIONING
    "makkahtour-umrah", #SIMILAR TO ^ BUT ALSO NOT FILTERING OUT CUSTOMER REVIEWS IN getSoup 
    "hajjandumrahexperts-umrah",
}

HAJJ_CASE_PARAMS = [
    pytest.param(case, marks=pytest.mark.xfail(reason="known scraping bug, not yet fixed"))
    if case_id(case) in HAJJ_XFAIL_CASE_IDS
    else case
    for case in HAJJ_CASES
]

UMRAH_CASE_PARAMS = [
    pytest.param(case, marks=pytest.mark.xfail(reason="known scraping bug, not yet fixed"))
    if case_id(case) in UMRAH_XFAIL_CASE_IDS
    else case
    for case in UMRAH_CASES
]


@pytest.mark.parametrize(
    "case_directory",
    HAJJ_CASE_PARAMS,
    ids=case_id,
)
def test_hajj_saved_page_matches_expected_output(case_directory: Path) -> None:
    assert_golden_case(
        case_directory,
        HajjOrUmrahEnum.HAJJ,
    )


@pytest.mark.parametrize(
    "case_directory",
    UMRAH_CASE_PARAMS,
    ids=case_id,
)
def test_umrah_saved_page_matches_expected_output(case_directory: Path,) -> None:
    assert_golden_case(
        case_directory,
        HajjOrUmrahEnum.UMRAH,
    )
