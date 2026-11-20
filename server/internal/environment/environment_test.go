package environment

import (
	"server/internal/geometry"
	"testing"
)

func TestWorldContains(t *testing.T) {
	world := World{
		Width:  1000,
		Height: 1000,
	}

	if !world.Contains(geometry.Position{X: 500, Y: 500}) {
		t.Error("Position interieure refusee")
	}

	if world.Contains(geometry.Position{X: 1100, Y: 500}) {
		t.Error("Position exterieure acceptee")
	}
}

func TestSensitiveZone(t *testing.T) {
	world := World{
		Zones: []Zone{
			{
				Center: geometry.Position{X: 500, Y: 500},
				Radius: 150,
			},
		},
	}

	if !world.IsInSensitiveZone(geometry.Position{X: 450, Y: 500}) {
		t.Error("Zone non detectee")
	}

	if world.IsInSensitiveZone(geometry.Position{X: 100, Y: 500}) {
		t.Error("Zone detectee a tort")
	}
}

func TestRouteLength(t *testing.T) {
	route := Route{
		Waypoints: []geometry.Position{
			{X: 0, Y: 0},
			{X: 3, Y: 4},
			{X: 6, Y: 8},
		},
	}

	if route.Length() != 10 {
		t.Errorf("Longueur obtenue : %f, attendue : 10",
			route.Length())
	}
}
