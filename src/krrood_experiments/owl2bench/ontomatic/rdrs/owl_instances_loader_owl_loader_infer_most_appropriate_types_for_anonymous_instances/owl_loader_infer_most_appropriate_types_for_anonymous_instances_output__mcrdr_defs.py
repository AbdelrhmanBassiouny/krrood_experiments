from ripple_down_rules.datastructures.case import Case
from typing_extensions import Dict, List, Set, Type, Union
from collections import defaultdict
from krrood_experiments.owl2bench.ontomatic.owl_instances_loader import (
    OwlLoader,
    URIType,
)
from krrood.class_diagrams.utils import (
    issubclass_or_role,
    sort_classes_by_role_aware_inheritance_path_length,
)
from ripple_down_rules import *

from krrood_experiments.owl2bench.ontomatic.utils import (
    get_non_class_attribute_names_of_instance,
)


def conditions_36442531050626921248523247604925620139(case) -> bool:
    def conditions_for_owl_loader_infer_most_appropriate_types_for_anonymous_instances(
        self_: OwlLoader, **kwargs
    ) -> bool:
        """Get conditions on whether it's possible to conclude a value for owl_loader_infer_most_appropriate_types_for_anonymous_instances.output_  of type URIType."""
        return True

    return (
        conditions_for_owl_loader_infer_most_appropriate_types_for_anonymous_instances(
            **case
        )
    )


def conclusion_36442531050626921248523247604925620139(case) -> List[URIType]:
    def owl_loader_infer_most_appropriate_types_for_anonymous_instances(
        self_: OwlLoader, **kwargs
    ) -> List[URIType]:
        """Get possible value(s) for owl_loader_infer_most_appropriate_types_for_anonymous_instances.output_  of type URIType."""
        inferred_types: Set[URIType] = set()
        for instance in self_.anonymous_instances.values():
            non_class_fields = get_non_class_attribute_names_of_instance(instance)
            descriptors = [
                self_.metadata.get_descriptor_base(f) for f in non_class_fields
            ]
            descriptors = [d for d in descriptors if d is not None]
            for desc in descriptors:
                domains = desc.all_domains[desc]
                if len(domains) == 1:
                    dom = list(domains)[0]
                    inferred_types.add(URIType(instance.uri, dom))
                    try:
                        range_ = desc.get_descriptor_instance_for_domain_type(dom).range
                        for range_inst in getattr(instance, desc.get_field_name()):
                            inferred_types.add(URIType(range_inst.uri, range_))
                    except ValueError:
                        pass
                    continue
                domains = list(
                    reversed(
                        sort_classes_by_role_aware_inheritance_path_length(
                            tuple(domains)
                        )
                    )
                )
                range_inst_types_map: Dict[Type, Set[Type]] = defaultdict(set)
                for dom in domains:
                    if hasattr(dom, "axiom_python") and dom.axiom_python(instance):
                        inferred_types.add(URIType(instance.uri, dom))
                        try:
                            range_ = desc.get_descriptor_instance_for_domain_type(
                                dom
                            ).range
                            for range_inst in getattr(instance, desc.get_field_name()):
                                inferred_types.add(URIType(range_inst.uri, range_))
                        except ValueError:
                            pass
                        break
                    try:
                        range_ = desc.get_descriptor_instance_for_domain_type(dom).range
                    except ValueError:
                        continue
                    for range_inst in getattr(instance, desc.get_field_name()):
                        if range_inst not in range_inst_types_map:
                            range_inst_types_map[range_inst] = {
                                out.type
                                for out in kwargs["output_"]
                                if out.uri == range_inst.uri
                            }
                        # if str(instance.uri) == "http://benchmark/OWL2Bench#U0C0D1CS0":
                        #     import pdbpp
                        #
                        #     pdbpp.set_trace()
                        if any(
                            issubclass_or_role(it, range_)
                            for it in range_inst_types_map[range_inst]
                        ):
                            inferred_types.add(URIType(instance.uri, dom))
                            inferred_types.add(URIType(range_inst.uri, range_))
                            break
        return list(inferred_types)

    return owl_loader_infer_most_appropriate_types_for_anonymous_instances(**case)
