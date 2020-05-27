""" Url router for the fancy tree module
"""

from django.urls import re_path

from core_module_fancy_tree_registry_app.views.views import FancyTreeModule

urlpatterns = [
    re_path(
        r"module-fancy-tree-registry",
        FancyTreeModule.as_view(),
        name="core_module_fancy_tree_registry",
    ),
]
