package agents

import (
	"math"
	"server/internal/geometry"
	"testing"
)

func TestNavireSuitRoute(t *testing.T) {
	navire := Ship{
		Position: geometry.Position{X: 0, Y: 0},
		Speed:    5,
	}

	points := []geometry.Position{
		{X: 0, Y: 0},
		{X: 10, Y: 0},
		{X: 10, Y: 10},
	}

	navire.SuivreRoute(3, points)

	attendu := geometry.Position{X: 10, Y: 5}
	if navire.Position.Distance(attendu) > 1e-9 {
		t.Errorf("Position incorrecte : %+v", navire.Position)
	}

	navire.SuivreRoute(1, points)

	if !navire.EstArrive {
		t.Error("Le navire devrait etre arrive")
	}
}

func TestPlongeeEtRemontee(t *testing.T) {
	cetace := Cetacean{
		Alive:            true,
		VitesseVerticale: 3,
		ProfondeurMax:    6,
	}

	profondeursAttendues := []float64{3, 6, 3, 0, 3}

	for _, attendu := range profondeursAttendues {
		cetace.Move(1)

		if cetace.Depth != attendu {
			t.Errorf("Profondeur : %.1f, attendue : %.1f",
				cetace.Depth, attendu)
		}
	}
}

func TestChangementDirection(t *testing.T) {
	cetace := Cetacean{
		Alive:           true,
		Speed:           2,
		VitesseRotation: math.Pi / 2,
	}

	cetace.Move(1)

	if math.Abs(cetace.Position.X) > 1e-9 ||
		math.Abs(cetace.Position.Y-2) > 1e-9 {
		t.Errorf("Deplacement incorrect : %+v", cetace.Position)
	}
}
