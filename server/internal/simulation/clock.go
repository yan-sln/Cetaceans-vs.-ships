package simulation

type Clock struct {
	TempsEcoule float64
	Iteration   int
}

// Fait avancer le temps simule.
func (horloge *Clock) Advance(pasTemps float64) {

	horloge.TempsEcoule += pasTemps
	horloge.Iteration++
}
