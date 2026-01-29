"""Models for pydantic parsing."""

from pydantic import BaseModel

DateTimeISO8601 = str
from pydantic import BaseModel

from typing import List, Literal, Dict, List, Tuple, Any, Optional, Union


from datetime import datetime


class Coords(BaseModel):
    """Coordinates and bounds."""

    lat: float
    lon: float
    bounds: Dict[str, float]



class UserModel(BaseModel):
    verified: Optional[bool] = None
    cars: Optional[List[str]] = []
    mustSendMailOnEachTransaction: Optional[bool] = None
    proAccountActivated: Optional[bool] = None
    subscribedToOnboardingCampaign: Optional[bool] = None
    _id: Optional[str] = None
    time: Optional[datetime] = None
    lastSeen: Optional[datetime] = None
    confidence: Optional[int] = None
    lang: Optional[str] = None
    __v: Optional[int] = None

class RemoteConfigsLastUpdateModel(BaseModel):
    messages: str

class SeetyUser(BaseModel):
    user: Optional[UserModel] = {}
    lastMapUpdate: Optional[datetime] = None
    remoteConfigsLastUpdate: Optional[RemoteConfigsLastUpdateModel] = {}
    access_token: Optional[str] = None
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    status: Optional[str] = None


class Rules(BaseModel):
    days: Optional[List[int]] = []
    prices: Optional[Dict[str, float]] = {}
    hours: Optional[List[str]] = []
    type: Optional[str] = None
    paymentPartner: Optional[str] = None
    advantageInApp: Optional[bool] = False
    displayNotPayable: Optional[bool] = False
    overrides: Optional[Dict[str, Any]] = {}
    forceDisplayPriceTables: Optional[bool] = False


class Properties(BaseModel):
    type: str
    color: str
    dotted: bool
    closest: Tuple[float, float]
    closestDist: float
    maxDistToPay: float
    city: str


class SeetyStreetRules(BaseModel):
    rules: Optional[Rules] = {}
    risk: Optional[int] = None
    overrides: Optional[Dict[str, Any]] = {}
    properties: Optional[Properties] = {}
    twoSided: Optional[bool] = False
    status: Optional[str] = None


class Location(BaseModel):
    lat: float
    lng: float


class Geometry(BaseModel):
    location: Location


class SeetyLocationGeocodeResult(BaseModel):
    formatted_address: str
    countryCode: str
    geometry: Geometry
    types: List[str]


class SeetyLocationResponse(BaseModel):
    status: Literal["OK"]
    results: List[SeetyLocationGeocodeResult]


# -------------------------
# Zone Table Row
# -------------------------
class ZoneTable(BaseModel):
    rows: Dict[str, List[Union[float, str]]]  # e.g., {"09:00,19:00": [0.1, 0.2, "D"]}
    cols: List[str]
    days: List[int]
    accessHours: Dict[str, Union[str, List[str]]] = {}
    entryHours: Optional[Union[str, List[str]]] = None


# -------------------------
# Color Info
# -------------------------
class ZoneColor(BaseModel):
    color: str
    dotted: bool


# -------------------------
# Special Permits
# -------------------------
class SpecialPermits(BaseModel):
    residents: Optional[List[str]] = []
    disabled: Optional[List[str]] = []


# -------------------------
# Summary Info
# -------------------------
class ZoneSummary(BaseModel):
    days: Optional[List[int]] = []
    prices: Optional[Dict[str, float]] = {}
    hours: Optional[List[str]] = None
    type: Optional[str] = None
    paymentPartner: Optional[str] = None
    advantageInApp: Optional[bool] = False
    displayNotPayable: Optional[bool] = False
    overrides: Optional[Dict[str, str]] = {}
    forceDisplayPriceTables: Optional[bool] = False


# -------------------------
# Zone Definition
# -------------------------
class Zone(BaseModel):
    weight: Optional[float] = None
    summary: Optional[ZoneSummary] = {}
    remarks: Optional[List[str]] = []
    specialPermits: Optional[SpecialPermits] = {}
    maxStay: Optional[Union[str, int]] = None
    color: Optional[ZoneColor] = {}
    name: Optional[str] = None
    table: Optional[List[ZoneTable]] = []
    parkingPaymentProviders: Optional[List[str]] = []
    displayNotPayable: Optional[bool] = False

# -------------------------
# Description for Provider
# -------------------------
class ProviderDescription(BaseModel):
    fr: Optional[str] = "" 
    en: Optional[str] = ""
    nl: Optional[str] = ""




class SessionFee(BaseModel):
    comment: Optional[ProviderDescription] = {} 
    fixed: Optional[float] = None
    percentage: Optional[float] = None
    
# -------------------------
# Fees for Providers
# -------------------------
class Fees(BaseModel):
    registration: Optional[Dict[str, float]] = {}
    session: Optional[SessionFee] = {}
    sessionSubscription: Optional[SessionFee] = {}
    notifSms: Optional[SessionFee] = {}
    notifApp: Optional[SessionFee] = {}




# -------------------------
# Subscription Info
# -------------------------
class Subscription(BaseModel):
    period: Optional[int] = None
    price: Optional[float] = None
    _id: Optional[str] = None


# -------------------------
# Provider Definition
# -------------------------
class Provider(BaseModel):
    descriptionApp: Optional[ProviderDescription] = {}
    descriptionSMS: Optional[ProviderDescription] = {}
    fees: Optional[Fees] = {}
    advantageApp: Optional[Dict[str, List[str]]] = {}
    disadvantageApp: Optional[Dict[str, List[str]]] = {}
    advantageSms: Optional[Dict[str, List[str]]] = {}
    disadvantageSms: Optional[Dict[str, List[str]]] = {}
    _id: Optional[str] = None
    name: str
    intName: Optional[str] = None
    rating: Optional[float] = None
    logo: Optional[str] = None
    subscriptions: Optional[List[Subscription]] = []
    url: Optional[str] = None
    transactionPrice: Optional[str] = None
    notificationPrice: Optional[str] = None
    registrationFees: Optional[str] = None
    subscriptionPrice: Optional[str] = None
    subscriptionType: Optional[str] = None


# -------------------------
# City Info
# -------------------------
class CityInfo(BaseModel):
    fr: Optional[str] = ""
    en: Optional[str] = ""
    nl: Optional[str] = ""


# -------------------------
# Full Response Model
# -------------------------
class SeetyStreetComplete(BaseModel):
    rules: Optional[Dict[str, Zone]] = {}
    table: Optional[List[ZoneTable]] = []
    maxStay: Optional[Union[str, int]] = None
    remarks: Optional[List[str]] = []
    specialPermits: Optional[SpecialPermits] = {}
    providers: Optional[List[Provider]] = []
    city: Optional[CityInfo] = {}
    cityName: Optional[str] = None
    status: Optional[str] = None

class CityParkingModel(BaseModel):
    user: Optional[SeetyUser] = {}
    location: Optional[SeetyLocationResponse] = {}
    rules: Optional[SeetyStreetRules] = {}
    streetComplete: Optional[SeetyStreetComplete] = {}
    origin: Optional[str] = None
    origin_coordinates: Optional[Coords] = {}
    extra_data: Optional[Dict[str, Any]] = {}