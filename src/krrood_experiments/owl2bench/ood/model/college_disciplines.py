from dataclasses import dataclass

from .base import CollegeDiscipline


# %% Engineering
@dataclass(eq=False)
class Engineering(CollegeDiscipline): ...


@dataclass(eq=False)
class AeronauticalEngineering(Engineering): ...


@dataclass(eq=False)
class BiomedicalEngineering(Engineering): ...


@dataclass(eq=False)
class ChemicalEngineering(Engineering): ...


@dataclass(eq=False)
class CivilEngineering(Engineering): ...


@dataclass(eq=False)
class ComputerEngineering(Engineering): ...


@dataclass(eq=False)
class ElectricalEngineering(Engineering): ...


@dataclass(eq=False)
class IndustryEngineering(Engineering): ...


@dataclass(eq=False)
class MaterialScienceEngineering(Engineering): ...


@dataclass(eq=False)
class MechanicalEngineering(Engineering): ...


@dataclass(eq=False)
class PetroleumlEngineering(Engineering): ...


# %% Fine Arts
@dataclass(eq=False)
class FineArts(CollegeDiscipline): ...


@dataclass(eq=False)
class Architecture(FineArts): ...


@dataclass(eq=False)
class AsianArts(FineArts): ...


@dataclass(eq=False)
class Drama(FineArts): ...


@dataclass(eq=False)
class LatinArts(FineArts): ...


@dataclass(eq=False)
class MediaArtsAndSciences(FineArts): ...


@dataclass(eq=False)
class MedievalArts(FineArts): ...


@dataclass(eq=False)
class ModernArts(FineArts): ...


@dataclass(eq=False)
class MusicsClass(FineArts): ...


@dataclass(eq=False)
class PerformingArts(FineArts): ...


@dataclass(eq=False)
class TheatreAndDance(FineArts): ...


# %% Humanities and Social Sciences


@dataclass(eq=False)
class HumanitiesAndSocial(CollegeDiscipline): ...


@dataclass(eq=False)
class Anthropology(HumanitiesAndSocial): ...


@dataclass(eq=False)
class Economics(HumanitiesAndSocial): ...


@dataclass(eq=False)
class English(HumanitiesAndSocial): ...


@dataclass(eq=False)
class History(HumanitiesAndSocial): ...


@dataclass(eq=False)
class Humanities(HumanitiesAndSocial): ...


@dataclass(eq=False)
class Linguistics(HumanitiesAndSocial): ...


@dataclass(eq=False)
class ModernLanguages(HumanitiesAndSocial): ...


@dataclass(eq=False)
class Philosophy(HumanitiesAndSocial): ...


@dataclass(eq=False)
class Psychology(HumanitiesAndSocial): ...


@dataclass(eq=False)
class Religions(HumanitiesAndSocial): ...


# %% Management
@dataclass(eq=False)
class Management(CollegeDiscipline): ...


@dataclass(eq=False)
class DesignManagement(Management): ...


@dataclass(eq=False)
class FinancialAndAccountingManagement(Management): ...


@dataclass(eq=False)
class HumanResourceManagement(Management): ...


@dataclass(eq=False)
class MarketingManagement(Management): ...


@dataclass(eq=False)
class OperationsManagement(Management): ...


@dataclass(eq=False)
class ProjectManagement(Management): ...


@dataclass(eq=False)
class PublicRelationsManagement(Management): ...


@dataclass(eq=False)
class RiskManagement(Management): ...


@dataclass(eq=False)
class SalesManagement(Management): ...


@dataclass(eq=False)
class SupplyChainManagement(Management): ...
