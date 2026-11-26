package agents

import (
	"math"
	"server/internal/geometry"
)

type Cetacean struct {
	ID        int
	Species   string
	Position  geometry.Position
	Speed     float64
	Direction float64
	Depth     float64
	Alive     bool

	VitesseRotation  float64
	VitesseVerticale float64
	ProfondeurMax    float64
}

// Deplace le cetace et actualise sa profondeur.
func (cetace *Cetacean) Move(pasTemps float64) {
	if !cetace.Alive || pasTemps <= 0 {
		return
	}

	// Changement progressif de direction.
	cetace.Direction += cetace.VitesseRotation * pasTemps

	// Deplacement horizontal.
	cetace.Position = cetace.Position.Move(
		cetace.Speed, cetace.Direction, pasTemps)

	// Aucun mouvement vertical si la plongee n'est pas configuree.
	if cetace.ProfondeurMax <= 0 || cetace.VitesseVerticale == 0 {
		return
	}

	// Calcul de la nouvelle profondeur.
	profondeur := cetace.Depth + cetace.VitesseVerticale*pasTemps

	// Rebond aux limites : surface et profondeur maximale.
	for profondeur < 0 || profondeur > cetace.ProfondeurMax {
		if profondeur > cetace.ProfondeurMax {
			profondeur = 2*cetace.ProfondeurMax - profondeur
			cetace.VitesseVerticale = -math.Abs(cetace.VitesseVerticale)
		} else {
			profondeur = -profondeur
			cetace.VitesseVerticale = math.Abs(cetace.VitesseVerticale)
		}
	}

	cetace.Depth = profondeur

	if cetace.Depth == 0 {
		cetace.VitesseVerticale = math.Abs(cetace.VitesseVerticale)
	} else if cetace.Depth == cetace.ProfondeurMax {
		cetace.VitesseVerticale = -math.Abs(cetace.VitesseVerticale)
	}
}
