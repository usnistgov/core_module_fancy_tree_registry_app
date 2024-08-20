""" Fancy Tree module view
"""

import re

from core_main_registry_app.components.category import api as category_api
from core_main_registry_app.components.refinement import api as refinement_api
from core_main_registry_app.components.template import (
    api as template_registry_api,
)
from core_main_registry_app.constants import CATEGORY_SUFFIX, UNSPECIFIED_LABEL
from core_parser_app.tools.modules.exceptions import ModuleError
from core_parser_app.tools.modules.views.module import AbstractModule
from xml_utils.xsd_tree.xsd_tree import XSDTree
from core_module_fancy_tree_registry_app.views.forms import RefinementForm


class FancyTreeModule(AbstractModule):
    """Fancy Tree Module"""

    is_managing_occurrences = True

    def __init__(self):
        AbstractModule.__init__(
            self,
            scripts=["core_module_fancy_tree_registry_app/js/fancy_tree.js"],
        )

    def _reload_data(self, field_id, refinement):
        if self.data == "":  # If no data is provided, the form will be empty.
            return {}

        # Get the categories for the current refinement
        categories = category_api.get_all_filtered_by_refinement_id(
            refinement.id
        )
        # Initialize list of categories id
        reload_categories_id_list = []
        # Load list of data to reload from XML
        reload_data = XSDTree.fromstring(f"<root>{self.data}</root>")
        # Iterate xml elements
        for reload_data_element in list(reload_data):
            try:
                if len(reload_data_element) == 0:
                    continue

                # The xml element value to be reloaded is the child element
                selected_value = reload_data_element[0].text
                # find the corresponding category and add its id to the list
                category = categories.get(value=selected_value)
                # if the element is an unspecified element
                if category.slug.startswith(UNSPECIFIED_LABEL):
                    # get the parent category
                    category = categories.get(
                        value=f"{selected_value}{CATEGORY_SUFFIX}"
                    )

                reload_categories_id_list.append(category.id)
            except Exception as exception:
                raise ModuleError(
                    "Something went wrong when reloading data from XML."
                    + str(exception)
                )

        # set data to reload in the form
        return {
            f"{RefinementForm.prefix}-{field_id}": reload_categories_id_list
        }

    def _render_module(self, request):
        # get the xml path of the element on which the module is placed
        xml_xpath = request.GET.get("xml_xpath", None)
        # xml path is provided
        if xml_xpath is None:
            raise ModuleError(
                "xml_xpath was not found in request GET parameters."
            )

        try:
            # create unique field id from xpath
            field_id = re.sub(r"[/.:\[\]]", "", xml_xpath)
            # get the last element of the xpath
            xml_element = xml_xpath.split("/")[-1]
            # only keep element name if namespace is present
            if ":" in xml_element:
                xml_element = xml_element.split(":")[-1]

            # get registry template
            template = template_registry_api.get_current_registry_template(
                request=request
            )
            # get all refinements for this template
            refinement_query_set = (
                refinement_api.get_all_filtered_by_template_hash(template.hash)
            )
            # get the refinement for the xml element
            refinement = refinement_query_set.get(xsd_name=xml_element)

            return AbstractModule.render_template(
                "core_module_fancy_tree_registry_app/fancy_tree.html",
                {
                    "form": RefinementForm(
                        refinement=refinement,
                        field_id=field_id,
                        data=self._reload_data(field_id, refinement),
                    )
                },
            )
        except Exception as exception:
            raise ModuleError(
                "Something went wrong when rendering the module: "
                + str(exception)
            )

    def _retrieve_data(self, request):
        if request.method == "GET":
            return request.GET.get("data", "")

        if request.method == "POST":
            form = RefinementForm(request.POST)
            if not form.is_valid():
                raise ModuleError("Data not properly sent to server.")

            if "data[]" not in request.POST:
                return ""

            data = ""
            try:
                category_id_list = request.POST.getlist("data[]")
                for category_id in category_id_list:
                    category = category_api.get_by_id(category_id)
                    split_category_path = category.path.split(".")
                    category_value = (
                        category.value
                        if not category.value.endswith(CATEGORY_SUFFIX)
                        else category.value[: -len(CATEGORY_SUFFIX)]
                    )

                    data += f"<{split_category_path[-2]}><{split_category_path[-1]}>{category_value}</{split_category_path[-1]}></{split_category_path[-2]}>"
            except Exception as exception:
                raise ModuleError(
                    "Something went wrong during the processing of posted data: "
                    + str(exception)
                )

            return data

    def _render_data(self, request):
        return ""
