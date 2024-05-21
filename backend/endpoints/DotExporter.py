import graphviz as gv  # type: ignore

from .TreeNode import TreeNode


class DotExporter:
    def __init__(self) -> None:
        pass

    @staticmethod
    def export(tree: TreeNode, output_path: str) -> None:
        g = gv.Digraph(format="png")
        DotExporter._export(g, tree)
        g.render(output_path, view=False)

    @staticmethod
    def _export(g: gv.Digraph, tree: TreeNode) -> None:
        g.node(str(id(tree)), tree.value)
        for child in tree.children:
            DotExporter._export(g, child)
            g.edge(str(id(tree)), str(id(child)))
