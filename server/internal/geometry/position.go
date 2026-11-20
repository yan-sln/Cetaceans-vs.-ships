package geometry

import "math"

// Position (en mètres) d'un agent dans l'environnement
type Position struct {
	X float64
	Y float64
}

// la distance entre deux positions
func (p Position) Distance(other Position) float64 {
	dx := other.X - p.X
	dy := other.Y - p.Y

	return math.Hypot(dx, dy)
}

// Calculer la nouvelle position après un déplacement
// speed: vitesse en m/s
// direction: angle en radians
// dt: temps écoulé en secondes
func (p Position) Move(speed, direction, dt float64) Position {
	return Position{
		X: p.X + speed*math.Cos(direction)*dt,
		Y: p.Y + speed*math.Sin(direction)*dt,
	}
}
