"""Define and operate on graph objects."""
import abc
import collections
import collections.abc
import functools
import json
import logging
import queue
import typing

# each module/file should provide a global-level logger using this statement
logger = logging.getLogger(__name__)

"""A graph vertex is any hashable object.

2 objects are the same vertex iff their hash codes are equals and
__eq__/__cmp__ indicate they are the same.
Vertices must be hashable as they will be used in sets and as keys in dicts."""
Vertex = collections.abc.Hashable

# graph distances can be only ints for our purposes.
GraphDistance = int


# ordering is done by distance, allowing paths to be added to a priority queue.
# mypy current complains that total_ordering must be used on a concrete type.
# https://github.com/python/mypy/issues/8539 agrees this is a bug
@functools.total_ordering  # type: ignore
class _Path(abc.ABC):
    """A generic path between 2 vertices."""

    @abc.abstractmethod
    def get_source_vertex(self) -> Vertex:
        """Return the source vertex."""

    @abc.abstractmethod
    def get_destination_vertex(self) -> Vertex:
        """Return the destination vertex."""

    @abc.abstractmethod
    def get_distance(self) -> GraphDistance:
        """Return the distance between the vertices."""

    @abc.abstractmethod
    def expand(self) -> collections.abc.Generator[
            collections.abc.Generator[Vertex, None, None], None, None]:
        """Return the distinct represented paths.

        Actually returns a generator where each item is a generator of vertices
        representing the path.  This is done to avoid temporary object
        construction and allows the _caller_ to decide if the paths should be
        stored into collections.

        The initial vertex is excluded.
        """

    def _is_valid_operand(self, other: typing.Any) -> bool:
        return isinstance(other, _Path)

    def __eq__(self, other: typing.Any) -> bool:
        """Define equals according to path distance."""
        if not self._is_valid_operand(other):
            return NotImplemented
        # mypy isn't doing well with NotImplemented's type
        return self.get_distance() == other.get_distance()  # type: ignore

    def __lt__(self, other: typing.Any) -> bool:
        """Define < according to path distance."""
        if not self._is_valid_operand(other):
            return NotImplemented
        # mypy isn't doing well with NotImplemented's type
        return self.get_distance() < other.get_distance()  # type: ignore


class _PathRef(object):
    """Holds a ref to a path so that it may be reassigned."""

    _path: _Path

    def __init__(self, path: _Path) -> None:
        """Initialize with value."""
        self._path = path

    def get(self) -> _Path:
        """Get the current value."""
        return self._path

    def set(self, path: _Path) -> None:
        """Set the ref value."""
        self._path = path

    def copy(self) -> '_PathRef':
        """Copy (shallow) the PathRef."""
        return _PathRef(self.get())

    def json_default(self) -> typing.Any:
        """Represent as json."""
        return {"path_ref": self._path}

    def __str__(self) -> str:
        """Represent as a string."""
        # not currently called as we always rather get the json implementation.
        # if we do end up needing then this will return that same json
        raise NotImplementedError


class Edge(_Path):
    """An Edge in a Graph.  This is a directed weighted edge.

    Vertices must be constructed first and passed as the arguments of edges.
    """

    _source_vertex: Vertex
    _destination_vertex: Vertex
    _distance: GraphDistance

    def __init__(
            self,
            source_vertex: Vertex,
            destination_vertex: Vertex,
            distance: GraphDistance) -> None:
        """Create the edge.

        Accepts the source and destination vertex as well as a weight.
        """
        self._source_vertex = source_vertex
        self._destination_vertex = destination_vertex
        self._distance = distance

    def get_source_vertex(self) -> Vertex:
        """Return the source vertex."""
        return self._source_vertex

    def get_destination_vertex(self) -> Vertex:
        """Return the destination vertex."""
        return self._destination_vertex

    def get_distance(self) -> GraphDistance:
        """Return the distance between the vertices."""
        return self._distance

    def expand(self) -> collections.abc.Generator[
            collections.abc.Generator[Vertex, None, None], None, None]:
        """Return the distinct represented paths.

        Excludes the first vertex.
        """

        def edge_gen() -> collections.abc.Generator[Vertex, None, None]:
            yield self.get_destination_vertex()
            return

        yield edge_gen()
        return

    def json_default(self) -> typing.Any:
        """Represent as json."""
        return {
            "type": "edge",
            "source_vertex": self._source_vertex,
            "destination_vertex": self._destination_vertex,
            "distance": self._distance,
        }

    def __str__(self) -> str:
        """Represent as a string."""
        return json.dumps(self)


class _PathSequence(_Path):
    """A sequence of Path and additional Edge forming a new Path."""

    _base_path_ref: _PathRef
    _added_edge: Edge
    # store this so that a long string of sequences doesn't have linear
    # get_distance time
    _distance: GraphDistance

    def __init__(
            self,
            base_path_ref: _PathRef,
            added_edge: Edge) -> None:
        """Create the sequence."""
        assert (base_path_ref.get().get_destination_vertex() ==
                added_edge.get_source_vertex())
        self._base_path_ref = base_path_ref
        self._added_edge = added_edge
        self._distance = (base_path_ref.get().get_distance() +
                          added_edge.get_distance())

    def get_source_vertex(self) -> Vertex:
        """Return the source vertex."""
        return self._base_path_ref.get().get_source_vertex()

    def get_destination_vertex(self) -> Vertex:
        """Return the destination vertex."""
        return self._added_edge.get_destination_vertex()

    def get_distance(self) -> GraphDistance:
        """Return the distance between the vertices."""
        return self._distance

    def expand(self) -> collections.abc.Generator[
            collections.abc.Generator[Vertex, None, None], None, None]:
        """Return the distinct represented paths.

        Excludes the first vertex.
        """
        def path_yielder(g: collections.abc.Generator[Vertex, None, None]) -> (
                collections.abc.Generator[Vertex, None, None]):
            yield from g
            yield self._added_edge.get_destination_vertex()
            return

        for g in self._base_path_ref.get().expand():
            yield path_yielder(g)
        return

    def json_default(self) -> typing.Any:
        """Represent as json."""
        return {
            "type": "PathSequence",
            "base_path_ref": self._base_path_ref,
            "added_edge": self._added_edge,
            "distance": self._distance,
        }

    def __str__(self) -> str:
        """Represent as a string."""
        return json.dumps(self)


class _PathAlternatives(_Path):
    """Two paths of equal distance between the same 2 vertices."""

    _path1: _PathRef
    _path2: _PathRef

    def __init__(
            self,
            path1: _PathRef,
            path2: _PathRef):
        """Create a Path representing 2 paths to the same vertex."""
        assert (path1.get().get_source_vertex() ==
                path2.get().get_source_vertex())
        assert (path1.get().get_destination_vertex() ==
                path2.get().get_destination_vertex())
        assert (path1.get().get_distance() ==
                path2.get().get_distance())
        self._path1 = path1
        self._path2 = path2

    def get_source_vertex(self) -> Vertex:
        """Return the source vertex."""
        return self._path1.get().get_source_vertex()

    def get_destination_vertex(self) -> Vertex:
        """Return the destination vertex."""
        return self._path1.get().get_destination_vertex()

    def get_distance(self) -> GraphDistance:
        """Return the distance between the vertices."""
        return self._path1.get().get_distance()

    def expand(self) -> collections.abc.Generator[
            collections.abc.Generator[Vertex, None, None], None, None]:
        """Return the distinct represented paths.

        Excludes the first vertex.
        """
        yield from self._path1.get().expand()
        yield from self._path2.get().expand()
        return

    def json_default(self) -> typing.Any:
        """Represent as json."""
        return {
            "type": "PathAlternatives",
            "path1": self._path1,
            "path2": self._path2,
        }

    def __str__(self) -> str:
        """Represent as a string."""
        return json.dumps(self)


class Graph(object):
    """Represent a graph."""

    _vertices: list[Vertex]
    _edges: list[Edge]
    _vertices_outgoing_edges: dict[Vertex, list[Edge]]
    _vertices_set: set[Vertex]

    def __init__(self, vertices: list[Vertex], edges: list[Edge]) -> None:
        """Create a graph from lists of vertices and edges."""
        self._vertices = vertices
        self._edges = edges

        # assert no duplicate vertex label
        self._vertices_set = set()
        for v in self._vertices:
            assert v not in self._vertices_set, "duplicate label: {}".format(v)
            self._vertices_set.add(v)

        # assert no duplicate edge
        edge_tuples = set()
        for e in self._edges:
            tup = (
                e.get_source_vertex(),
                e.get_destination_vertex(),)
            assert tup not in edge_tuples, "duplicate edge: {}".format(tup)
            edge_tuples.add(tup)

        # assemble the dict of vertex labels to edges
        self._vertices_outgoing_edges = collections.defaultdict(list)
        for e in self._edges:
            self._vertices_outgoing_edges[e.get_source_vertex()].append(e)
        logger.debug("calculated outgoing edges of all vertices: {}".format(
            self._vertices_outgoing_edges))

    def calculate_shortest_paths(self, start: Vertex) -> dict[Vertex, _Path]:
        """Calculate shortest paths from vertex "start" to all others."""
        logger.info("calculating shortest paths from vertex: {}".format(start))
        assert start in self._vertices, (
            "unexpected vertex: {}".format(start))

        shortest_paths: dict[Vertex, _PathRef] = {}
        next_path_by_distance: queue.PriorityQueue[_Path] = (
            queue.PriorityQueue())

        # add all vertices connected to the start vertex to "next" queue
        for e in self._vertices_outgoing_edges.get(start, []):
            logger.debug("adding initial edge: {}".format(e))
            next_path_by_distance.put(e)

        # implicit shortest path to starting node is 0
        shortest_paths[start] = _PathRef(Edge(start, start, 0))

        # pop the next path.  If we've never seen the destination vertex it
        # is a shortest path so add a result and add its edges to next
        # vertices.  If we have seen it check to see if this is an alternate
        # shortest path to the vertex, but then add no next vertex.  Do this
        # until there is no more work (no more items in queue).
        while not next_path_by_distance.empty():
            next_path = next_path_by_distance.get_nowait()
            vertex = next_path.get_destination_vertex()
            logger.debug("popped next path: {}.  shortest paths: {}".format(
                next_path, shortest_paths))
            if vertex in shortest_paths:
                logger.debug("vertex in shortest paths")
                existing_path_ref = shortest_paths[vertex]
                existing_path = existing_path_ref.get()
                assert existing_path.get_distance() <= next_path.get_distance()
                if existing_path.get_distance() == next_path.get_distance():
                    logger.debug("new alternative path")
                    # we have an alternate shortest path to this vertex
                    new_alternatives = _PathAlternatives(
                        existing_path_ref.copy(), _PathRef(next_path))
                    logger.debug(
                        ("replacing path with alternatives.  "
                         "Original path: {}.  New alternatives: {}").format(
                            existing_path,
                            next_path
                        ))
                    existing_path_ref.set(new_alternatives)
                else:
                    logger.debug("this is a longer path than exists")
                # do not add any new paths to search
            else:
                # a new shortest path!
                logger.debug("vertex NOT in shortest paths")
                path_ref = _PathRef(next_path)
                shortest_paths[vertex] = path_ref
                # add all outgoing edges to next paths.
                for e in self._vertices_outgoing_edges[vertex]:
                    new_path = _PathSequence(
                        path_ref,
                        e)
                    logger.debug("adding additional path: {}".format(new_path))
                    next_path_by_distance.put_nowait(new_path)

        # unpack the path refs to return
        ret: dict[Vertex, _Path] = {}
        for (k, v,) in shortest_paths.items():
            ret[k] = v.get()
        return ret
