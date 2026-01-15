from typing_extensions import Dict, Optional, Set, Union
from ripple_down_rules.datastructures.case import Case, create_case
from ripple_down_rules.utils import copy_case, make_set
from krrood_experiments.owl2bench.ontomatic.owl_instances_loader import URIType
from ripple_down_rules.helpers import get_an_updated_case_copy, update_case_and_conclusions_with_rule_output
from .owl_loader_infer_most_appropriate_types_for_anonymous_instances_output__mcrdr_defs import *


attribute_name = 'output_'
conclusion_type = (set, URIType, list,)
mutually_exclusive = False
name = 'output_'
case_type = Dict
case_name = 'owl_loader_infer_most_appropriate_types_for_anonymous_instances'


def classify(case: Dict, **kwargs) -> Set[URIType]:
    if not isinstance(case, Case):
        case = create_case(case, max_recursion_idx=3)
    else:
        case = copy_case(case)
    conclusions = set()

    if conditions_36442531050626921248523247604925620139(case):
        update_case_and_conclusions_with_rule_output(case, conclusions, conclusion_36442531050626921248523247604925620139(case),attribute_name, conclusion_type, mutually_exclusive)
    return conclusions
