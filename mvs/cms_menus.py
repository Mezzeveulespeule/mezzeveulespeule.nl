from menus.base import Modifier
from menus.menu_pool import menu_pool

from cms.models import Page


class ColorModifier(Modifier):
    """ """

    def modify(self, request, nodes, namespace, root_id, post_cut, breadcrumb):
        # only do something when the menu has already been cut
        if post_cut:
            # only consider nodes that refer to cms pages
            # and put them in a dict for efficient access
            page_nodes = {n.id: n for n in nodes if n.attr["is_page"]}
            # retrieve the attributes of interest from the relevant pages
            pages = (
                Page.objects.filter(id__in=page_nodes.keys())
                .select_related("colorextension")
                .values("id", "colorextension__color")
            )
            # loop over all relevant pages
            for page in pages:
                node = page_nodes[page["id"]]
                node.color = page["colorextension__color"]

        return nodes


menu_pool.register_modifier(ColorModifier)
