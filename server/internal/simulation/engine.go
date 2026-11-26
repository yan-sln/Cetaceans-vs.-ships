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

	// Verifie que les routes attribuees aux navires existent.
	for _, navire := range monde.Ships {
		if navire.NumeroRoute != 0 &&
			monde.TrouverRoute(navire.NumeroRoute) == nil {
			return nil, fmt.Errorf(
				"route %d introuvable pour le navire %d",
				navire.NumeroRoute, navire.ID)
		}
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

	// Deplacement des navires.
	for indice := range moteur.Monde.Ships {
		navire := &moteur.Monde.Ships[indice]

		if navire.NumeroRoute == 0 {
			// Sans route, on garde le deplacement simple.
			navire.Move(pasTemps)
		} else {
			// Sinon, on suit la route attribuee.
			route := moteur.Monde.TrouverRoute(navire.NumeroRoute)
			navire.SuivreRoute(pasTemps, route.Waypoints)
		}
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
