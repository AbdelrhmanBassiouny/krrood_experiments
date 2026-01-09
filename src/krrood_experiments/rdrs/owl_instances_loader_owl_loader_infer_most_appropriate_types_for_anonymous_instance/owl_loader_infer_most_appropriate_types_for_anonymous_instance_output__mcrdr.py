from typing_extensions import Dict, Optional, Set, Union
from ripple_down_rules.utils import copy_case, make_set
from ripple_down_rules.datastructures.case import Case, create_case
from ripple_down_rules.helpers import get_an_updated_case_copy, update_case_and_conclusions_with_rule_output
from .owl_loader_infer_most_appropriate_types_for_anonymous_instance_output__mcrdr_defs import *


attribute_name = 'output_'
conclusion_type = (list, type,)
mutually_exclusive = False
name = 'output_'
case_type = Dict
case_name = 'owl_loader_infer_most_appropriate_types_for_anonymous_instance'


def classify(case: Dict, **kwargs) -> Set[type]:
    if not isinstance(case, Case):
        case = create_case(case, max_recursion_idx=3)
    else:
        case = copy_case(case)
    conclusions = set()

    if conditions_20100493747705403503239541007013585584(case):
        update_case_and_conclusions_with_rule_output(case, conclusions, conclusion_20100493747705403503239541007013585584(case),attribute_name, conclusion_type, mutually_exclusive)

    if conditions_178686770575922948619403589971234626498(case):
        update_case_and_conclusions_with_rule_output(case, conclusions, conclusion_178686770575922948619403589971234626498(case),attribute_name, conclusion_type, mutually_exclusive)

    if conditions_39422379577793614665216170177046282573(case):
        update_case_and_conclusions_with_rule_output(case, conclusions, conclusion_39422379577793614665216170177046282573(case),attribute_name, conclusion_type, mutually_exclusive)

    if conditions_199871154586794138198665296345684269309(case):
        update_case_and_conclusions_with_rule_output(case, conclusions, conclusion_199871154586794138198665296345684269309(case),attribute_name, conclusion_type, mutually_exclusive)
    return conclusions
