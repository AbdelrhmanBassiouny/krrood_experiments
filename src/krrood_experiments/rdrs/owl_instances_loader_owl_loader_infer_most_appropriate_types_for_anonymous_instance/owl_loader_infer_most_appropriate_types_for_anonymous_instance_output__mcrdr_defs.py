from krrood.class_diagrams.utils import (
    Role,
    sort_classes_by_role_aware_inheritance_path_length,
)
from ripple_down_rules.datastructures.case import Case
from typing_extensions import Dict, List, Set, Union
from krrood_experiments.owl_instances_loader import OwlLoader
from krrood_experiments.utils import (
    get_most_specific_types,
    get_non_class_attribute_names_of_instance,
    AnonymousClass,
)
from ripple_down_rules import *


def conditions_20100493747705403503239541007013585584(case) -> bool:
    def conditions_for_owl_loader_infer_most_appropriate_types_for_anonymous_instance(
        self_: OwlLoader, instance: AnonymousClass, **kwargs
    ) -> bool:
        """Get conditions on whether it's possible to conclude a value for owl_loader_infer_most_appropriate_types_for_anonymous_instance.output_  of type ."""
        return len(
            instance.types
        ) == 1 and not get_non_class_attribute_names_of_instance(instance)

    return (
        conditions_for_owl_loader_infer_most_appropriate_types_for_anonymous_instance(
            **case
        )
    )


def conclusion_20100493747705403503239541007013585584(case) -> List[type]:
    def owl_loader_infer_most_appropriate_types_for_anonymous_instance(
        self_: OwlLoader, instance: AnonymousClass, **kwargs
    ) -> List[type]:
        """Get possible value(s) for owl_loader_infer_most_appropriate_types_for_anonymous_instance.output_  of type ."""
        return case.instance.types

    return owl_loader_infer_most_appropriate_types_for_anonymous_instance(**case)


def conditions_178686770575922948619403589971234626498(case) -> bool:
    def conditions_for_owl_loader_infer_most_appropriate_types_for_anonymous_instance(
        self_: OwlLoader, instance: AnonymousClass, **kwargs
    ) -> bool:
        """Get conditions on whether it's possible to conclude a value for owl_loader_infer_most_appropriate_types_for_anonymous_instance.output_  of type ."""
        inferred_types = self_.get_inferred_types_from_descriptors_domains_of_instance(
            instance
        )
        return len(instance.types) == 1 and all(
            issubclass(et, it)
            or (issubclass(et, Role) and issubclass(et.get_role_taker_type(), it))
            for et in instance.types
            for it in inferred_types
        )

    return (
        conditions_for_owl_loader_infer_most_appropriate_types_for_anonymous_instance(
            **case
        )
    )


def conclusion_178686770575922948619403589971234626498(case) -> List[type]:
    def owl_loader_infer_most_appropriate_types_for_anonymous_instance(
        self_: OwlLoader, instance: AnonymousClass, **kwargs
    ) -> List[type]:
        """Get possible value(s) for owl_loader_infer_most_appropriate_types_for_anonymous_instance.output_  of type ."""
        return list(case.instance.types)

    return owl_loader_infer_most_appropriate_types_for_anonymous_instance(**case)


def conditions_107546415252908647157514226735385206217(case) -> bool:
    def conditions_for_owl_loader_infer_most_appropriate_types_for_anonymous_instance(
        self_: OwlLoader, instance: AnonymousClass, **kwargs
    ) -> bool:
        """Get conditions on whether it's possible to conclude a value for owl_loader_infer_most_appropriate_types_for_anonymous_instance.output_  of type ."""
        return (
            len(
                case.self_.get_inferred_types_from_descriptors_domains_of_instance(
                    case.instance
                )
            )
            > 1
        )

    return (
        conditions_for_owl_loader_infer_most_appropriate_types_for_anonymous_instance(
            **case
        )
    )


def conclusion_107546415252908647157514226735385206217(case) -> List[type]:
    def owl_loader_infer_most_appropriate_types_for_anonymous_instance(
        self_: OwlLoader, instance: AnonymousClass, **kwargs
    ) -> List[type]:
        """Get possible value(s) for owl_loader_infer_most_appropriate_types_for_anonymous_instance.output_  of type ."""
        possible_types = self_.get_inferred_types_from_descriptors_domains_of_instance(
            instance
        )

        possible_types.update(instance.types)

        possible_types = get_most_specific_types(possible_types)

        return sort_classes_by_role_aware_inheritance_path_length(possible_types)

    return owl_loader_infer_most_appropriate_types_for_anonymous_instance(**case)
