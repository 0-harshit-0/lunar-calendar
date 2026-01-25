from enum import Enum
from dataclasses import dataclass
from typing import List


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


@dataclass(frozen=True)
class Tithi:
    paksha: Paksha
    index: int
    name: TithiName


TITHIS: List[Tithi] = [
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
