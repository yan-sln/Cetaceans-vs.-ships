package environment

import (
	"server/internal/agents"
	"server/internal/geometry"
)

type World struct {
	Width     float64
	Height    float64
	Ships     []agents.Ship
	Cetaceans []agents.Cetacean
	Zones     []Zone
	Routes    []Route
}

// Verifier si une position appartient au monde
func (w World) Contains(p geometry.Position) bool {
	return p.X >= 0 && p.X <= w.Width &&
		p.Y >= 0 && p.Y <= w.Height
}

// Verifie si une position appartient a une zone sensible
func (w World) IsInSensitiveZone(p geometry.Position) bool {
	for _, zone := range w.Zones {
		if zone.Contains(p) {
			return true
		}
	}

	return false
}
