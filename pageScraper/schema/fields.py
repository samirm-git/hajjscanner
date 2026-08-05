from enum import StrEnum

class BaseField(StrEnum):
    """Fields shared by both Hajj and Umrah scrapers."""
    COMPANY = "company"
    URL = "url"
    PPP = "ppp"
    YEAR = "year"
    TOTAL_DAYS = "total_days"
    TIER = "tier"
    STARS = "stars"
    DEPARTURE_CITY = "departure_city"
    IS_VISA_INCLUDED = "is_visa_included"
    MAKKAH_HOTEL = 'makkah_hotel'
    MADINAH_HOTEL = 'madinah_hotel'

class HajjField(StrEnum):
    """Fields only in the Hajj schema."""
    IS_SHIFTING = "is_shifting"

class UmrahField(StrEnum):
    """Fields only in the Umrah schema."""
    SEASON = "season"
    MONTH = "month"
    ISLAMIC_MONTH = "islamic_month"
    IS_ZIYARAT_INCLUDED = "is_ziyarat_included"

class HotelField(StrEnum):
    """Fields in the hotel.json schema (used for both makkahHotel and madinahHotel)."""
    NAME = "name"
    TOTAL_DAYS = "total_days"
    IMAGES = "images"
    STARS = "stars"
    HAS_WIFI = "has_wifi"
    HAS_AC = "has_ac"
    OTHER_AMENITIES = "other_amenities"
    DISTANCE_TO_HARAM = "distance_to_haram"
    WALK_TO_HARAM = "walk_to_haram"
    NUMBER_OF_BEDS = "number_of_beds"