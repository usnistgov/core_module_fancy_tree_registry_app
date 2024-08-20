""" Unit tests for the `core_module_fancy_tree_registry_app.views.views` package.
"""

from unittest import TestCase
from unittest.mock import patch, MagicMock, call, Mock

from core_main_registry_app.constants import (
    UNSPECIFIED_LABEL,
    CATEGORY_SUFFIX,
)
from core_module_fancy_tree_registry_app.views import (
    views as module_fancy_tree_views,
)
from core_module_fancy_tree_registry_app.views.forms import RefinementForm
from core_parser_app.tools.modules.exceptions import ModuleError


class TestFancyTreeModuleInit(TestCase):
    """Unit tests for the `__init__` method of `FancyTreeModule` class."""

    @patch(
        "core_parser_app.tools.modules.views.module.AbstractModule.__init__"
    )
    def test_abstract_module_init_called(self, mock_abstract_module_init):
        """test_abstract_module_init_called"""
        mock_module = module_fancy_tree_views.FancyTreeModule()

        mock_abstract_module_init.assert_called_with(
            mock_module,
            scripts=["core_module_fancy_tree_registry_app/js/fancy_tree.js"],
        )

    @patch.object(module_fancy_tree_views, "AbstractModule")
    def test_is_managing_occurence_true(self, mock_abstract_module):
        """test_is_managing_occurence_true"""
        mock_module = module_fancy_tree_views.FancyTreeModule()
        self.assertTrue(mock_module.is_managing_occurrences)


class TestFancyTreeModuleReloadData(TestCase):
    """Unit tests for the `_reload_data` method of `FancyTreeModule` class."""

    def setUp(self):
        """setUp"""
        self.mock_kwargs = {"field_id": MagicMock(), "refinement": MagicMock()}

        self.mock_module = module_fancy_tree_views.FancyTreeModule()
        self.mock_module.data = MagicMock()

    def test_no_data_returns_empty_dict(self):
        """test_no_data_returns_empty_dict"""
        self.mock_module.data = ""
        self.assertDictEqual(
            self.mock_module._reload_data(**self.mock_kwargs), {}
        )

    @patch.object(module_fancy_tree_views, "category_api")
    @patch.object(module_fancy_tree_views, "XSDTree")
    def test_get_all_filtered_by_refinement_id_called(
        self, mock_xsd_tree, mock_category_api
    ):
        """test_get_all_filtered_by_refinement_id_called"""
        self.mock_module._reload_data(**self.mock_kwargs)
        mock_category_api.get_all_filtered_by_refinement_id.assert_called_with(
            self.mock_kwargs["refinement"].id
        )

    @patch.object(module_fancy_tree_views, "category_api")
    @patch.object(module_fancy_tree_views, "XSDTree")
    def test_xsd_tree_from_string_called(
        self, mock_xsd_tree, mock_category_api
    ):
        """test_xsd_tree_from_string_called"""
        self.mock_module._reload_data(**self.mock_kwargs)
        mock_xsd_tree.fromstring.assert_called_with(
            f"<root>{self.mock_module.data}</root>"
        )

    @patch.object(module_fancy_tree_views, "category_api")
    @patch.object(module_fancy_tree_views, "XSDTree")
    def test_categories_get_called(self, mock_xsd_tree, mock_category_api):
        """test_categories_get_called"""
        mock_category = MagicMock()
        mock_category.slug = "mock_category_name"
        mock_categories = MagicMock()
        mock_categories.get.return_value = mock_category
        mock_category_api.get_all_filtered_by_refinement_id.return_value = (
            mock_categories
        )

        mock_xsd_element = MagicMock()
        mock_xsd_tree.fromstring.return_value = [[mock_xsd_element]]

        self.mock_module._reload_data(**self.mock_kwargs)
        mock_categories.get.assert_called_with(value=mock_xsd_element.text)

    @patch.object(module_fancy_tree_views, "category_api")
    @patch.object(module_fancy_tree_views, "XSDTree")
    def test_categories_get_not_called_if_item_is_empty(
        self, mock_xsd_tree, mock_category_api
    ):
        """test_categories_get_not_called_if_item_is_empty"""
        mock_categories = MagicMock()
        mock_category_api.get_all_filtered_by_refinement_id.return_value = (
            mock_categories
        )

        mock_xsd_tree.fromstring.return_value = [[]]

        self.mock_module._reload_data(**self.mock_kwargs)
        mock_categories.get.assert_not_called()

    @patch.object(module_fancy_tree_views, "category_api")
    @patch.object(module_fancy_tree_views, "XSDTree")
    def test_categories_get_has_multiple_calls_if_unspecified(
        self, mock_xsd_tree, mock_category_api
    ):
        """test_categories_get_has_multiple_calls_if_unspecified"""
        mock_category = MagicMock()
        mock_category.slug = f"{UNSPECIFIED_LABEL}_label"

        mock_categories = MagicMock()
        mock_categories.get.return_value = mock_category
        mock_category_api.get_all_filtered_by_refinement_id.return_value = (
            mock_categories
        )

        mock_xsd_element = MagicMock()
        mock_xsd_tree.fromstring.return_value = [[mock_xsd_element]]

        self.mock_module._reload_data(**self.mock_kwargs)

        mock_categories.get.assert_has_calls(
            [
                call(value=mock_xsd_element.text),
                call(value=f"{mock_xsd_element.text}{CATEGORY_SUFFIX}"),
            ]
        )

    @patch.object(module_fancy_tree_views, "category_api")
    @patch.object(module_fancy_tree_views, "XSDTree")
    def test_categories_get_exception_raises_module_error(
        self, mock_xsd_tree, mock_category_api
    ):
        """test_categories_get_exception_raises_module_error"""
        mock_categories = MagicMock()
        mock_categories.get.side_effect = Exception(
            "mock_categories_get_exception"
        )
        mock_category_api.get_all_filtered_by_refinement_id.return_value = (
            mock_categories
        )

        mock_xsd_element = MagicMock()
        mock_xsd_tree.fromstring.return_value = [[mock_xsd_element]]

        with self.assertRaises(ModuleError):
            self.mock_module._reload_data(**self.mock_kwargs)

    @patch.object(module_fancy_tree_views, "category_api")
    @patch.object(module_fancy_tree_views, "XSDTree")
    def test_returns_data_dict(self, mock_xsd_tree, mock_category_api):
        """test_returns_data_dict"""
        mock_category_specified = MagicMock()
        mock_category_specified_id = 1
        mock_category_specified.id = mock_category_specified_id
        mock_category_specified.slug = "mock_specified_category"
        mock_category_unspecified = MagicMock()
        mock_category_unspecified_id = 2
        mock_category_unspecified.id = mock_category_unspecified_id
        mock_category_unspecified.slug = f"{UNSPECIFIED_LABEL}_label"

        mock_categories = MagicMock()
        mock_categories.get.side_effect = [
            mock_category_specified,
            mock_category_unspecified,
            mock_category_unspecified,
        ]
        mock_category_api.get_all_filtered_by_refinement_id.return_value = (
            mock_categories
        )

        mock_xsd_element_1 = MagicMock()
        mock_xsd_element_2 = MagicMock()
        mock_xsd_tree.fromstring.return_value = [
            [mock_xsd_element_1],
            [],
            [mock_xsd_element_2],
        ]

        expected_result = {
            f"{RefinementForm.prefix}-{self.mock_kwargs['field_id']}": [
                mock_category_specified_id,
                mock_category_unspecified_id,
            ]
        }
        result = self.mock_module._reload_data(**self.mock_kwargs)

        self.assertEqual(result, expected_result)


class TestFancyTreeModuleRenderModule(TestCase):
    """Unit tests for the `_render_module` method of `FancyTreeModule` class."""

    def setUp(self):
        """setUp"""
        self.mock_module = module_fancy_tree_views.FancyTreeModule()
        self.mock_kwargs = {"request": MagicMock()}

    def test_retrieve_xml_xpath_from_request(self):
        """test_retrieve_xml_xpath_from_request"""
        with self.assertRaises(ModuleError):
            self.mock_module._render_module(**self.mock_kwargs)

        self.mock_kwargs["request"].GET.get.assert_called_with(
            "xml_xpath", None
        )

    def test_xml_xpath_none_raises_module_error(self):
        """test_xml_xpath_none_raises_module_error"""
        self.mock_kwargs["request"].GET.get.return_value = None

        with self.assertRaises(ModuleError):
            self.mock_module._render_module(**self.mock_kwargs)

    @patch.object(module_fancy_tree_views, "re")
    @patch.object(module_fancy_tree_views, "template_registry_api")
    def test_get_current_registry_template_called(
        self, mock_template_registry_api, mock_re
    ):
        """test_get_current_registry_template_called"""
        with self.assertRaises(ModuleError):
            self.mock_module._render_module(**self.mock_kwargs)

        mock_template_registry_api.get_current_registry_template.assert_called_with(
            request=self.mock_kwargs["request"]
        )

    @patch.object(module_fancy_tree_views, "re")
    @patch.object(module_fancy_tree_views, "template_registry_api")
    def test_get_current_registry_template_exception_raises_module_error(
        self, mock_template_registry_api, mock_re
    ):
        """test_get_current_registry_template_exception_raises_module_error"""
        mock_template_registry_api.get_current_registry_template.side_effect = Exception(
            "mock_get_current_registry_template_exception"
        )

        with self.assertRaises(ModuleError):
            self.mock_module._render_module(**self.mock_kwargs)

    @patch.object(module_fancy_tree_views, "re")
    @patch.object(module_fancy_tree_views, "template_registry_api")
    @patch.object(module_fancy_tree_views, "refinement_api")
    def test_get_all_filtered_by_template_hash_called(
        self, mock_refinement_api, mock_template_registry_api, mock_re
    ):
        """test_get_all_filtered_by_template_hash_called"""
        mock_template = MagicMock()
        mock_template_registry_api.get_current_registry_template.return_value = (
            mock_template
        )

        with self.assertRaises(ModuleError):
            self.mock_module._render_module(**self.mock_kwargs)

        mock_refinement_api.get_all_filtered_by_template_hash.assert_called_with(
            mock_template.hash
        )

    @patch.object(module_fancy_tree_views, "re")
    @patch.object(module_fancy_tree_views, "template_registry_api")
    @patch.object(module_fancy_tree_views, "refinement_api")
    def test_get_all_filtered_by_template_hash_exception_raises_module_error(
        self, mock_refinement_api, mock_template_registry_api, mock_re
    ):
        """test_get_all_filtered_by_template_hash_exception_raises_module_error"""
        mock_refinement_api.get_all_filtered_by_template_hash.side_effect = (
            Exception("get_all_filtered_by_template_hash")
        )

        with self.assertRaises(ModuleError):
            self.mock_module._render_module(**self.mock_kwargs)

    @patch.object(module_fancy_tree_views, "re")
    @patch.object(module_fancy_tree_views, "template_registry_api")
    @patch.object(module_fancy_tree_views, "refinement_api")
    def test_refinements_get_called(
        self, mock_refinement_api, mock_template_registry_api, mock_re
    ):
        """test_refinements_get_called"""
        xml_element_namespace = "mock_namespace"
        xml_element = "mock_xml_xpath"
        self.mock_kwargs["request"].GET.get.return_value = (
            f"{xml_element_namespace}:{xml_element}"
        )

        mock_refinement_query_set = MagicMock()
        mock_refinement_api.get_all_filtered_by_template_hash.return_value = (
            mock_refinement_query_set
        )

        with self.assertRaises(ModuleError):
            self.mock_module._render_module(**self.mock_kwargs)

        mock_refinement_query_set.get.assert_called_with(xsd_name=xml_element)

    @patch.object(module_fancy_tree_views, "re")
    @patch.object(module_fancy_tree_views, "template_registry_api")
    @patch.object(module_fancy_tree_views, "refinement_api")
    def test_refinements_get_exception_raises_module_error(
        self, mock_refinement_api, mock_template_registry_api, mock_re
    ):
        """test_refinements_get_exception_raises_module_error"""
        """test_refinements_get_called"""
        xml_element = "mock_xml_xpath"
        self.mock_kwargs["request"].GET.get.return_value = xml_element

        mock_refinement_query_set = MagicMock()
        mock_refinement_api.get_all_filtered_by_template_hash.return_value = (
            mock_refinement_query_set
        )

        mock_refinement_query_set.get.side_effect = Exception(
            "mock_refinement_query_set_get_exception"
        )

        with self.assertRaises(ModuleError):
            self.mock_module._render_module(**self.mock_kwargs)

    @patch.object(module_fancy_tree_views, "re")
    @patch.object(module_fancy_tree_views, "template_registry_api")
    @patch.object(module_fancy_tree_views, "refinement_api")
    @patch.object(module_fancy_tree_views, "AbstractModule")
    @patch.object(module_fancy_tree_views, "RefinementForm")
    @patch.object(module_fancy_tree_views.FancyTreeModule, "_reload_data")
    def test_abstract_module_render_template_called(
        self,
        mock_reload_data,
        mock_refinement_form,
        mock_abstract_module,
        mock_refinement_api,
        mock_template_registry_api,
        mock_re,
    ):
        """test_abstract_module_render_template_called"""
        mock_field_id = MagicMock()
        mock_re.sub.return_value = mock_field_id

        mock_refinement_query_set = MagicMock()
        mock_refinement_api.get_all_filtered_by_template_hash.return_value = (
            mock_refinement_query_set
        )

        mock_refinement = MagicMock()
        mock_refinement_query_set.get.return_value = mock_refinement

        mock_data = MagicMock()
        mock_reload_data.return_value = mock_data

        mock_refinement_form_object = MagicMock()
        mock_refinement_form.return_value = mock_refinement_form_object

        self.mock_module._render_module(**self.mock_kwargs)

        mock_reload_data.assert_called_with(mock_field_id, mock_refinement)

        mock_refinement_form.assert_called_with(
            refinement=mock_refinement, field_id=mock_field_id, data=mock_data
        )

        mock_abstract_module.render_template.assert_called_with(
            "core_module_fancy_tree_registry_app/fancy_tree.html",
            {"form": mock_refinement_form_object},
        )

    @patch.object(module_fancy_tree_views, "re")
    @patch.object(module_fancy_tree_views, "template_registry_api")
    @patch.object(module_fancy_tree_views, "refinement_api")
    @patch.object(module_fancy_tree_views, "AbstractModule")
    @patch.object(module_fancy_tree_views, "RefinementForm")
    @patch.object(module_fancy_tree_views.FancyTreeModule, "_reload_data")
    def test_abstract_module_render_template_exception_raises_module_error(
        self,
        mock_reload_data,
        mock_refinement_form,
        mock_abstract_module,
        mock_refinement_api,
        mock_template_registry_api,
        mock_re,
    ):
        """test_abstract_module_render_template_exception_raises_module_error"""
        mock_field_id = MagicMock()
        mock_re.sub.return_value = mock_field_id

        mock_refinement_query_set = MagicMock()
        mock_refinement_api.get_all_filtered_by_template_hash.return_value = (
            mock_refinement_query_set
        )

        mock_refinement = MagicMock()
        mock_refinement_query_set.get.return_value = mock_refinement

        mock_data = MagicMock()
        mock_reload_data.return_value = mock_data

        mock_refinement_form_object = MagicMock()
        mock_refinement_form.return_value = mock_refinement_form_object

        mock_abstract_module.render_template.side_effect = Exception(
            "mock_abstract_module_render_module_exception"
        )

        with self.assertRaises(ModuleError):
            self.mock_module._render_module(**self.mock_kwargs)

    @patch.object(module_fancy_tree_views, "re")
    @patch.object(module_fancy_tree_views, "template_registry_api")
    @patch.object(module_fancy_tree_views, "refinement_api")
    @patch.object(module_fancy_tree_views, "AbstractModule")
    @patch.object(module_fancy_tree_views, "RefinementForm")
    @patch.object(module_fancy_tree_views.FancyTreeModule, "_reload_data")
    def test_returns_abstract_module_render_template(
        self,
        mock_reload_data,
        mock_refinement_form,
        mock_abstract_module,
        mock_refinement_api,
        mock_template_registry_api,
        mock_re,
    ):
        """test_returns_abstract_module_render_template"""
        mock_module_template_rendering = MagicMock()
        mock_abstract_module.render_template.return_value = (
            mock_module_template_rendering
        )

        results = self.mock_module._render_module(**self.mock_kwargs)

        self.assertEqual(results, mock_module_template_rendering)


class TestFancyTreeModuleRetrieveDataGet(TestCase):
    """Unit tests for the `_retrieve_data` method of `FancyTreeModule` class. These
    tests only cover GET requests."""

    def setUp(self):
        """setUp"""
        self.mock_request = MagicMock
        self.mock_request.method = "GET"

        self.mock_kwargs = {"request": self.mock_request}
        self.mock_module = module_fancy_tree_views.FancyTreeModule()

    def test_no_data_in_request_returns_empty_string(self):
        """test_no_data_in_request_returns_empty_string"""
        self.mock_request.GET = {}

        self.assertEqual(
            self.mock_module._retrieve_data(**self.mock_kwargs), ""
        )

    def test_data_in_request_is_returned(self):
        """test_data_in_request_is_returned"""
        mock_data = "mock_data"
        self.mock_request.GET = {"data": mock_data}

        self.assertEqual(
            self.mock_module._retrieve_data(**self.mock_kwargs), mock_data
        )


class TestFancyTreeModuleRetrieveDataPost(TestCase):
    """Unit tests for the `_retrieve_data` method of `FancyTreeModule` class. These
    tests only cover POST requests."""

    def setUp(self):
        """setUp"""
        self.mock_request = MagicMock()
        self.mock_request.method = "POST"

        self.mock_kwargs = {"request": self.mock_request}
        self.mock_module = module_fancy_tree_views.FancyTreeModule()

    @patch.object(module_fancy_tree_views, "RefinementForm")
    def test_refinement_form_called(self, mock_refinement_form):
        """test_refinement_form_called"""
        self.mock_module._retrieve_data(**self.mock_kwargs)

        mock_refinement_form.assert_called_with(
            self.mock_kwargs["request"].POST
        )

    @patch.object(module_fancy_tree_views, "RefinementForm")
    def test_form_is_valid_called(self, mock_refinement_form):
        """test_form_is_valid_called"""
        mock_form = MagicMock()
        mock_refinement_form.return_value = mock_form

        self.mock_module._retrieve_data(**self.mock_kwargs)

        mock_form.is_valid.assert_called()

    @patch.object(module_fancy_tree_views, "RefinementForm")
    def test_form_not_valid_raises_module_error(self, mock_refinement_form):
        """test_form_not_valid_raises_module_error"""
        mock_form = MagicMock()
        mock_refinement_form.return_value = mock_form

        mock_form.is_valid.return_value = False

        with self.assertRaises(ModuleError):
            self.mock_module._retrieve_data(**self.mock_kwargs)

    @patch.object(module_fancy_tree_views, "RefinementForm")
    def test_no_data_in_request_returns_empty_string(
        self, mock_refinement_form
    ):
        """test_no_data_in_request_returns_empty_string"""
        mock_form = MagicMock()
        mock_refinement_form.return_value = mock_form
        mock_form.is_valid.return_value = True

        self.assertEqual(
            self.mock_module._retrieve_data(**self.mock_kwargs), ""
        )

    @patch.object(module_fancy_tree_views, "RefinementForm")
    def test_request_getlist_called(self, mock_refinement_form):
        """test_request_getlist_called"""

        class MockPostData(Mock):
            def __contains__(self, item):
                return True

        self.mock_kwargs["request"].POST = MockPostData()
        self.mock_kwargs["request"].POST.getlist.return_value = []

        mock_form = MagicMock()
        mock_refinement_form.return_value = mock_form
        mock_form.is_valid.return_value = True

        self.mock_module._retrieve_data(**self.mock_kwargs)

        self.mock_kwargs["request"].POST.getlist.assert_called_with("data[]")

    @patch.object(module_fancy_tree_views, "RefinementForm")
    def test_request_getlist_exception_raises_module_error(
        self, mock_refinement_form
    ):
        """test_request_getlist_exception_raises_module_error"""

        class MockPostData(Mock):
            def __contains__(self, item):
                return True

        self.mock_kwargs["request"].POST = MockPostData()
        self.mock_kwargs["request"].POST.getlist.side_effect = Exception(
            "mock_post_get_list_exception"
        )

        mock_form = MagicMock()
        mock_refinement_form.return_value = mock_form
        mock_form.is_valid.return_value = True

        with self.assertRaises(ModuleError):
            self.mock_module._retrieve_data(**self.mock_kwargs)

    @patch.object(module_fancy_tree_views, "RefinementForm")
    @patch.object(module_fancy_tree_views, "category_api")
    def test_category_api_get_by_id_called(
        self, mock_category_api, mock_refinement_form
    ):
        """test_category_api_get_by_id_called"""

        class MockPostData(Mock):
            def __contains__(self, item):
                return True

        self.mock_kwargs["request"].POST = MockPostData()
        mock_category_id = MagicMock()
        self.mock_kwargs["request"].POST.getlist.return_value = [
            mock_category_id
        ]

        mock_form = MagicMock()
        mock_refinement_form.return_value = mock_form
        mock_form.is_valid.return_value = True

        self.mock_module._retrieve_data(**self.mock_kwargs)

        mock_category_api.get_by_id.assert_called_with(mock_category_id)

    @patch.object(module_fancy_tree_views, "RefinementForm")
    @patch.object(module_fancy_tree_views, "category_api")
    def test_category_api_get_by_id_exception_raises_module_error(
        self, mock_category_api, mock_refinement_form
    ):
        """test_category_api_get_by_id_exception_raises_module_error"""

        class MockPostData(Mock):
            def __contains__(self, item):
                return True

        self.mock_kwargs["request"].POST = MockPostData()
        mock_category_id = MagicMock()
        self.mock_kwargs["request"].POST.getlist.return_value = [
            mock_category_id
        ]

        mock_form = MagicMock()
        mock_refinement_form.return_value = mock_form
        mock_form.is_valid.return_value = True

        mock_category_api.get_by_id.side_effect = Exception(
            "mock_category_get_by_id_exception"
        )

        with self.assertRaises(ModuleError):
            self.mock_module._retrieve_data(**self.mock_kwargs)

    @patch.object(module_fancy_tree_views, "RefinementForm")
    @patch.object(module_fancy_tree_views, "category_api")
    def test_succesful_execution_returns_data(
        self, mock_category_api, mock_refinement_form
    ):
        """test_succesful_execution_returns_data"""
        self.maxDiff = None

        class MockPostData(Mock):
            def __contains__(self, item):
                return True

        self.mock_kwargs["request"].POST = MockPostData()
        mock_category_id = MagicMock()
        self.mock_kwargs["request"].POST.getlist.return_value = [
            mock_category_id
        ]

        mock_form = MagicMock()
        mock_refinement_form.return_value = mock_form
        mock_form.is_valid.return_value = True

        mock_category = MagicMock()
        category_path_1 = MagicMock()
        category_path_2 = MagicMock()
        mock_category.path.split.return_value = [
            category_path_1,
            category_path_2,
        ]
        mock_category_api.get_by_id.return_value = mock_category

        expected_results = f"<{category_path_1}><{category_path_2}>{mock_category.value.__getitem__()}</{category_path_2}></{category_path_1}>"

        self.assertEqual(
            self.mock_module._retrieve_data(**self.mock_kwargs),
            expected_results,
        )


class TestFancyTreeModuleRenderData(TestCase):
    """Unit tests for the `_render_data` method of `FancyTreeModule` class."""

    @patch.object(module_fancy_tree_views, "AbstractModule")
    def test_returns_empty_string(self, mock_abstract_module):
        """test_returns_empty_string"""
        mock_module = module_fancy_tree_views.FancyTreeModule()
        self.assertEqual(mock_module._render_data(MagicMock()), "")
