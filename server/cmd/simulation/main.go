package main

import (
	"fmt"
	"math"
	"server/internal/agents"
	"server/internal/environment"
	"server/internal/geometry"
)

func main() {

	world := environment.World{
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

	fmt.Printf("Monde : %.0f x %.0f m\n",
		world.Width, world.Height)

	fmt.Println("Navires :", len(world.Ships))
	fmt.Println("Cetaces :", len(world.Cetaceans))
	fmt.Println("Zones sensibles :", len(world.Zones))
	fmt.Println("Routes :", len(world.Routes))

	for _, ship := range world.Ships {
		fmt.Printf("Navire %d - Dans une zone sensible : %t\n",
			ship.ID,
			world.IsInSensitiveZone(ship.Position))
	}

	for _, route := range world.Routes {
		fmt.Printf("Route %d - Longueur : %.0f m\n",
			route.ID, route.Length())
	}
}
