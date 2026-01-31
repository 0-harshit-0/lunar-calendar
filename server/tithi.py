from enum import Enum
from dataclasses import dataclass
from typing import List, Optional


class FastingType(Enum):
    TITHI_BASED = "Tithi-based (Moon–Sun)"
    SOLAR_BASED = "Solar (Sun longitude)"
    MIXED_TIME_RULE = "Tithi with time rule"


class Ayana(Enum):
    UTTARAYANA = "Uttarayana"
    DAKSHINAYANA = "Dakshinayana"
    

class Rashi(Enum):
    MESHA = "Mesha"
    VRISHABHA = "Vrishabha"
    MITHUNA = "Mithuna"
    KARKA = "Karka"
    SIMHA = "Simha"
    KANYA = "Kanya"
    TULA = "Tula"
    VRISHCHIKA = "Vrishchika"
    DHANU = "Dhanu"
    MAKARA = "Makara"
    KUMBHA = "Kumbha"
    MEENA = "Meena"


class Masa(Enum):
    CHAITRA = "Chaitra"
    VAISHAKHA = "Vaishakha"
    JYAISHTHA = "Jyaishtha"
    ASHADHA = "Ashadha"
    SHRAVANA = "Shravana"
    BHADRAPADA = "Bhadrapada"
    ASHVINA = "Ashvina"
    KARTIKA = "Kartika"
    MARGASHIRSHA = "Margashirsha"
    PAUSHA = "Pausha"
    MAGHA = "Magha"
    PHALGUNA = "Phalguna"


class Paksha(Enum):
    SHUKLA = "Shukla Paksha"
    KRISHNA = "Krishna Paksha"


class TithiName(Enum):
    PRATIPADA = "Pratipada"
    DWITIYA = "Dwitiya"
    TRITIYA = "Tritiya"
    CHATURTHI = "Chaturthi"
    PANCHAMI = "Panchami"
    SHASHTHI = "Shashthi"
    SAPTAMI = "Saptami"
    ASHTAMI = "Ashtami"
    NAVAMI = "Navami"
    DASHAMI = "Dashami"
    EKADASHI = "Ekadashi"
    DWADASHI = "Dwadashi"
    TRAYODASHI = "Trayodashi"
    CHATURDASHI = "Chaturdashi"
    PURNIMA = "Purnima"
    AMAVASYA = "Amavasya"


class Ritu(Enum):
    VASANTA = "Vasanta"
    GRISHMA = "Grishma"
    VARSHA = "Varsha"
    SHARAD = "Sharad"
    HEMANTA = "Hemanta"
    SHISHIRA = "Shishira"
    

@dataclass(frozen=True)
class Tithi:
    paksha: Paksha
    index: int
    name: TithiName

@dataclass(frozen=True)
class FastingDay:
    name: str
    fasting_type: FastingType
    tithi_name: Optional[TithiName] = None
    paksha: Optional[Paksha] = None
    masa: Optional[Masa] = None
    description: str = ""


TITHIs: List[Tithi] = [
    *[
        Tithi(Paksha.SHUKLA, i + 1, name)
        for i, name in enumerate([
            TithiName.PRATIPADA,
            TithiName.DWITIYA,
            TithiName.TRITIYA,
            TithiName.CHATURTHI,
            TithiName.PANCHAMI,
            TithiName.SHASHTHI,
            TithiName.SAPTAMI,
            TithiName.ASHTAMI,
            TithiName.NAVAMI,
            TithiName.DASHAMI,
            TithiName.EKADASHI,
            TithiName.DWADASHI,
            TithiName.TRAYODASHI,
            TithiName.CHATURDASHI,
            TithiName.PURNIMA,
        ])
    ],
    *[
        Tithi(Paksha.KRISHNA, i + 1, name)
        for i, name in enumerate([
            TithiName.PRATIPADA,
            TithiName.DWITIYA,
            TithiName.TRITIYA,
            TithiName.CHATURTHI,
            TithiName.PANCHAMI,
            TithiName.SHASHTHI,
            TithiName.SAPTAMI,
            TithiName.ASHTAMI,
            TithiName.NAVAMI,
            TithiName.DASHAMI,
            TithiName.EKADASHI,
            TithiName.DWADASHI,
            TithiName.TRAYODASHI,
            TithiName.CHATURDASHI,
            TithiName.AMAVASYA,
        ])
    ],
]
MASAs: list[Masa] = [
    Masa.CHAITRA,
    Masa.VAISHAKHA,
    Masa.JYAISHTHA,
    Masa.ASHADHA,
    Masa.SHRAVANA,
    Masa.BHADRAPADA,
    Masa.ASHVINA,
    Masa.KARTIKA,
    Masa.MARGASHIRSHA,
    Masa.PAUSHA,
    Masa.MAGHA,
    Masa.PHALGUNA,
]
RASHIs: list[Rashi] = [
    Rashi.MESHA,
    Rashi.VRISHABHA,
    Rashi.MITHUNA,
    Rashi.KARKA,
    Rashi.SIMHA,
    Rashi.KANYA,
    Rashi.TULA,
    Rashi.VRISHCHIKA,
    Rashi.DHANU,
    Rashi.MAKARA,
    Rashi.KUMBHA,
    Rashi.MEENA,
]
FASTING_DAYS: List[FastingDay] = [
    # --- Ekadashi ---
    FastingDay(
        name="Ekadashi",
        fasting_type=FastingType.MIXED_TIME_RULE,
        tithi_name=TithiName.EKADASHI,
        description="Observed on the 11th lunar tithi when it prevails at local sunrise."
    ),

    # --- Pradosha ---
    FastingDay(
        name="Pradosha",
        fasting_type=FastingType.MIXED_TIME_RULE,
        tithi_name=TithiName.TRAYODASHI,
        description="Observed on the 13th tithi during the evening twilight period."
    ),

    # --- Maha Shivaratri ---
    FastingDay(
        name="Maha Shivaratri",
        fasting_type=FastingType.MIXED_TIME_RULE,
        tithi_name=TithiName.CHATURDASHI,
        paksha=Paksha.KRISHNA,
        masa=Masa.MAGHA,
        description="Krishna Paksha Chaturdashi of Magha, observed mainly during night."
    ),

    # --- Amavasya ---
    FastingDay(
        name="Amavasya",
        fasting_type=FastingType.TITHI_BASED,
        tithi_name=TithiName.AMAVASYA,
        description="Observed on the new moon when Moon–Sun longitude difference reaches 360°."
    ),

    # --- Purnima ---
    FastingDay(
        name="Purnima",
        fasting_type=FastingType.TITHI_BASED,
        tithi_name=TithiName.PURNIMA,
        description="Observed on the full moon when Moon–Sun longitude difference reaches 180°."
    ),

    # --- Sankashti Chaturthi ---
    FastingDay(
        name="Sankashti Chaturthi",
        fasting_type=FastingType.TITHI_BASED,
        tithi_name=TithiName.CHATURTHI,
        paksha=Paksha.KRISHNA,
        description="Krishna Paksha Chaturthi dedicated to Ganesha, observed till moonrise."
    ),

    # --- Vinayaka Chaturthi ---
    FastingDay(
        name="Vinayaka Chaturthi",
        fasting_type=FastingType.TITHI_BASED,
        tithi_name=TithiName.CHATURTHI,
        paksha=Paksha.SHUKLA,
        description="Shukla Paksha Chaturthi dedicated to Ganesha."
    ),

    # --- Ashtami ---
    FastingDay(
        name="Ashtami",
        fasting_type=FastingType.TITHI_BASED,
        tithi_name=TithiName.ASHTAMI,
        description="Observed on the 8th lunar tithi, commonly associated with Devi worship."
    ),

    # --- Navami ---
    FastingDay(
        name="Navami",
        fasting_type=FastingType.TITHI_BASED,
        tithi_name=TithiName.NAVAMI,
        description="Observed on the 9th lunar tithi, notably during Navaratri."
    ),

    # --- Dwadashi ---
    FastingDay(
        name="Dwadashi",
        fasting_type=FastingType.TITHI_BASED,
        tithi_name=TithiName.DWADASHI,
        description="Observed on the 12th tithi, often marking the breaking of Ekadashi fast."
    ),

    # # --- Sankranti ---
    # FastingDay(
    #     name="Sankranti",
    #     fasting_type=FastingType.SOLAR_BASED,
    #     description="Observed when the Sun enters a new zodiac sign every 30 degrees."
    # ),

    # --- Makara Sankranti ---
    FastingDay(
        name="Makara Sankranti",
        fasting_type=FastingType.SOLAR_BASED,
        description="Observed when the Sun enters Makara Rashi, marking Uttarayana."
    ),
]
