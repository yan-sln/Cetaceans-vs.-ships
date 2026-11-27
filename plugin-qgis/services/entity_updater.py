# -*- coding: utf-8 -*-

class EntityUpdater:
    """Regroupe les changements reçus du moteur avant leur affichage."""

    def __init__(self):
        self.pending_states = {}
        self.pending_deletions = set()
        self.pending_collisions = []

    def enqueue_message(self, message):
        message_type = message.get("type")

        if message_type == "entity_updates":
            for entity in message.get("entities", []):
                entity_id = entity.get("id")

                if not entity_id:
                    continue

                revision = entity.get("revision", 0)
                previous = self.pending_states.get(entity_id)

                if previous is not None:
                    if revision <= previous.get("revision", 0):
                        continue

                self.pending_states[entity_id] = entity
                self.pending_deletions.discard(entity_id)

        elif message_type == "entity_delete":
            entity_id = message.get("id")

            if entity_id:
                self.pending_states.pop(entity_id, None)
                self.pending_deletions.add(entity_id)

        elif message_type == "collision":
            event = message.get("event")

            if event:
                self.pending_collisions.append(event)

    def take_pending_batch(self):
        """Récupère les changements et vide les files en attente."""

        batch = {
            "entities": list(self.pending_states.values()),
            "deletions": list(self.pending_deletions),
            "collisions": list(self.pending_collisions),
        }

        self.clear()
        return batch

    def clear(self):
        self.pending_states.clear()
        self.pending_deletions.clear()
        self.pending_collisions.clear()

    def has_pending_updates(self):
        return bool(
            self.pending_states
            or self.pending_deletions
            or self.pending_collisions
        )