# Mistral TTS: ret en forkert testforudsætning

Den negative Mistral-test valgte ikke `tts.provider=mistral`. Den målte derfor
standardleverandøren Edge, der korrekt var tilgængelig, og krævede fejlagtigt
False. Den forsøgte også at blokere gamle SDK-importører, som den passive
leverandørkontrol ikke længere bruger.

Testen vælger nu Mistral udtrykkeligt og prøver en manglende nøgle både med
og uden installeret Mistral-SDK, mens Edge er tilgængelig. Den positive test
og begge negative tilfælde bekræfter, at kontrollen ikke installerer pakker.
Produktkode, stemmevalg og indstillinger er uændrede.

Husets isolerede runner: før 11 PASS / 1 FAIL; efter 34 PASS på tværs af
Mistral, passive kontroller, leverandørvalg og SDK-importører. Ingen
netkald, talegenerering eller beskeder mod drift. Ingen tjenestegenstart
nødvendig ved denne ændring af tests og dokumentation.
