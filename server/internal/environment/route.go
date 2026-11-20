package environment

import "server/internal/geometry"

type Route struct {
	ID        int
	Waypoints []geometry.Position
}

// Calcule la longueur totale de la route en metres.
func (r Route) Length() float64 {
	total := 0.0

	for i := 1; i < len(r.Waypoints); i++ {
		total += r.Waypoints[i-1].Distance(r.Waypoints[i])
	}

	return total
}
