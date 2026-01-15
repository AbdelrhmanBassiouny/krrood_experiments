from ripple_down_rules.utils import make_set
from ripple_down_rules.datastructures.case import Case
from krrood.class_diagrams.utils import (
    Role,
    issubclass_or_role,
    nearest_common_ancestor,
    role_aware_nearest_common_ancestor,
)
from krrood_experiments.owl2bench.ontomatic.owl_instances_loader import OwlLoader
from collections import defaultdict
from typing_extensions import List
from krrood_experiments.owl2bench.ontomatic.utils import (
    AnonymousClass,
    get_most_specific_types,
    get_non_class_attribute_names_of_instance,
)
from krrood.ontomatic.property_descriptor.property_descriptor import PropertyDescriptor
from krrood.entity_query_language.entity import has_solution
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
        return (
            len(instance.types) == 1
            and bool(inferred_types)
            and inferred_types != instance.types
            and all(
                issubclass_or_role(et, it)
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
    def owl_loader_infer_most_appropriate_types_for_anonymous_instance(
        self_: OwlLoader, instance: AnonymousClass, **kwargs
    ) -> List[type]:
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
    def owl_loader_infer_most_appropriate_types_for_anonymous_instance(
        self_: OwlLoader, instance: AnonymousClass, **kwargs
    ) -> List[type]:
        """Get possible value(s) for owl_loader_infer_most_appropriate_types_for_anonymous_instance.output_  of type ."""
        contesting_types = set()
        inferred_types = self_.get_inferred_types_from_descriptors_domains_of_instance(
            instance
        )
        explicit_types = instance.types
        inferred_list = list(inferred_types)
        contesting_types_by_ancestors = defaultdict(set)
        for i, c1 in enumerate(inferred_list[:-1]):
            for c2 in inferred_list[i + 1 :]:
                nca = nearest_common_ancestor([c1, c2])
                if nca in [Role, ABC, object, None]:
                    continue
                contesting_types_by_ancestors[nca].update({c1, c2})
                contesting_types.update({c1, c2})
        non_contesting_types = inferred_types - contesting_types
        for nct in non_contesting_types:
            contesting_types_by_ancestors[nct].add(nct)
        final_ancestors = list(contesting_types_by_ancestors.keys())
        for i, a1 in enumerate(final_ancestors[:-1]):
            for a2 in final_ancestors[i + 1 :]:
                try:
                    if issubclass(a1, a2):
                        final_ancestors.remove(a1)
                    elif issubclass(a2, a1):
                        final_ancestors.remove(a2)
                except ValueError:
                    pass
        final_types = set(final_ancestors).union(explicit_types)
        most_specific_types = get_most_specific_types(final_types)
        return most_specific_types

    return owl_loader_infer_most_appropriate_types_for_anonymous_instance(**case)


def conditions_199871154586794138198665296345684269309(case) -> bool:
    def conditions_for_owl_loader_infer_most_appropriate_types_for_anonymous_instance(
        self_: OwlLoader, instance: AnonymousClass, **kwargs
    ) -> bool:
        """Get conditions on whether it's possible to conclude a value for owl_loader_infer_most_appropriate_types_for_anonymous_instance.output_  of type ."""
        # output = kwargs["output_"]
        # return len(output) == 0
        return True

    return (
        conditions_for_owl_loader_infer_most_appropriate_types_for_anonymous_instance(
            **case
        )
    )


def conclusion_199871154586794138198665296345684269309(case) -> List[type]:
    def owl_loader_infer_most_appropriate_types_for_anonymous_instance(
        self_: OwlLoader, instance: AnonymousClass, **kwargs
    ) -> List[type]:
        """Get possible value(s) for owl_loader_infer_most_appropriate_types_for_anonymous_instance.output_  of type ."""
        pred_subjects = self_.obj_pred_subj_map[instance.uri]
        ranges = set()
        for pred, subjects in pred_subjects.items():
            ranges.update(
                PropertyDescriptor.all_ranges[self_.metadata.get_descriptor_base(pred)]
            )
        current_types = instance.types.union(make_set(kwargs["output_"]))
        if len(ranges) and all(
            (issubclass_or_role(ct, tuple(ranges)) for ct in current_types)
        ):
            return []
        ancestor = role_aware_nearest_common_ancestor(tuple(ranges))
        if ancestor is None:
            return []
        return ancestor

    return owl_loader_infer_most_appropriate_types_for_anonymous_instance(**case)


def conditions_308052122250742423873206453845882804138(case) -> bool:
    def conditions_for_owl_loader_infer_most_appropriate_types_for_anonymous_instance(
        self_: OwlLoader, instance: AnonymousClass, **kwargs
    ) -> bool:
        """Get conditions on whether it's possible to conclude a value for owl_loader_infer_most_appropriate_types_for_anonymous_instance.output_  of type ."""
        return (
            len(instance.types) == 0
            and len(kwargs["output_"]) == 0
            and self_.metadata.get_python_class(instance.uri) is None
        )

    return (
        conditions_for_owl_loader_infer_most_appropriate_types_for_anonymous_instance(
            **case
        )
    )


def conclusion_308052122250742423873206453845882804138(case) -> List[type]:
    def owl_loader_infer_most_appropriate_types_for_anonymous_instance(
        self_: OwlLoader, instance: AnonymousClass, **kwargs
    ) -> List[type]:
        """Get possible value(s) for owl_loader_infer_most_appropriate_types_for_anonymous_instance.output_  of type ."""
        return [self_.metadata.ontology_base_class]

    return owl_loader_infer_most_appropriate_types_for_anonymous_instance(**case)


def conditions_156662505516608460529403101557922300371(case) -> bool:
    def conditions_for_owl_loader_infer_most_appropriate_types_for_anonymous_instance(
        self_: OwlLoader, instance: AnonymousClass, **kwargs
    ) -> bool:
        """Get conditions on whether it's possible to conclude a value for owl_loader_infer_most_appropriate_types_for_anonymous_instance.output_  of type ."""
        return (
            len(instance.types) == 0
            and len(kwargs["output_"]) == 0
            and self_.metadata.get_python_class(instance.uri) is not None
        )

    return (
        conditions_for_owl_loader_infer_most_appropriate_types_for_anonymous_instance(
            **case
        )
    )


def conclusion_156662505516608460529403101557922300371(case) -> List[type]:
    def owl_loader_infer_most_appropriate_types_for_anonymous_instance(
        self_: OwlLoader, instance: AnonymousClass, **kwargs
    ) -> List[type]:
        """Get possible value(s) for owl_loader_infer_most_appropriate_types_for_anonymous_instance.output_  of type ."""
        return [self_.metadata.get_python_class(instance.uri)]

    return owl_loader_infer_most_appropriate_types_for_anonymous_instance(**case)


def conditions_60769889497012087197446453003101494103(case) -> bool:
    def conditions_for_owl_loader_infer_most_appropriate_types_for_anonymous_instance(
        self_: OwlLoader, instance: AnonymousClass, **kwargs
    ) -> bool:
        """Get conditions on whether it's possible to conclude a value for owl_loader_infer_most_appropriate_types_for_anonymous_instance.output_  of type ."""
        return True

    return (
        conditions_for_owl_loader_infer_most_appropriate_types_for_anonymous_instance(
            **case
        )
    )


def conclusion_60769889497012087197446453003101494103(case) -> List[type]:
    def owl_loader_infer_most_appropriate_types_for_anonymous_instance(
        self_: OwlLoader, instance: AnonymousClass, **kwargs
    ) -> List[type]:
        """Get possible value(s) for owl_loader_infer_most_appropriate_types_for_anonymous_instance.output_  of type ."""
        non_class_fields = get_non_class_attribute_names_of_instance(instance)
        ds = {self_.metadata.get_descriptor_base(d) for d in non_class_fields}
        all_classes = set()
        for d in ds:
            if d is None:
                continue
            all_classes.update(d.all_domains[d])
        classes_that_satsify_the_axioms = [
            c
            for c in all_classes
            if hasattr(c, "axiom_python") and c.axiom_python(instance)
        ]
        most_specific_classes = get_most_specific_types(classes_that_satsify_the_axioms)
        if len(most_specific_classes) > 1:
            nca = nearest_common_ancestor(most_specific_classes)
            if (
                nca is not case.self_.metadata.ontology_base_class
                and issubclass(nca, case.self_.metadata.ontology_base_class)
                and case.instance.types
            ):
                explicit_classes = get_most_specific_types(case.instance.types)
                final_classes = {
                    c
                    for c in most_specific_classes
                    if issubclass_or_role(c, tuple(explicit_classes))
                }
            else:
                final_classes = most_specific_classes
        else:
            final_classes = most_specific_classes
        return final_classes

    return owl_loader_infer_most_appropriate_types_for_anonymous_instance(**case)
