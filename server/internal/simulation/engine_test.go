package simulation

import (
	"server/internal/agents"
	"server/internal/environment"
	"server/internal/geometry"
	"testing"
)

// Cree un petit moteur pour effectuer les tests.
func moteurTest(t *testing.T, duree float64) *Engine {
	t.Helper()

	monde := &environment.World{
		Width:  1000,
		Height: 1000,

		Ships: []agents.Ship{
			{
				Position: geometry.Position{X: 100, Y: 500},
				Speed:    10,
			},
			{
				Position: geometry.Position{X: 450, Y: 500},
				Speed:    8,
			},
		},

		Cetaceans: []agents.Cetacean{
			{
				Position: geometry.Position{X: 500, Y: 500},
				Speed:    2,
				Alive:    true,
			},
		},
	}

	moteur, erreur := NewEngine(monde, Config{
		PasTemps: 1,
		Duree:    duree,
	})

	if erreur != nil {
		t.Fatal(erreur)
	}

	return moteur
}

func TestIteration(t *testing.T) {

	moteur := moteurTest(t, 10)
	moteur.Start()

	if !moteur.Step() {
		t.Fatal("Le moteur n'a pas avance")
	}

	if moteur.Horloge.TempsEcoule != 1 ||
		moteur.Horloge.Iteration != 1 {
		t.Error("Horloge incorrecte")
	}

	if moteur.Monde.Ships[0].Position.X != 110 ||
		moteur.Monde.Ships[1].Position.X != 458 {
		t.Error("Position des navires incorrecte")
	}

	if moteur.Monde.Cetaceans[0].Position.X != 502 {
		t.Error("Position du cetace incorrecte")
	}
}

func TestPauseRepriseArret(t *testing.T) {

	moteur := moteurTest(t, 10)

	if moteur.Step() {
		t.Fatal("Le moteur ne doit pas avancer avant le demarrage")
	}

	moteur.Start()
	moteur.Step()
	moteur.Pause()

	if moteur.Step() || moteur.Horloge.TempsEcoule != 1 {
		t.Fatal("La pause ne fonctionne pas")
	}

	moteur.Resume()

	if !moteur.Step() || moteur.Horloge.TempsEcoule != 2 {
		t.Fatal("La reprise ne fonctionne pas")
	}

	moteur.Stop()

	if moteur.Step() || moteur.Etat != Arrete {
		t.Fatal("L'arret ne fonctionne pas")
	}
}

func TestFinSimulation(t *testing.T) {

	moteur := moteurTest(t, 2.5)
	moteur.Start()

	for moteur.Step() {
	}

	if moteur.Horloge.TempsEcoule != 2.5 ||
		moteur.Horloge.Iteration != 3 ||
		moteur.Etat != Termine {
		t.Fatal("Fin de simulation incorrecte")
	}

	if moteur.Monde.Ships[0].Position.X != 125 {
		t.Fatal("Dernier deplacement incorrect")
	}
}

func TestConfigurationInvalide(t *testing.T) {

	_, erreur := NewEngine(&environment.World{}, Config{
		PasTemps: 0,
		Duree:    10,
	})

	if erreur == nil {
		t.Error("Un pas de temps nul doit etre refuse")
	}
}
