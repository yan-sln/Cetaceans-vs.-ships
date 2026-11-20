package simulation

import (
	"fmt"
	"math"
)

type Config struct {
	PasTemps float64
	Duree    float64
}

// Verifie que les parametres sont valides.
func (c Config) Validate() error {

	if c.PasTemps <= 0 || math.IsNaN(c.PasTemps) || math.IsInf(c.PasTemps, 0) {
		return fmt.Errorf("le pas de temps doit etre positif et fini")
	}

	if c.Duree <= 0 || math.IsNaN(c.Duree) || math.IsInf(c.Duree, 0) {
		return fmt.Errorf("la duree doit etre positive et finie")
	}

	return nil
}
