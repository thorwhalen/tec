# tec.dependencies

Tools to analyze dependencies between python objects.

You may also wish to look at the unbox package for a more complete solution.

Packages to extract module dependencies are easy to find. Example:

* [https://github.com/thebjorn/pydeps](https://github.com/thebjorn/pydeps)
* [https://pypi.org/project/modulegraph/](https://pypi.org/project/modulegraph/)
* [https://pypi.org/project/findimports/](https://pypi.org/project/findimports/)

But to get this dependency analysis at a lower level is harder. There’s:

* [http://pycallgraph.slowchop.com/en/master/guide/index.html](http://pycallgraph.slowchop.com/en/master/guide/index.html)
  (but need to run the code – no static analysis that I can see)
* (There was snakefood, but no 3.x support !!!!)

I searched around AST and found some useful things there.
Often, around this AST code there are “fragility warnings” that say something along the
lines of “will not work in complex situations”.

My take on that is:

* if IDEs can refactor more or less correctly, then there’s a tool to do it sufficiently
* sufficiently is enough for most applications (it’s for the human, not the machine)

Gathered here are some tools to get the problem’s solution off the ground.

#### NOTE
The module requires `ast_scope` and `graphviz` to be installed.

### Functions

| `ast_scope_graph_to_dot`(ast_scope_graph)                                                    |                                                                    |
|----------------------------------------------------------------------------------------------|--------------------------------------------------------------------|
| [`dependency_graph_for`](#tec.dependencies.dependency_graph_for)(obj[, prefix, suffix]) | Get graphviz Digraph object of the dependencies of a python object |
| `edges_to_dot_graph_edges`(edges)                                                            |                                                                    |
| `get_source_string`(obj)                                                                     |                                                                    |
| `source_string_to_ast_scope_graph`(source_string)                                            |                                                                    |
| `to_ast_scope_graph`(obj)                                                                    |                                                                    |

### tec.dependencies.dependency_graph_for(obj, prefix='rankdir="LR"', suffix='', \*\*digraph_kwargs)

Get graphviz Digraph object of the dependencies of a python object
