# -*- coding: utf-8 -*-
import collections

categories = collections.OrderedDict(
    {
        "essen": {
            "discounter": {"query": "Discounter", "id": 0},
            "supermarkt": {"query": "Supermarkt", "id": 1},
            "biosupermarkt": {"query": "Biosupermarkt", "id": 2},
            "bioladen": {"query": "Bioladen", "id": 3},
            "unverpackladen": {"query": "Unverpackt Laden", "id": 4},
            "biowochenmarkt": {"query": "Biowochenmarkt", "id": 5},
            "convenience": {"query": "Convenience Store", "id": 6},
        },
        "bekleidung": {
            "bekleidungsgeschaeft": {"query": "Bekleidungsgeschäft", "id": 0},
            "oekobekleidungsgeschaeft": {"query": "Öko Bekleidungsgeschäft", "id": 1},
            "faires_bekleidungsgeschaeft": {"query": "Faires Bekleidungsgeschäft", "id": 2},
            "second_hand": {"query": "Second Hand", "id": 3},
            "oekobekleidungsgeschaeft_spez": {
                "query": "Spezialisiertes Öko Bekleidungsgeschäft",
                "id": 4,
            },
            "faires_bekleidungsgeschaeft_spez": {
                "query": "Spezialisiertes Faires Bekleidungsgeschäft",
                "id": 5,
            },
        },
    }
)
