from enum import Enum
from dataclasses import dataclass
from typing import List


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
