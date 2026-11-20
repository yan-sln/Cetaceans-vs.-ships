package environment

import "server/internal/geometry"

type Zone struct {
	ID     int
	Center geometry.Position
	Radius float64
}

// Verifier si une position se trouve dans la zone.
func (z Zone) Contains(p geometry.Position) bool {
	return z.Center.Distance(p) <= z.Radius
}
