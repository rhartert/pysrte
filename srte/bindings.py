import ctypes
from ctypes import Structure, c_char, c_double, c_int32, c_int64, c_ulong

c_lib = ctypes.CDLL("srte-c-bindings.so")


class C_Move(Structure):
    _fields_ = [
        ("moveType", c_char),
        ("position", c_int32),
        ("node", c_int32),
        ("demand", c_int32),
    ]


class C_Edge(Structure):
    _fields_ = [
        ("src", c_int32),
        ("dest", c_int32),
        ("weight", c_int32),
        ("capacity", c_int64),
    ]


class C_Demand(Structure):
    _fields_ = [
        ("src", c_int32),
        ("dest", c_int32),
        ("traffic", c_int64),
    ]


class C_Config(Structure):
    _fields_ = [
        ("maxNodes", c_int32),
        ("alpha", c_double),
        ("beta", c_double),
    ]


c_lib.newInstance.restype = c_ulong
c_lib.freeInstance.restype = None
c_lib.addEdge.restype = None
c_lib.addDemand.restype = None
c_lib.newSolver.restype = c_ulong
c_lib.freeSolver.restype = None
c_lib.applyMove.restype = c_char
c_lib.maxUtilization.restype = c_double
c_lib.mostUtilizedEdge.restype = c_int32
c_lib.search.restype = C_Move
c_lib.selectEdge.restype = c_int32
c_lib.selectDemand.restype = c_int32
c_lib.edgeLoad.restype = c_int64
c_lib.edgeUtilization.restype = c_double
