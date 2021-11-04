import collections.abc
import pytest
import src.graph


def _bidirectional_edge(
        v1: src.graph.Vertex,
        v2: src.graph.Vertex,
        weight: src.graph.GraphDistance) -> list[src.graph.Edge]:
    return [src.graph.Edge(v1, v2, weight), src.graph.Edge(v2, v1, weight)]


class _NotEdge(object):
    """This class is not an edge and cannot be compared against an edge."""


def test_path_comparison() -> None:
    e1 = src.graph.Edge("1", "2", 1)
    e2 = src.graph.Edge("3", "4", 2)
    e3 = src.graph.Edge("5", "6", 1)

    assert e1 == e1
    assert e1 < e2
    assert e2 > e1
    assert e1 <= e2
    assert e2 >= e1
    assert e1 != e2
    assert e1 == e3

    not_edge = _NotEdge()
    assert e1 != not_edge
    with pytest.raises(TypeError, match="'<=' not supported"):
        assert not e1 <= not_edge


def _assert_expand(
        it: collections.abc.Generator[
            collections.abc.Generator[src.graph.Vertex, None, None],
            None,
            None],
        expected_paths: list[list[src.graph.Vertex]]) -> None:
    s = set([tuple(p) for p in expected_paths])
    for g in it:
        t = tuple(g)
        assert t in s
        s.remove(t)
    assert not s


def test_paths() -> None:
    # construct a graph:
    # 1 (10) -> 2 (20) -> 3
    # 1 (30) -> 3
    # 1 (20) -> 4 (10) -> 3
    # 1 (20) -> 5 (20) -> 3
    # 3 (10) -> 6
    # all bidirectional
    graph = src.graph.Graph(
        ["1", "2", "3", "4", "5", "6"],
        _bidirectional_edge("1", "2", 10) +
        _bidirectional_edge("2", "3", 20) +
        _bidirectional_edge("1", "3", 30) +
        _bidirectional_edge("1", "4", 20) +
        _bidirectional_edge("4", "3", 10) +
        _bidirectional_edge("1", "5", 20) +
        _bidirectional_edge("5", "3", 20) +
        _bidirectional_edge("3", "6", 10)
    )

    shortest_paths = graph.calculate_shortest_paths("1")
    assert shortest_paths["1"].get_distance() == 0
    assert shortest_paths["2"].get_distance() == 10
    assert shortest_paths["3"].get_distance() == 30
    assert shortest_paths["4"].get_distance() == 20
    assert shortest_paths["5"].get_distance() == 20
    assert shortest_paths["6"].get_distance() == 40
    assert len(shortest_paths) == 6

    # test path expansion.
    _assert_expand(shortest_paths["1"].expand(), [["1"]])
    _assert_expand(shortest_paths["2"].expand(), [["2"]])
    _assert_expand(shortest_paths["3"].expand(), [
        ["3", ],
        ["2", "3", ],
        ["4", "3", ],
    ])
    _assert_expand(shortest_paths["4"].expand(), [["4"]])
    _assert_expand(shortest_paths["5"].expand(), [["5"]])
    _assert_expand(shortest_paths["6"].expand(), [
        ["3", "6", ],
        ["2", "3", "6", ],
        ["4", "3", "6", ],
    ])
