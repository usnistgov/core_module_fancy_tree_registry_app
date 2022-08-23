""" Refinement Form.
"""
from django import forms

from core_main_registry_app.components.category import api as category_api
from core_main_registry_app.constants import UNSPECIFIED_LABEL
from core_main_registry_app.utils.fancytree.widget import FancyTreeWidget


class RefinementForm(forms.Form):
    """Refinement Form"""

    prefix = "refinement"

    def __init__(self, *args, **kwargs):
        refinement = kwargs.pop("refinement", None)
        field_id = kwargs.pop("field_id", None)
        super().__init__(*args, **kwargs)
        if refinement and field_id:
            # Get categories except unspecified (those should be selected by checking a parent node)
            categories = category_api.get_all_filtered_by_refinement_id(
                refinement.id
            ).exclude(name__startswith=UNSPECIFIED_LABEL)
            self.fields[field_id] = forms.ModelMultipleChoiceField(
                queryset=categories,
                required=False,
                label="",
                widget=FancyTreeWidget(queryset=categories, select_mode=2),
            )
