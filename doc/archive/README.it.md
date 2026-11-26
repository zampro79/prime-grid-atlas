# Archivio documentazione storica

Questa directory locale conserva le versioni precedenti del paper. I file dei
paper sono esclusi dal commit pubblico v1.0.0 finché attribuzione e diritti di
redistribuzione non saranno confermati. Le copie locali restano integre e non
descrivono in modo autorevole la versione v1.0.0.

## Contenuto

- `complete_paper_v1.md`: sorgente Markdown del primo paper completo;
- `complete_paper_v1.pdf`: esportazione PDF della stessa fase;
- `complete_paper_v1.docx`: esportazione Word della stessa fase;
- `revised_paper_v3.pdf`: revisione successiva, precedente al protocollo v170.

## Limitazioni note

Questi documenti:

- descrivono ancora l'interfaccia Tkinter;
- non includono il backend GPU completo;
- non formalizzano il parametro `start`;
- non distinguono adeguatamente piano XY e placement lineare;
- non specificano tutte le metriche implementate;
- contengono affermazioni sperimentali non ancora supportate da intervalli statistici;
- non costituiscono il paper corrente del progetto.

I riferimenti attivi della v1.0.0 sono:

- [`../README.md`](../README.md);
- [`../software_manual.md`](../software_manual.md);
- [`../research_protocol.md`](../research_protocol.md).

Un nuovo paper dovrà essere generato soltanto dopo l'esecuzione dello studio confermativo definito nel protocollo di ricerca.

## Verifica prima della pubblicazione

I PDF riportano metadati Author «ChatGPT Canvas» e Creator «ChatGPT»; non
identificano l'autore umano. Il proprietario deve confermare attribuzione e
diritti; per questo i file non vengono pubblicati. Nel paper v1 l'entropia globale viene interpretata come dispersione
spaziale e la baseline come conservazione esatta degli hit: queste descrizioni
non corrispondono alle metriche attuali. Le affermazioni di significatività
empirica non sono validate dai test software. Gli originali restano invariati.
