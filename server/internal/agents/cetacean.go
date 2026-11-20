package agents

import "server/internal/geometry"

type Cetacean struct {
	ID        int
	Species   string
	Position  geometry.Position
	Speed     float64
	Direction float64
	Depth     float64
	Alive     bool
}

// Déplacer le cétacé pendant dt secondes
func (c *Cetacean) Move(dt float64) {
	if !c.Alive {
		return
	}

	c.Position = c.Position.Move(c.Speed, c.Direction, dt)
}
