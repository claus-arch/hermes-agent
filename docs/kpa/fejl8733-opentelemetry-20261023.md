# FEJL-8733: OpenTelemetry-parser i Hermes

OpenTelemetry API er låst til1.45.1. Det valgfrie OTLP-SDK og HTTP-exporter
følger samme patch. Den gamle mistralai2.4.8 låste semantic-conventions<0.61
og gjorde en sikker opløsning umulig;2.9.2 er den første kompatible2.x-release.
Mistral ligger fortsat uden for de normale extras. Alle nye releases er ældre
end karantænevinduet; det er bevaret. PM har løst hele låsen uden overrides.

Isoleret PM-build af de18valgte aktive extras ændrer kun API1.39.1→1.45.1
og fjerner de to nu ubrugte transitiver importlib-metadata/zipp. Kandidaten
bevarer Pillow13-rettelsen, browser-harness-wheelen og alle øvrige pakker.
Et separat PM-testmiljø indeholder også de valgfrie mistral/otlp-extras.

Lokal regression: den gamle1.39.1-parser bruger6,808s på80KB ugyldigt input.
20centrale tests består efter ændringen: bounded parser, gyldige værdier,
Mistrals rigtige klient/audio-metoder, eksisterende OTLP-/redaktionskontroller
og Mistral tool-IDs. Ingen provider- eller live exploit-kald. En separat
TTS-suite giver11PASS/1FAIL både før og efter: den eksisterende test
`test_mistral_key_missing_returns_false` afspejler ikke den aktuelle generelle
TTS-provideropdagelse. Den ændres ikke her. CLI-setup-testene kan ikke afvikles
med husets-pytest-pluginargumenter, der fejlfortolkes som Hermes-profilen
kpa_testvagt. Det er et testopsætningsproblem, ikke en grøn kontrol.
`scripts/check --staged --base HEAD`:12checksOK,0blocking/0advisory.

Udrulning: publicér koden i KPA-forken, fast-forward den aktive installation,
lad PM lave en ny generation med de eksisterende extras og plugins, og
verificér den realiserede pakkeforskel før genstart af gateway/teksttjenesten.
Kontrollér de faktiske PID'er/interpretere, konfigurationsaftryk og platforme.
Ingen testbesked, testagent, tools-kald eller ændring af samtykkeindstillinger.
Anna må få pakken, men dens gateway må ikke startes.

Primær kilde:
https://github.com/open-telemetry/opentelemetry-python/security/advisories/GHSA-xcq7-p3pf-p88h
Privat evidens: ~/.local/share/kpa-qa/fejlcenter-20261023-110900/hermes-*.json
