from enum import Enum
from dataclasses import dataclass
from typing import List, Optional


class UpavaasType(Enum):
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


class Tithi(Enum):
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
class TithiInfo:
    paksha: Paksha
    index: int
    name: Tithi

@dataclass(frozen=True)
class Upavaas:
    name: str
    upavaas_type: UpavaasType
    tithi: Optional[Tithi] = None
    paksha: Optional[Paksha] = None
    masa: Optional[Masa] = None
    description: str = ""


TITHIs: List[TithiInfo] = [
    *[
        TithiInfo(Paksha.SHUKLA, i + 1, name)
        for i, name in enumerate([
            Tithi.PRATIPADA,
            Tithi.DWITIYA,
            Tithi.TRITIYA,
            Tithi.CHATURTHI,
            Tithi.PANCHAMI,
            Tithi.SHASHTHI,
            Tithi.SAPTAMI,
            Tithi.ASHTAMI,
            Tithi.NAVAMI,
            Tithi.DASHAMI,
            Tithi.EKADASHI,
            Tithi.DWADASHI,
            Tithi.TRAYODASHI,
            Tithi.CHATURDASHI,
            Tithi.PURNIMA,
        ])
    ],
    *[
        TithiInfo(Paksha.KRISHNA, i + 1, name)
        for i, name in enumerate([
            Tithi.PRATIPADA,
            Tithi.DWITIYA,
            Tithi.TRITIYA,
            Tithi.CHATURTHI,
            Tithi.PANCHAMI,
            Tithi.SHASHTHI,
            Tithi.SAPTAMI,
            Tithi.ASHTAMI,
            Tithi.NAVAMI,
            Tithi.DASHAMI,
            Tithi.EKADASHI,
            Tithi.DWADASHI,
            Tithi.TRAYODASHI,
            Tithi.CHATURDASHI,
            Tithi.AMAVASYA,
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
UPAVAASs: List[Upavaas] = [
    # --- Ekadashi ---
    Upavaas(
        name="Ekadashi",
        upavaas=UpavaasType.MIXED_TIME_RULE,
        tithi=Tithi.EKADASHI,
        description="Observed on the 11th lunar tithi when it prevails at local sunrise."
    ),

    # --- Pradosha ---
    Upavaas(
        name="Pradosha",
        upavaas=UpavaasType.MIXED_TIME_RULE,
        tithi=Tithi.TRAYODASHI,
        description="Observed on the 13th tithi during the evening twilight period."
    ),

    # --- Maha Shivaratri ---
    Upavaas(
        name="Maha Shivaratri",
        upavaas=UpavaasType.MIXED_TIME_RULE,
        tithi=Tithi.CHATURDASHI,
        paksha=Paksha.KRISHNA,
        masa=Masa.MAGHA,
        description="Krishna Paksha Chaturdashi of Magha, observed mainly during night."
    ),

    # --- Amavasya ---
    Upavaas(
        name="Amavasya",
        upavaas=UpavaasType.TITHI_BASED,
        tithi=Tithi.AMAVASYA,
        description="Observed on the new moon when Moon–Sun longitude difference reaches 360°."
    ),

    # --- Purnima ---
    Upavaas(
        name="Purnima",
        upavaas=UpavaasType.TITHI_BASED,
        tithi=Tithi.PURNIMA,
        description="Observed on the full moon when Moon–Sun longitude difference reaches 180°."
    ),

    # --- Sankashti Chaturthi ---
    Upavaas(
        name="Sankashti Chaturthi",
        upavaas=UpavaasType.TITHI_BASED,
        tithi=Tithi.CHATURTHI,
        paksha=Paksha.KRISHNA,
        description="Krishna Paksha Chaturthi dedicated to Ganesha, observed till moonrise."
    ),

    # --- Vinayaka Chaturthi ---
    Upavaas(
        name="Vinayaka Chaturthi",
        upavaas=UpavaasType.TITHI_BASED,
        tithi=Tithi.CHATURTHI,
        paksha=Paksha.SHUKLA,
        description="Shukla Paksha Chaturthi dedicated to Ganesha."
    ),

    # --- Ashtami ---
    Upavaas(
        name="Ashtami",
        upavaas=UpavaasType.TITHI_BASED,
        tithi=Tithi.ASHTAMI,
        description="Observed on the 8th lunar tithi, commonly associated with Devi worship."
    ),

    # --- Navami ---
    Upavaas(
        name="Navami",
        upavaas=UpavaasType.TITHI_BASED,
        tithi=Tithi.NAVAMI,
        description="Observed on the 9th lunar tithi, notably during Navaratri."
    ),

    # --- Dwadashi ---
    Upavaas(
        name="Dwadashi",
        upavaas=UpavaasType.TITHI_BASED,
        tithi=Tithi.DWADASHI,
        description="Observed on the 12th tithi, often marking the breaking of Ekadashi fast."
    ),

    # # --- Sankranti ---
    # Upavaas(
    #     name="Sankranti",PRATIPADA
    #     upavaas=UpavaasType.SOLAR_BASED,
    #     description="Observed when the Sun enters a new zodiac sign every 30 degrees."
    # ),

    # --- Makara Sankranti ---
    Upavaas(
        name="Makara Sankranti",
        upavaas=UpavaasType.SOLAR_BASED,
        description="Observed when the Sun enters Makara Rashi, marking Uttarayana."
    ),
]
