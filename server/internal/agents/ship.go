package agents

import "server/internal/geometry"

type Ship struct {
	ID        int
	Position  geometry.Position
	Speed     float64
	Direction float64
	Length    float64
	Width     float64
	Draft     float64 //(le tirant d'eau)information utile qui nous permettra de déterminer si un cétacé est suffisamment proche de la surface pour risquer une collision
}

// Déplacer le navire pendant dt secondes
func (s *Ship) Move(dt float64) {
	s.Position = s.Position.Move(s.Speed, s.Direction, dt)
}
