package simulation

import (
	"server/internal/agents"
	"server/internal/environment"
	"server/internal/geometry"
	"testing"
)

func TestMoteurAvecRoute(t *testing.T) {
	monde := &environment.World{
		Ships: []agents.Ship{
			{ID: 1, Speed: 5, NumeroRoute: 3},
		},
		Routes: []environment.Route{
			{
				ID: 3,
				Waypoints: []geometry.Position{
					{X: 0, Y: 0},
					{X: 10, Y: 0},
					{X: 10, Y: 10},
				},
			},
		},
	}

	moteur, erreur := NewEngine(monde, Config{
		PasTemps: 1,
		Duree:    4,
	})
	if erreur != nil {
		t.Fatal(erreur)
	}

	moteur.Start()

	for moteur.Step() {
	}

	if !monde.Ships[0].EstArrive {
		t.Fatal("Le navire n'est pas arrive")
	}
}

func TestRouteInconnue(t *testing.T) {
	monde := &environment.World{
		Ships: []agents.Ship{
			{ID: 1, NumeroRoute: 55},
		},
	}

	_, erreur := NewEngine(monde, Config{
		PasTemps: 1,
		Duree:    2,
	})

	if erreur == nil {
		t.Fatal("Une route inexistante doit etre refusee")
	}
}
