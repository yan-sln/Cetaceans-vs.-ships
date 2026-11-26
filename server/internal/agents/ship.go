package agents

import (
	"math"
	"server/internal/geometry"
)

type Ship struct {
	ID        int
	Position  geometry.Position
	Speed     float64
	Direction float64
	Length    float64
	Width     float64
	Draft     float64

	NumeroRoute  int
	PointSuivant int
	EstArrive    bool
}

// Deplacement simple en ligne droite.
func (navire *Ship) Move(pasTemps float64) {
	navire.Position = navire.Position.Move(
		navire.Speed, navire.Direction, pasTemps)
}

// Fait suivre au navire les points de sa route.
func (navire *Ship) SuivreRoute(pasTemps float64, points []geometry.Position) {
	if navire.EstArrive || navire.Speed <= 0 ||
		pasTemps <= 0 || len(points) == 0 {
		return
	}

	tempsRestant := pasTemps

	for tempsRestant > 0 && navire.PointSuivant < len(points) {
		cible := points[navire.PointSuivant]
		distance := navire.Position.Distance(cible)

		// Si le navire est deja sur le point, passer au suivant.
		if distance < 1e-9 {
			navire.Position = cible
			navire.PointSuivant++
			continue
		}

		// Calculer la direction vers le prochain point.
		navire.Direction = math.Atan2(
			cible.Y-navire.Position.Y,
			cible.X-navire.Position.X,
		)

		tempsNecessaire := distance / navire.Speed

		if tempsRestant >= tempsNecessaire {
			// Le navire atteint le point pendant cette iteration.
			navire.Position = cible
			tempsRestant -= tempsNecessaire
			navire.PointSuivant++
		} else {
			// Le navire avance sans atteindre le point.
			navire.Position = navire.Position.Move(
				navire.Speed, navire.Direction, tempsRestant)
			tempsRestant = 0
		}
	}

	// Tous les points de la route ont ete atteints.
	if navire.PointSuivant >= len(points) {
		navire.EstArrive = true
	}
}
