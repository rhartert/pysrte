from ctypes import c_char, c_double, c_int32, c_long, c_ulong
from dataclasses import dataclass
from enum import IntEnum

from .bindings import C_Config, C_Demand, C_Edge, C_Move, c_lib


@dataclass
class Edge:
    src: int
    dest: int
    capacity: int
    weight: int


class MoveType(IntEnum):
    UNKNOWN = 0
    CLEAR = 1
    REMOVE = 2
    UPDATE = 3
    INSERT = 4


@dataclass
class Move:
    move_type: MoveType
    position: int
    node: int
    demand: int


@dataclass
class Demand:
    src: int
    dest: int
    traffic: int


@dataclass
class Config:
    alpha: float
    beta: float
    max_nodes: int


class Instance:
    def __init__(self):
        self._id = c_lib.newInstance()

    def __del__(self):
        c_lib.freeInstance(self._id)

    def add_edge(self, edge: Edge):
        c_edge = C_Edge()
        c_edge.src = c_int32(edge.src)
        c_edge.dest = c_int32(edge.dest)
        c_edge.capacity = c_long(edge.capacity)
        c_edge.weight = c_int32(edge.weight)
        c_lib.addEdge(self._id, c_edge)

    def add_demand(self, demand: Demand):
        c_demand = C_Demand()
        c_demand.src = c_int32(demand.src)
        c_demand.dest = c_int32(demand.dest)
        c_demand.traffic = c_long(demand.traffic)
        c_lib.addDemand(self._id, c_demand)

    def print(self):
        c_lib.printInstance(self._id)


class LgsSolver:
    def __init__(self, inst: Instance, cfg: Config):
        c_cfg = C_Config()
        c_cfg.alpha = c_double(cfg.alpha)
        c_cfg.beta = c_double(cfg.beta)
        c_cfg.maxNodes = c_int32(cfg.max_nodes)
        self._id = c_lib.newSolver(c_ulong(inst._id), c_cfg)

    def __del__(self):
        c_lib.freeSolver(self._id)

    def apply_move(self, move: Move) -> bool:
        c_move = C_Move()
        c_move.moveType = c_char(move.move_type)
        c_move.position = c_int32(move.position)
        c_move.node = c_int32(move.node)
        c_move.demand = c_int32(move.demand)
        b = c_lib.applyMove(c_ulong(self._id), c_move)
        return b == 1

    def max_utilization(self) -> float:
        return float(c_lib.maxUtilization(self._id))

    def max_utilized_edge(self) -> int:
        return int(c_lib.mostUtilizedEdge(self._id))

    def search(self, edge: int, demand: int, max_util: float) -> Move:
        c_move = c_lib.search(
            self._id, c_int32(edge), c_int32(demand), c_double(max_util)
        )

        mt = MoveType(ord(c_move.moveType))
        if mt == MoveType.UNKNOWN:
            return None

        return Move(
            move_type=mt,
            position=int(c_move.position),
            node=int(c_move.node),
            demand=int(c_move.demand),
        )

    def select_edge(self, r: float) -> int:
        return int(c_lib.selectEdge(self._id, c_double(r)))

    def select_demand(self, edge: int, r: float) -> int:
        d = int(c_lib.selectDemand(self._id, c_int32(edge), c_double(r)))
        return d if d >= 0 else None

    def edge_load(self, edge: int) -> int:
        return int(c_lib.edgeLoad(self._id, edge))

    def edge_util(self, edge: int) -> float:
        return float(c_lib.edgeUtilization(self._id, c_int32(edge)))
