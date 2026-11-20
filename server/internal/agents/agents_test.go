package agents

import (
	"math"
	"server/internal/geometry"
	"testing"
)

func TestShipMove(t *testing.T) {
	ship := Ship{
		ID:        1,
		Position:  geometry.Position{X: 10, Y: 50},
		Speed:     10,
		Direction: 0,
	}

	ship.Move(5)

	expected := geometry.Position{X: 60, Y: 50}

	if ship.Position.Distance(expected) > 1e-9 {
		t.Errorf("Position incorrecte : %+v", ship.Position)
	}
}

func TestCetaceanMove(t *testing.T) {
	whale := Cetacean{
		ID:        1,
		Position:  geometry.Position{X: 80, Y: 50},
		Speed:     2,
		Direction: math.Pi,
		Alive:     true,
	}

	whale.Move(5)

	expected := geometry.Position{X: 70, Y: 50}

	if whale.Position.Distance(expected) > 1e-9 {
		t.Errorf("Position incorrecte : %+v", whale.Position)
	}
}

func TestDeadCetaceanDoesNotMove(t *testing.T) {
	whale := Cetacean{
		ID:       1,
		Position: geometry.Position{X: 80, Y: 50},
		Speed:    2,
		Alive:    false,
	}

	initialPosition := whale.Position

	whale.Move(5)

	if whale.Position != initialPosition {
		t.Error("Un cetace mort ne doit pas se deplacer")
	}
}
