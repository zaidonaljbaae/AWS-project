#Services
from enum import Enum

class AnaliseSpedEnum(Enum):
    C100 = 'C100'
    C170 = 'C170'
    NOTA = 'NOTA'
    ITEM = 'ITEM'
    ERROR_FISCAL_C100 = 'Invoice XML not available - SPED Fiscal'
    ERROR_FISCAL_NOTA = 'Invoice XML not found in the SPED Fiscal'
    ERROR_FISCAL_C170 = 'Item not found in invoice XML - SPED Fiscal'
    ERROR_FISCAL_ITEM = 'Invoice item not found in the Fiscal SPED'
    ERROR_CONTRIB_C100 = 'Invoice XML not available - SPED Contribuição'
    ERROR_CONTRIB_NOTA = 'Invoice XML not found in the SPED Contribuição'
    ERROR_CONTRIB_C170 = 'Item not found in invoice XML - SPED Contribuição'
    ERROR_CONTRIB_ITEM = 'Invoice item not found in the SPED Contribuição'
 