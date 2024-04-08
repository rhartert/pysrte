package main

//struct Move {
//  char moveType;
//  int position;
//  int node;
//  int demand;
//};
//
//struct Edge {
//	int src;
//  int dest;
//  int weight;
//  long capacity;
//};
//
//struct Demand {
//  int src;
//  int dest;
//  long traffic;
//};
//
//struct Config {
//  int maxNodes;
//  double alpha;
//  double beta;
//};
//
// #include <stdlib.h>
import "C"

import (
	"fmt"

	"github.com/rhartert/srte-ls/solver"
	"github.com/rhartert/srte-ls/srte"
)

// Instance
// --------

type instanceID = uint64

var instances = map[instanceID]*instance{}

type edge struct {
	src    int
	dest   int
	weight int
	capa   int64
}

type demand struct {
	src     int
	dest    int
	traffic int64
}

type instance struct {
	edges   []edge
	demands []demand
}

//export newInstance
func newInstance() C.ulong {
	iid := instanceID(42)
	instances[iid] = &instance{}
	return C.ulong(iid)
}

//export freeInstance
func freeInstance(iid C.ulong) {
	delete(instances, instanceID(iid))
}

//export addEdge
func addEdge(iid C.ulong, e C.struct_Edge) {
	inst := instances[instanceID(iid)]
	inst.edges = append(inst.edges, edge{
		src:    int(e.src),
		dest:   int(e.dest),
		capa:   int64(e.capacity),
		weight: int(e.weight),
	})
}

//export addDemand
func addDemand(iid C.ulong, d C.struct_Demand) {
	inst := instances[instanceID(iid)]
	inst.demands = append(inst.demands, demand{
		src:     int(d.src),
		dest:    int(d.dest),
		traffic: int64(d.traffic),
	})
}

//export printInstance
func printInstance(iid C.ulong) {
	inst := instances[instanceID(iid)]
	fmt.Printf("nEdges: %d, nDemands: %d", len(inst.edges), len(inst.demands))
}

// Solver
// ------

type solverID = uint64

var solvers = map[solverID]*solver.LinkGuidedSolver{}

//export newSolver
func newSolver(iid C.ulong, cfg C.struct_Config) C.ulong {
	inst := instances[instanceID(iid)]
	nEdges := len(inst.edges)
	edges := make([]srte.Edge, nEdges)
	capacities := make([]int64, nEdges)
	nNodes := 0
	for i, e := range inst.edges {
		edges[i] = srte.Edge{
			From: e.src,
			To:   e.dest,
			Cost: e.weight,
		}
		capacities[i] = e.capa * 1000
		if e.src > nNodes {
			nNodes = e.src + 1
		}
		if e.dest > nNodes {
			nNodes = e.dest + 1
		}
	}

	demands := make([]srte.Demand, len(inst.demands))
	for i, d := range inst.demands {
		demands[i] = srte.Demand{
			From:      d.src,
			To:        d.dest,
			Bandwidth: d.traffic * 1000,
		}
	}

	topology := srte.NewTopology(edges, nNodes)
	fgraphs, _ := srte.NewFGraphs(topology)
	state, _ := srte.NewSRTE(&srte.SRTEInstance{
		Graph:          topology,
		FGraphs:        fgraphs,
		MaxPathNodes:   int(cfg.maxNodes) + 2,
		Demands:        demands,
		LinkCapacities: capacities,
	})

	sid := solverID(len(solvers))
	s := solver.NewLinkGuidedSolver(state, solver.Config{
		Alpha: float64(cfg.alpha),
		Beta:  float64(cfg.beta),
	})
	solvers[sid] = s
	return C.ulong(sid)
}

//export freeSolver
func freeSolver(sid C.ulong) {
	delete(solvers, solverID(sid))
}

//export applyMove
func applyMove(sid C.ulong, move C.struct_Move) C.char {
	s := solvers[solverID(sid)]
	applied := s.ApplyMove(srte.Move{
		MoveType: srte.MoveType(move.moveType),
		Position: int(move.position),
		Node:     int(move.node),
		Demand:   int(move.demand),
	})

	if applied {
		return C.char(1)
	} else {
		return C.char(0)
	}
}

//export maxUtilization
func maxUtilization(sid C.ulong) C.double {
	s := solvers[solverID(sid)]
	return C.double(s.MaxUtilization())
}

//export mostUtilizedEdge
func mostUtilizedEdge(sid C.ulong) C.int {
	s := solvers[solverID(sid)]
	return C.int(s.MostUtilizedEdge())

}

//export search
func search(sid C.ulong, edge C.int, demand C.int, maxUtil C.double) C.struct_Move {
	s := solvers[solverID(sid)]
	m, found := s.Search(int(edge), int(demand), float64(maxUtil))
	if !found {
		return C.struct_Move{moveType: C.char(srte.MoveUnknown)}
	}

	return C.struct_Move{
		moveType: C.char(m.MoveType),
		position: C.int(m.Position),
		node:     C.int(m.Node),
		demand:   C.int(m.Demand),
	}
}

//export selectEdge
func selectEdge(sid C.ulong, r C.double) C.int {
	s := solvers[solverID(sid)]
	return C.int(s.SelectEdge(float64(r)))
}

//export selectDemand
func selectDemand(sid C.ulong, edge C.int, r C.double) C.int {
	s := solvers[solverID(sid)]
	return C.int(s.SelectDemand(int(edge), float64(r)))
}

//export edgeLoad
func edgeLoad(sid C.ulong, edge C.int) C.long {
	s := solvers[solverID(sid)]
	return C.long(s.State.Load(int(edge)))
}

//export edgeUtilization
func edgeUtilization(sid C.ulong, edge C.int) C.double {
	s := solvers[solverID(sid)]
	return C.double(s.State.Utilization(int(edge)))
}

func main() {}
