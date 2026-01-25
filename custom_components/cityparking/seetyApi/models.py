"""Models for pydantic parsing."""

from pydantic import BaseModel, Field, ConfigDict

DateTimeISO8601 = str
from typing import List
from pydantic import BaseModel

from typing import Dict, List, Tuple, Any, Optional, Union


from datetime import datetime

class UserModel(BaseModel):
    verified: bool
    cars: List[str]
    mustSendMailOnEachTransaction: bool
    proAccountActivated: bool
    subscribedToOnboardingCampaign: bool
    _id: str
    time: datetime
    lastSeen: datetime
    confidence: int
    lang: str
    __v: int

class RemoteConfigsLastUpdateModel(BaseModel):
    messages: str

class SeetyUser(BaseModel):
    user: UserModel
    lastMapUpdate: datetime
    remoteConfigsLastUpdate: RemoteConfigsLastUpdateModel
    access_token: str
    expires_in: int
    refresh_token: str
    status: str


class Rules(BaseModel):
    days: List[int]
    prices: Dict[str, float]
    hours: List[str]
    type: str
    paymentPartner: Optional[str] = None
    advantageInApp: bool
    displayNotPayable: bool
    overrides: Dict[str, Any]
    forceDisplayPriceTables: bool


class Properties(BaseModel):
    type: str
    color: str
    dotted: bool
    closest: Tuple[float, float]
    closestDist: float
    maxDistToPay: float
    city: str


class SeetyStreetRules(BaseModel):
    rules: Rules
    risk: Optional[int] = None
    overrides: Dict[str, Any]
    properties: Properties
    twoSided: bool
    status: str


class Location(BaseModel):
    lat: float
    lng: float


class Geometry(BaseModel):
    location: Location


class SeetyLocation(BaseModel):
    formatted_address: str
    countryCode: str
    geometry: Geometry
    types: List[str]





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
    residents: List[str] = []
    disabled: List[str] = []


# -------------------------
# Summary Info
# -------------------------
class ZoneSummary(BaseModel):
    days: List[int]
    prices: Dict[str, float] = {}
    hours: Optional[List[str]] = None
    type: str
    paymentPartner: Optional[str] = None
    advantageInApp: Optional[bool] = False
    displayNotPayable: Optional[bool] = False
    overrides: Optional[Dict[str, str]] = {}
    forceDisplayPriceTables: Optional[bool] = False


# -------------------------
# Zone Definition
# -------------------------
class Zone(BaseModel):
    weight: float
    summary: ZoneSummary
    remarks: List[str] = []
    specialPermits: SpecialPermits = SpecialPermits()
    maxStay: Union[str, int] = 0
    color: ZoneColor
    name: str
    table: List[ZoneTable] = []
    parkingPaymentProviders: List[str] = []
    displayNotPayable: Optional[bool] = False


# -------------------------
# Fees for Providers
# -------------------------
class Fees(BaseModel):
    registration: Dict[str, float] = {}
    session: Dict[str, float] = {}
    notifApp: Dict[str, float] = {}


# -------------------------
# Description for Provider
# -------------------------
class ProviderDescription(BaseModel):
    fr: Optional[str] = ""
    en: Optional[str] = ""
    nl: Optional[str] = ""


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
    descriptionApp: Optional[ProviderDescription] = None
    descriptionSMS: Optional[ProviderDescription] = None
    fees: Optional[Fees] = None
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
    rules: Dict[str, Zone]
    table: Optional[List[ZoneTable]] = []
    maxStay: Union[str, int] = 0
    remarks: Optional[List[str]] = []
    specialPermits: Optional[SpecialPermits] = SpecialPermits()
    providers: Optional[List[Provider]] = []
    city: CityInfo
    cityName: str
    status: str

class CityParkingModel(BaseModel):
    user: Optional[SeetyUser] = None
    rules: Optional[SeetyStreetRules] = None
    streetComplete: Optional[SeetyStreetComplete] = None