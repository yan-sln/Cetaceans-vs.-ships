package main

import (
	"fmt"
	"math"
	"server/internal/agents"
	"server/internal/geometry"
)

func main() {
	fmt.Println("==============================")
	fmt.Println("    Cetaceans vs. Ships")
	fmt.Println("==============================")

	ship := agents.Ship{
		ID:        1,
		Position:  geometry.Position{X: 10, Y: 50},
		Speed:     10,
		Direction: 0,
		Length:    100,
		Width:     20,
		Draft:     5,
	}

	whale := agents.Cetacean{
		ID:        1,
		Species:   "Cachalot",
		Position:  geometry.Position{X: 80, Y: 50},
		Speed:     2,
		Direction: math.Pi,
		Depth:     0,
		Alive:     true,
	}

	fmt.Println("\nEtat initial :")
	fmt.Printf("Navire : (%.2f, %.2f)\n",
		ship.Position.X, ship.Position.Y)

	fmt.Printf("Cetace : (%.2f, %.2f)\n",
		whale.Position.X, whale.Position.Y)

	fmt.Printf("Distance : %.2f m\n",
		ship.Position.Distance(whale.Position))

	// On fait avancer les deux agents de 5 secondes.
	dt := 5.0

	ship.Move(dt)
	whale.Move(dt)

	fmt.Println("\nEtat apres 5 secondes :")

	fmt.Printf("Navire : (%.2f, %.2f)\n",
		ship.Position.X, ship.Position.Y)

	fmt.Printf("Cetace : (%.2f, %.2f)\n",
		whale.Position.X, whale.Position.Y)

	fmt.Printf("Distance : %.2f m\n",
		ship.Position.Distance(whale.Position))
}
