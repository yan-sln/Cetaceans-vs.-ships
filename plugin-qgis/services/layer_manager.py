
# -*- coding: utf-8 -*-

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
)


class LayerManager:
    """
    Gestion des quatre couches géographiques du plugin.

    Les couches QGIS constituent uniquement une représentation
    de l'état transmis par le moteur Go.
    """

    PROPERTY_KEY = "cetaceans_vs_ships/role"

    LAYER_DEFINITIONS = {
        "routes": {
            "geometry": "LineString",
            "name": "Routes",
            "fields": (
                "field=route_id:string(80)"
                "&field=route_name:string(120)"
            ),
        },
        "ships": {
            "geometry": "Point",
            "name": "Navires",
            "fields": (
                "field=entity_id:string(80)"
                "&field=entity_type:string(80)"
                "&field=rotation:double"
                "&field=speed:double"
                "&field=length:double"
                "&field=revision:integer"
            ),
        },
        "cetaceans": {
            "geometry": "Point",
            "name": "Cétacés",
            "fields": (
                "field=entity_id:string(80)"
                "&field=entity_type:string(80)"
                "&field=rotation:double"
                "&field=speed:double"
                "&field=size:double"
                "&field=revision:integer"
            ),
        },
        "collisions": {
            "geometry": "Point",
            "name": "Collisions",
            "fields": (
                "field=event_id:string(80)"
                "&field=ship_id:string(80)"
                "&field=cetacean_id:string(80)"
                "&field=simulation_time:double"
                "&field=fatal:integer"
            ),
        },
    }

    def __init__(self):
        self.project = QgsProject.instance()

        self.routes_layer = None
        self.ships_layer = None
        self.cetaceans_layer = None
        self.collisions_layer = None

        # Identifiant métier -> FID QGIS
        self.ship_fids = {}
        self.cetacean_fids = {}
        self.collision_fids = {}

    # ---------------------------------------------------------
    # INITIALISATION
    # ---------------------------------------------------------

    def initializeLayers(self):
        """Crée ou retrouve les quatre couches du plugin."""

        layers = {}

        for role, definition in self.LAYER_DEFINITIONS.items():
            layer = self._findExistingLayer(role)

            if layer is None:
                layer = self._createLayer(role, definition)

            layers[role] = layer

        self.routes_layer = layers["routes"]
        self.ships_layer = layers["ships"]
        self.cetaceans_layer = layers["cetaceans"]
        self.collisions_layer = layers["collisions"]

        self._rebuildIndexes()

        return layers

    def _findExistingLayer(self, role):
        """Retrouve une couche appartenant au plugin."""

        for layer in self.project.mapLayers().values():
            if layer.customProperty(self.PROPERTY_KEY) == role:
                if isinstance(layer, QgsVectorLayer) and layer.isValid():
                    return layer

        return None

    def _createLayer(self, role, definition):
        """Crée une couche mémoire EPSG:4326."""

        uri = (
            f"{definition['geometry']}?"
            f"crs=EPSG:4326&"
            f"{definition['fields']}"
        )

        layer = QgsVectorLayer(
            uri,
            definition["name"],
            "memory",
        )

        if not layer.isValid():
            raise RuntimeError(
                f"Impossible de créer la couche {role}"
            )

        layer.setCustomProperty(self.PROPERTY_KEY, role)

        self.project.addMapLayer(layer)

        return layer

    # ---------------------------------------------------------
    # INDEX DES ENTITES
    # ---------------------------------------------------------

    def _rebuildIndexes(self):
        """Reconstruit les correspondances identifiant / FID."""

        self.ship_fids = self._buildIndex(
            self.ships_layer,
            "entity_id",
        )

        self.cetacean_fids = self._buildIndex(
            self.cetaceans_layer,
            "entity_id",
        )

        self.collision_fids = self._buildIndex(
            self.collisions_layer,
            "event_id",
        )

    @staticmethod
    def _buildIndex(layer, field_name):
        index = {}

        for feature in layer.getFeatures():
            identifier = feature[field_name]

            if identifier is not None:
                index[str(identifier)] = feature.id()

        return index

    # ---------------------------------------------------------
    # ROUTES
    # ---------------------------------------------------------

    def loadRoutes(self, routes):
        """
        Charge les routes prédéfinies.

        Format attendu :
        [
            {
                "id": "route_A",
                "name": "Route A",
                "coordinates": [
                    [-15.42, 28.13],
                    [-15.50, 28.20]
                ]
            }
        ]
        """

        if self.routes_layer.featureCount() > 0:
            return

        features = []

        for route in routes:
            coordinates = route.get("coordinates", [])

            if len(coordinates) < 2:
                continue

            points = [
                QgsPointXY(
                    float(coordinate[0]),
                    float(coordinate[1]),
                )
                for coordinate in coordinates
            ]

            feature = QgsFeature(self.routes_layer.fields())

            feature.setAttribute("route_id", route["id"])
            feature.setAttribute("route_name", route["name"])

            feature.setGeometry(
                QgsGeometry.fromPolylineXY(points)
            )

            features.append(feature)

        if features:
            success, _ = self.routes_layer.dataProvider().addFeatures(
                features
            )

            if not success:
                raise RuntimeError("Erreur lors du chargement des routes")

            self.routes_layer.updateExtents()

    # ---------------------------------------------------------
    # ENTITES DYNAMIQUES
    # ---------------------------------------------------------

    @staticmethod
    def _getEntityLayer(entity):
        """Détermine la couche à partir du type d'entité."""

        entity_type = str(entity.get("entity_type", "")).lower()

        if entity_type.startswith("ship"):
            return "ships"

        if entity_type.startswith("cetacean"):
            return "cetaceans"

        raise ValueError(
            f"Type d'entité inconnu : {entity_type}"
        )

    @staticmethod
    def _getPointGeometry(coordinates):
        """Construit une géométrie à partir de longitude / latitude."""

        longitude = float(coordinates["longitude"])
        latitude = float(coordinates["latitude"])

        return QgsGeometry.fromPointXY(
            QgsPointXY(longitude, latitude)
        )

    def addOrUpdateEntities(self, entities):
        """
        Ajoute ou actualise les entités reçues de Go.

        Les features existantes sont conservées.
        """

        providers = {
            "ships": self.ships_layer,
            "cetaceans": self.cetaceans_layer,
        }

        indexes = {
            "ships": self.ship_fids,
            "cetaceans": self.cetacean_fids,
        }

        new_features = {
            "ships": [],
            "cetaceans": [],
        }

        new_ids = {
            "ships": [],
            "cetaceans": [],
        }

        geometry_changes = {
            "ships": {},
            "cetaceans": {},
        }

        attribute_changes = {
            "ships": {},
            "cetaceans": {},
        }

        for entity in entities:
            role = self._getEntityLayer(entity)

            layer = providers[role]
            index = indexes[role]

            identifier = str(
                entity.get("id", entity.get("entity_id", ""))
            )

            if not identifier:
                raise ValueError("Identifiant d'entité absent")

            geometry = self._getPointGeometry(
                entity["coordinates"]
            )

            extra = entity.get("extra", {})

            values = {
                "entity_id": identifier,
                "entity_type": entity["entity_type"],
                "rotation": entity.get("rotation"),
                "speed": extra.get("speed"),
                "revision": entity.get("revision"),
            }

            if role == "ships":
                values["length"] = extra.get("length")
            else:
                values["size"] = extra.get("size")

            if identifier in index:
                fid = index[identifier]

                geometry_changes[role][fid] = geometry

                attribute_changes[role][fid] = {
                    layer.fields().indexFromName(name): value
                    for name, value in values.items()
                    if layer.fields().indexFromName(name) >= 0
                }

            else:
                feature = QgsFeature(layer.fields())

                for name, value in values.items():
                    feature.setAttribute(name, value)

                feature.setGeometry(geometry)

                new_features[role].append(feature)
                new_ids[role].append(identifier)

        # Application des modifications aux features existantes
        for role, layer in providers.items():
            provider = layer.dataProvider()

            if geometry_changes[role]:
                success = provider.changeGeometryValues(
                    geometry_changes[role]
                )

                if not success:
                    raise RuntimeError(
                        f"Erreur géométrique sur la couche {role}"
                    )

            if attribute_changes[role]:
                success = provider.changeAttributeValues(
                    attribute_changes[role]
                )

                if not success:
                    raise RuntimeError(
                        f"Erreur attributaire sur la couche {role}"
                    )

            # Ajout groupé des nouvelles features
            if new_features[role]:
                success, added_features = provider.addFeatures(
                    new_features[role]
                )

                if not success:
                    raise RuntimeError(
                        f"Impossible d'ajouter des entités à {role}"
                    )

                for feature in added_features:
                    identifier = str(feature["entity_id"])
                    indexes[role][identifier] = feature.id()

            if geometry_changes[role] or new_features[role]:
                layer.updateExtents()
                layer.triggerRepaint()

    # ---------------------------------------------------------
    # SUPPRESSION D'ENTITES
    # ---------------------------------------------------------

    def deleteEntities(self, identifiers):
        """Supprime les entités indiquées dans les couches dynamiques."""

        for role, layer, index in (
            ("ships", self.ships_layer, self.ship_fids),
            ("cetaceans", self.cetaceans_layer, self.cetacean_fids),
        ):
            fids = []

            for identifier in identifiers:
                fid = index.pop(str(identifier), None)

                if fid is not None:
                    fids.append(fid)

            if fids:
                success = layer.dataProvider().deleteFeatures(fids)

                if not success:
                    raise RuntimeError(
                        f"Erreur lors de la suppression dans {role}"
                    )

                layer.updateExtents()
                layer.triggerRepaint()

    # ---------------------------------------------------------
    # COLLISIONS
    # ---------------------------------------------------------

    def addCollisions(self, events):
        """Ajoute les événements de collision."""

        features = []

        for event in events:
            identifier = str(
                event.get("event_id", event.get("id", ""))
            )

            if not identifier:
                raise ValueError("Identifiant de collision absent")

            if identifier in self.collision_fids:
                continue

            feature = QgsFeature(self.collisions_layer.fields())

            feature.setAttribute("event_id", identifier)
            feature.setAttribute("ship_id", event.get("ship_id"))
            feature.setAttribute(
                "cetacean_id",
                event.get("cetacean_id"),
            )
            feature.setAttribute(
                "simulation_time",
                event.get("simulation_time"),
            )
            feature.setAttribute(
                "fatal",
                int(bool(event.get("fatal", False))),
            )

            feature.setGeometry(
                self._getPointGeometry(event["coordinates"])
            )

            features.append(feature)

        if features:
            success, added_features = (
                self.collisions_layer.dataProvider().addFeatures(
                    features
                )
            )

            if not success:
                raise RuntimeError(
                    "Impossible d'ajouter les collisions"
                )

            for feature in added_features:
                identifier = str(feature["event_id"])
                self.collision_fids[identifier] = feature.id()

            self.collisions_layer.updateExtents()
            self.collisions_layer.triggerRepaint()

    # ---------------------------------------------------------
    # SNAPSHOT ET LOTS DE MISE A JOUR
    # ---------------------------------------------------------

    def reconcileSnapshot(self, snapshot):
        """
        Réconcilie les entités QGIS avec un snapshot complet du moteur.

        Les entités absentes du snapshot sont supprimées.
        """

        entities = snapshot.get("entities", [])

        expected_ids = {
            "ships": set(),
            "cetaceans": set(),
        }

        for entity in entities:
            role = self._getEntityLayer(entity)
            identifier = str(
                entity.get("id", entity.get("entity_id", ""))
            )

            if identifier:
                expected_ids[role].add(identifier)

        obsolete_ids = (
            set(self.ship_fids) - expected_ids["ships"]
        ) | (
            set(self.cetacean_fids) - expected_ids["cetaceans"]
        )

        if obsolete_ids:
            self.deleteEntities(obsolete_ids)

        self.addOrUpdateEntities(entities)

    def applyBatch(self, batch):
        """Applique un lot de changements aux couches QGIS."""

        snapshot = batch.get("snapshot")

        if snapshot is not None:
            self.reconcileSnapshot(snapshot)

        self.addOrUpdateEntities(
            batch.get("entities", [])
        )

        self.deleteEntities(
            batch.get("deletions", [])
        )

        self.addCollisions(
            batch.get("collisions", [])
        )

    # ---------------------------------------------------------
    # REINITIALISATION
    # ---------------------------------------------------------

    def purgeSimulationLayers(self):
        """
        Vide les couches dynamiques.

        La couche des routes est conservée.
        """

        for layer, index in (
            (self.ships_layer, self.ship_fids),
            (self.cetaceans_layer, self.cetacean_fids),
            (self.collisions_layer, self.collision_fids),
        ):
            if layer is None:
                continue

            fids = [
                feature.id()
                for feature in layer.getFeatures()
            ]

            if fids:
                success = layer.dataProvider().deleteFeatures(fids)

                if not success:
                    raise RuntimeError(
                        f"Impossible de vider la couche {layer.name()}"
                    )

            index.clear()
            layer.updateExtents()

    def clear(self):
        """Réinitialise les index en mémoire du gestionnaire."""

        self.ship_fids.clear()
        self.cetacean_fids.clear()
        self.collision_fids.clear()

    def clearAllLayers(self):
        """Supprime toutes les features des quatre couches."""

        layers = (
            self.routes_layer,
            self.ships_layer,
            self.cetaceans_layer,
            self.collisions_layer,
        )

        for layer in layers:
            if layer is None or not layer.isValid():
                continue

            feature_ids = [
                feature.id()
                for feature in layer.getFeatures()
            ]

            if feature_ids:
                success = layer.dataProvider().deleteFeatures(
                    feature_ids
                )

                if not success:
                    raise RuntimeError(
                        f"Impossible de vider la couche {layer.name()}"
                    )

            layer.updateExtents()
            layer.triggerRepaint()

        # Reconstruction des index : ils seront désormais vides.
        self._rebuildIndexes()