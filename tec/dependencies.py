"""Tools to analyze dependencies between python objects

Packages to extract module dependencies are easy to find. Example:
* https://github.com/thebjorn/pydeps
* https://pypi.org/project/modulegraph/
* https://pypi.org/project/findimports/

But to get this dependency analysis at a lower level is harder. There's:
* http://pycallgraph.slowchop.com/en/master/guide/index.html
(but need to run the code -- no static analysis that I can see)
* (There was snakefood, but no 3.x support !!!!)

I searched around AST and found some useful things there.
Often, around this AST code there are "fragility warnings" that say something along the
lines of "will not work in complex situations".

My take on that is:
* if IDEs can refactor more or less correctly, then there's a tool to do it sufficiently
* sufficiently is enough for most applications (it's for the human, not the machine)

Gathered here are some tools to get the problem's solution off the ground.

Note: The module requires `ast_scope` and `graphviz` to be installed.
"""


def get_source_string(obj: object) -> str:
    import inspect

    if isinstance(obj, str):
        return obj
    return inspect.getsource(obj)


def source_string_to_ast_scope_graph(source_string: str):
    import ast
    import ast_scope

    tree = ast.parse(source_string)
    scope_info = ast_scope.annotate(tree)
    return scope_info.static_dependency_graph


def to_ast_scope_graph(obj: object):
    import ast_scope.graph
    if isinstance(obj, ast_scope.graph.DiGraph):
        return obj
    return source_string_to_ast_scope_graph(get_source_string(obj))


def ast_scope_graph_to_dot(ast_scope_graph):
    return edges_to_dot_graph_edges(ast_scope_graph.edges())


def edges_to_dot_graph_edges(edges):
    for from_, to_ in edges:
        yield f'{from_} -> {to_}'


def dependency_graph_for(obj: object, prefix='rankdir=LR', suffix='', **digraph_kwargs):
    """Get graphviz Digraph object of the dependencies of a python object"""
    graph = to_ast_scope_graph(obj)
    from graphviz import Digraph

    return Digraph(
        **digraph_kwargs,
        body=[*prefix.split('\n'), *ast_scope_graph_to_dot(graph), *suffix.split('\n')],
    )
