from ripple_down_rules.helpers import general_rdr_classify
from typing_extensions import Any, Dict
from ripple_down_rules.datastructures.case import Case, create_case
from . import owl_loader_infer_most_appropriate_types_for_anonymous_instance_output__mcrdr as output__classifier

name = 'output_'
case_type = Dict
case_name = 'owl_loader_infer_most_appropriate_types_for_anonymous_instance'
classifiers_dict = dict()
classifiers_dict['output_'] = output__classifier


def classify(case: Dict, **kwargs) -> Dict[str, Any]:
    if not isinstance(case, Case):
        case = create_case(case, max_recursion_idx=3)
    return general_rdr_classify(classifiers_dict, case, **kwargs)
