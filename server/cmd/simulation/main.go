package main

import (
	"fmt"
	"math"
	"server/internal/agents"
	"server/internal/environment"
	"server/internal/geometry"
	"server/internal/simulation"
)

func main() {

	// Initialisation du monde maritime.
	monde := environment.World{
		Width:  1000,
		Height: 1000,

		Ships: []agents.Ship{
			{
				ID:       1,
				Position: geometry.Position{X: 100, Y: 500},
				Speed:    10,
				Length:   100,
				Width:    20,
				Draft:    5,
			},
			{
				ID:       2,
				Position: geometry.Position{X: 450, Y: 500},
				Speed:    8,
				Length:   80,
				Width:    15,
				Draft:    4,
			},
		},

		Cetaceans: []agents.Cetacean{
			{
				ID:        1,
				Species:   "Cachalot",
				Position:  geometry.Position{X: 500, Y: 500},
				Speed:     2,
				Direction: math.Pi,
				Alive:     true,
			},
			{
				ID:       2,
				Species:  "Dauphin",
				Position: geometry.Position{X: 750, Y: 800},
				Speed:    3,
				Depth:    10,
				Alive:    true,
			},
		},

		Zones: []environment.Zone{
			{
				ID:     1,
				Center: geometry.Position{X: 500, Y: 500},
				Radius: 150,
			},
		},

		Routes: []environment.Route{
			{
				ID: 1,
				Waypoints: []geometry.Position{
					{X: 100, Y: 500},
					{X: 500, Y: 500},
					{X: 900, Y: 500},
				},
			},
		},
	}

	// Configuration de la simulation.
	configuration := simulation.Config{
		PasTemps: 1,
		Duree:    10,
	}

	// Creation du moteur.
	moteur, erreur := simulation.NewEngine(&monde, configuration)

	if erreur != nil {
		fmt.Println(erreur)
		return
	}

	// Demarrage de la simulation.
	moteur.Start()

	// Boucle principale de simulation.
	for moteur.Step() {

		fmt.Printf("\nTemps : %.1f s | Iteration : %d\n",
			moteur.Horloge.TempsEcoule,
			moteur.Horloge.Iteration)

		// Affichage des navires.
		for _, navire := range monde.Ships {
			fmt.Printf("Navire %d : (%.1f, %.1f)\n",
				navire.ID,
				navire.Position.X,
				navire.Position.Y)
		}

		// Affichage des cetaces.
		for _, cetace := range monde.Cetaceans {
			fmt.Printf("Cetace %d : (%.1f, %.1f)\n",
				cetace.ID,
				cetace.Position.X,
				cetace.Position.Y)
		}
	}

	fmt.Println("\nEtat final :", moteur.Etat)
}
