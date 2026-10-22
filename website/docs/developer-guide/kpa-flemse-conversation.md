# Flemse: naturlig samtale i Slack

29-09-2026. Modelvalg: behold `gpt-5.6-sol`, `openai-codex` og eksisterende
reasoning-indstilling. Tonen og statusvisningen ændres; systemadgang og
logningsprojektet er separate opgaver. Promptens afvisning af systembygning
er ikke en teknisk adgangsspærre.

Den hemmelighedsfrie opskrift står i `kpa-flemse-conversation.yaml`:

- Flet kun de viste Slack-nøgler ind i profilens konfiguration.
- Tilføj `slack_system_prompt` til `agent.system_prompt` én gang. Afsnittet
  gælder udtrykkeligt kun Slack; eksisterende tekniske opslagsregler bevares.
- Bevar model, øvrige platforme, credentials, værktøjer og adgangsregler.
- Tag en privat backup af konfigurationen og validér YAML før atomisk byt.
- Indlæs Python-ændringen med gatewayens normale drænende reload.

## Adfærd

Et hurtigt svar kommer direkte. Er agenten stadig i gang efter fem
sekunder, sender gatewayen en kort dansk kvittering. Derefter opdateres
samme statusbesked hver 60. sekund, så chatten ikke fyldes med gentagelser.
Kvitteringen ophører, når arbejdet slutter eller samtalen overtages af
en anden agenttur. Tekniske værktøjsmeldinger og reasoning vises ikke.
Opfølgende beskeder får en kort dansk kvittering uden kommandovejledning.

`display.platforms.<platform>.long_running_interval` overstyrer den
globale statusfrekvens; <= 0 slår den fra.
`long_running_initial_delay` vælger første ventetid. Uden disse nøgler
bevares den eksisterende globale frekvens (normalt 180 sekunder).
Ved tidligere første besked og `long_running_notifications: generic`
bruges `status_phrases.generic` først og `status_phrases.status` bagefter.
`busy_ack_text` erstatter den tekniske kvittering for en besked under
igangværende arbejde. Det ændrer ikke håndteringen af selve beskeden.

## Kontrol

Isolerede tests dækker første kvittering, opdatering af samme besked,
afsluttet arbejde uden forsinkede kvitteringer, ingen rå argumenter i
status og uændret timing på en platform uden overstyring. Busy-kvitteringen
testes ved styring, kø og afbrydelse. Ingen rigtig Slack-besked eller
produktions-AI-tur bruges som test.

Kør `scripts/run_tests.sh tests/gateway/test_conversational_status.py
tests/gateway/test_display_config.py tests/gateway/test_status_phrases.py
tests/gateway/test_busy_session_ack.py --file-retries 0 -q`.

Officielt modelgrundlag:
https://developers.openai.com/api/docs/models/gpt-5.6-sol
https://developers.openai.com/api/docs/guides/model-selection
Et andet modelvalg bør afgøres med repræsentative KPA-opgaver, ikke kun
en vurdering af samtaletonen.
