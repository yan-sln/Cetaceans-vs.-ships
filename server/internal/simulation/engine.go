package simulation

import (
	"fmt"
	"server/internal/environment"
)

type State string

const (
	Pret    State = "ready"
	EnCours State = "running"
	EnPause State = "paused"
	Arrete  State = "stopped"
	Termine State = "finished"
)

type Engine struct {
	Monde         *environment.World
	Configuration Config
	Horloge       Clock
	Etat          State
}

// Initialiser le moteur de simulation
func NewEngine(monde *environment.World, configuration Config) (*Engine, error) {

	if monde == nil {
		return nil, fmt.Errorf("le monde est manquant")
	}

	if erreur := configuration.Validate(); erreur != nil {
		return nil, erreur
	}

	return &Engine{
		Monde:         monde,
		Configuration: configuration,
		Etat:          Pret,
	}, nil
}

// Demarre la simulation
func (moteur *Engine) Start() {
	if moteur.Etat == Pret {
		moteur.Etat = EnCours
	}
}

// Met en pause la simulation
func (moteur *Engine) Pause() {
	if moteur.Etat == EnCours {
		moteur.Etat = EnPause
	}
}

// Reprend la simulation
func (moteur *Engine) Resume() {
	if moteur.Etat == EnPause {
		moteur.Etat = EnCours
	}
}

// Arreter la simulation
func (moteur *Engine) Stop() {
	if moteur.Etat == Pret || moteur.Etat == EnCours || moteur.Etat == EnPause {
		moteur.Etat = Arrete
	}
}

// Execute une iteration de la simulation
func (moteur *Engine) Step() bool {

	if moteur.Etat != EnCours {
		return false
	}

	tempsRestant := moteur.Configuration.Duree - moteur.Horloge.TempsEcoule
	pasTemps := moteur.Configuration.PasTemps

	// Ajuster dernier pas de temps
	if pasTemps > tempsRestant {
		pasTemps = tempsRestant
	}

	// Deplacement de tous les navires
	for i := range moteur.Monde.Ships {
		moteur.Monde.Ships[i].Move(pasTemps)
	}

	// Deplacement de tous les cetaces
	for i := range moteur.Monde.Cetaceans {
		moteur.Monde.Cetaceans[i].Move(pasTemps)
	}

	// Mettre a jour de l'horloge
	moteur.Horloge.Advance(pasTemps)

	// Verifier  la fin de simulation
	if pasTemps == tempsRestant {
		moteur.Horloge.TempsEcoule = moteur.Configuration.Duree
		moteur.Etat = Termine
	}

	return true
}
