from typing_extensions import Dict, List, Set, Union
from krrood.class_diagrams.utils import Role, nearest_common_ancestor
from krrood.entity_query_language.entity import has_solution
from krrood_experiments.utils import AnonymousClass, get_most_specific_types, get_non_class_attribute_names_of_instance
from krrood_experiments.owl_instances_loader import OwlLoader
from abc import ABC
from ripple_down_rules import *


def conditions_20100493747705403503239541007013585584(case) -> bool:
                def conditions_for_owl_loader_infer_most_appropriate_types_for_anonymous_instance(
                    self_: OwlLoader, instance: AnonymousClass, **kwargs
                ) -> bool:
                    """Get conditions on whether it's possible to conclude a value for owl_loader_infer_most_appropriate_types_for_anonymous_instance.output_  of type ."""
                    return len(instance.types) == 1 and not bool(
                        get_non_class_attribute_names_of_instance(instance)
                    )
    
                return (
                    conditions_for_owl_loader_infer_most_appropriate_types_for_anonymous_instance(
                        **case
                    )
                )


def conclusion_20100493747705403503239541007013585584(case) -> List[type]:
    def owl_loader_infer_most_appropriate_types_for_anonymous_instance(self_: OwlLoader, instance: AnonymousClass, **kwargs) -> List[type]:
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
                    return (
                        len(instance.types) == 1
                        and bool(inferred_types)
                        and inferred_types != instance.types
                        and all(
                            issubclass(et, it)
                            or (issubclass(et, Role) and issubclass(et.get_role_taker_type(), it))
                            for et in instance.types
                            for it in inferred_types
                        )
                    )
    
                return (
                    conditions_for_owl_loader_infer_most_appropriate_types_for_anonymous_instance(
                        **case
                    )
                )


def conclusion_178686770575922948619403589971234626498(case) -> List[type]:
    def owl_loader_infer_most_appropriate_types_for_anonymous_instance(self_: OwlLoader, instance: AnonymousClass, **kwargs) -> List[type]:
        """Get possible value(s) for owl_loader_infer_most_appropriate_types_for_anonymous_instance.output_  of type ."""
        return list(case.instance.types)
    return owl_loader_infer_most_appropriate_types_for_anonymous_instance(**case)


def conditions_39422379577793614665216170177046282573(case) -> bool:
                def conditions_for_owl_loader_infer_most_appropriate_types_for_anonymous_instance(
                    self_: OwlLoader, instance: AnonymousClass, **kwargs
                ) -> bool:
                    """Get conditions on whether it's possible to conclude a value for owl_loader_infer_most_appropriate_types_for_anonymous_instance.output_  of type ."""
                    return not bool(case.output_)
    
                return (
                    conditions_for_owl_loader_infer_most_appropriate_types_for_anonymous_instance(
                        **case
                    )
                )


def conclusion_39422379577793614665216170177046282573(case) -> List[type]:
    def owl_loader_infer_most_appropriate_types_for_anonymous_instance(self_: OwlLoader, instance: AnonymousClass, **kwargs) -> List[type]:
        """Get possible value(s) for owl_loader_infer_most_appropriate_types_for_anonymous_instance.output_  of type ."""
        contesting_types = set()
        inferred_types = self_.get_inferred_types_from_descriptors_domains_of_instance(instance)
        explicit_types = instance.types
        all_types = list(set(inferred_types).union(set(explicit_types)))
        for i, c1 in enumerate(all_types[:-1]):
            for c2 in all_types[i + 1:]:
                nca = nearest_common_ancestor([c1, c2])
                if nca in [Role, ABC, object, None]:
                    continue
                contesting_types.update({c1, c2})
        non_contesting_types = set(all_types) - contesting_types
        types_with_satisfied_axioms = [t for t in contesting_types if not hasattr(t, 'axiom') or has_solution(instance, t.axiom)]
        final_types = non_contesting_types.union(set(types_with_satisfied_axioms))
        most_specific_types = get_most_specific_types(final_types)
        return most_specific_types
    return owl_loader_infer_most_appropriate_types_for_anonymous_instance(**case)


