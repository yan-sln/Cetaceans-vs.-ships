package geometry

import (
	"math"
	"testing"
)

func TestDistance(t *testing.T) {
	p1 := Position{X: 0, Y: 0}
	p2 := Position{X: 3, Y: 4}

	result := p1.Distance(p2)
	expected := 5.0

	if math.Abs(result-expected) > 1e-9 {
		t.Errorf("Distance obtenue : %f, attendue : %f",
			result, expected)
	}
}

func TestMoveEast(t *testing.T) {
	p := Position{X: 10, Y: 20}

	result := p.Move(5, 0, 2)

	if math.Abs(result.X-20) > 1e-9 ||
		math.Abs(result.Y-20) > 1e-9 {
		t.Errorf("Position incorrecte : %+v", result)
	}
}

func TestMoveNorth(t *testing.T) {
	p := Position{X: 10, Y: 20}

	result := p.Move(5, math.Pi/2, 2)

	if math.Abs(result.X-10) > 1e-9 ||
		math.Abs(result.Y-30) > 1e-9 {
		t.Errorf("Position incorrecte : %+v", result)
	}
}

func TestMoveZeroTime(t *testing.T) {
	p := Position{X: 10, Y: 20}

	result := p.Move(5, 0, 0)

	if result != p {
		t.Errorf("La position ne doit pas changer : %+v", result)
	}
}
