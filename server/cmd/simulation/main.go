package main

import (
	"fmt"
	"server/internal/geometry"
)

func main() {
	fmt.Println("==============================")
	fmt.Println("    Cetaceans vs. Ships")
	fmt.Println("==============================")

	fmt.Println("Moteur de simulation initialisé")

	boat := geometry.Position{X: 10, Y: 50}
	whale := geometry.Position{X: 80, Y: 50}

	fmt.Printf("Position du bateau : (%.2f, %.2f)\n",
		boat.X, boat.Y)

	fmt.Printf("Position du cétacé : (%.2f, %.2f)\n",
		whale.X, whale.Y)

	distance := boat.Distance(whale)

	fmt.Printf("Distance initiale : %.2f m\n", distance)

	// Déplacement du bateau à 10 m/s pendant 5 secondes.
	boat = boat.Move(10, 0, 5)

	fmt.Printf("Nouvelle position du bateau : (%.2f, %.2f)\n",
		boat.X, boat.Y)

	fmt.Printf("Nouvelle distance : %.2f m\n",
		boat.Distance(whale))
}
