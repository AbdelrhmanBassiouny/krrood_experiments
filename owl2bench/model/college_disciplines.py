from dataclasses import dataclass

from .base import CollegeDiscipline


# %% Engineering
@dataclass
class Engineering(CollegeDiscipline): ...


@dataclass
class AeronauticalEngineering(Engineering): ...


@dataclass
class BiomedicalEngineering(Engineering): ...


@dataclass
class ChemicalEngineering(Engineering): ...


@dataclass
class CivilEngineering(Engineering): ...


@dataclass
class ComputerEngineering(Engineering): ...


@dataclass
class ElectricalEngineering(Engineering): ...


@dataclass
class IndustryEngineering(Engineering): ...


@dataclass
class MaterialScienceEngineering(Engineering): ...


@dataclass
class MechanicalEngineering(Engineering): ...


@dataclass
class PetroleumlEngineering(Engineering): ...


# %% Fine Arts
@dataclass
class FineArts(CollegeDiscipline): ...


@dataclass
class Architecture(FineArts): ...


@dataclass
class AsianArts(FineArts): ...


@dataclass
class Drama(FineArts): ...


@dataclass
class LatinArts(FineArts): ...


@dataclass
class MediaArtsAndSciences(FineArts): ...


@dataclass
class MedievalArts(FineArts): ...


@dataclass
class ModernArts(FineArts): ...


@dataclass
class MusicsClass(FineArts): ...


@dataclass
class PerformingArts(FineArts): ...


@dataclass
class TheatreAndDance(FineArts): ...


# %% Humanities and Social Sciences


@dataclass
class HumanitiesAndSocial(CollegeDiscipline): ...


@dataclass
class Anthropology(HumanitiesAndSocial): ...


@dataclass
class Economics(HumanitiesAndSocial): ...


@dataclass
class English(HumanitiesAndSocial): ...


@dataclass
class History(HumanitiesAndSocial): ...


@dataclass
class Humanities(HumanitiesAndSocial): ...


@dataclass
class Linguistics(HumanitiesAndSocial): ...


@dataclass
class ModernLanguages(HumanitiesAndSocial): ...


@dataclass
class Philosophy(HumanitiesAndSocial): ...


@dataclass
class Psychology(HumanitiesAndSocial): ...


@dataclass
class Religions(HumanitiesAndSocial): ...


# %% Management
@dataclass
class Management(CollegeDiscipline): ...


@dataclass
class DesignManagement(Management): ...


@dataclass
class FinancialAndAccountingManagement(Management): ...


@dataclass
class HumanResourceManagement(Management): ...


@dataclass
class MarketingManagement(Management): ...


@dataclass
class OperationsManagement(Management): ...


@dataclass
class ProjectManagement(Management): ...


@dataclass
class PublicRelationsManagement(Management): ...


@dataclass
class RiskManagement(Management): ...


@dataclass
class SalesManagement(Management): ...


@dataclass
class SupplyChainManagement(Management): ...
