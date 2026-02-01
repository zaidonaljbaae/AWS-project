#Services
from enum import Enum

class TipoSpedEnum(Enum):
    SPED_FISCAL = 'EFD - ICMS/IPI'
    SPED_CONTRIB = 'EFD - Contribuições'
    ECD = 'ECD'
    ECF = 'ECF'
