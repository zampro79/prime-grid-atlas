# Prime Grid Atlas v1.0.0 — Manuale software

## 1. Scopo

Prime Grid Atlas è un ambiente interattivo per esplorare embedding modulari, maschere di primalità e strutture coprime. La build `1.0.0`, prima versione ufficiale, usa:

- PySide6 per l'interfaccia a tab;
- NumPy come backend numerico obbligatorio;
- CuPy/CUDA come backend GPU opzionale;
- PyQtGraph/OpenGL per la vista 3D;
- Matplotlib per gli export scientifici.

Il programma è uno strumento di matematica sperimentale. Non genera numeri primi e non dimostra nuove leggi sulla loro distribuzione.

## 2. Installazione

Requisiti principali:

```bash
python -m pip install -r requirements.txt
```

Backend NVIDIA CUDA 12 opzionale:

```bash
python -m pip install --upgrade -r requirements-gpu-cuda12.txt
```

Avvio:

```bash
python -B main.py
```

Verifica CuPy:

```bash
python -c "import cupy as cp; a=cp.arange(1000); print(cp.sqrt(a).sum()); print(cp.fft.fft(a).shape)"
```

Se CUDA non è disponibile, il programma continua automaticamente con NumPy.

## 3. Struttura dell'interfaccia

L'applicazione usa una sola finestra con tab permanenti o create quando necessarie:

- **Grid**: configurazione e visualizzazione principale;
- **Module scan**: scansione atlas asincrona;
- **FFT / Heatmap**: heatmap prodotte da Module scan; la FFT corrente è integrata nella Grid;
- **3D**: visualizzazione OpenGL;
- **Configuration**: parametri applicativi e scientifici persistenti.

## 4. Configurazione della griglia

### Dimensioni

I controlli `X`, `Y` e `Z` definiscono il volume discreto. Con placement `Linear`:

\[
n(x,y,z)=s+zXY+yX+x,
\]

dove `Start` corrisponde a \(s\).

`Lock aspect ratio` mantiene le proporzioni correnti quando una dimensione viene modificata.

### Preset

Sono disponibili configurazioni rapide:

- `71×30×30`;
- `37×32×30`;
- Prime overlay;
- Entropy;
- Twin primes;
- Residues mod N.

### Modi

Il controllo `Mode group` separa le funzioni in tre insiemi metodologici.

#### Prime research

- `Primes`, `Twin primes`, `Sophie Germain primes` e `Safe primes`.

#### Scientific controls

- `Coprimes with N`, `Square-free numbers`, `Semiprimes` e `Prime powers`.

#### Modular diagnostics

- `Multiples of k`, `Residues modulo N`, `Divisor count τ(n)`,
  `Möbius μ(n)` e `GCD with N`.

`Parameter` rappresenta \(k\) o il modulo N ed è abilitato soltanto per le
modalità che lo richiedono.

Convenzioni implementative:

- `Semiprimes` richiede due fattori primi contando la molteplicità, quindi include \(p^2\);
- `Prime powers` include anche i primi, corrispondenti all'esponente 1;
- `Twin primes` seleziona il membro inferiore \(p\) quando anche \(p+2\) è primo;
- `Sophie Germain primes` richiede che \(p\) e \(2p+1\) siano primi;
- `Safe primes` richiede che \(p\) e \((p-1)/2\) siano primi.

I campi aritmetici non sono ridotti a maschere binarie:

- `Residues modulo N` calcola per ogni cella il campo scalare \(n \bmod N\);
- `Divisor count τ(n)` colora il numero totale di divisori positivi;
- `Möbius μ(n)` usa rosso per −1, grigio per 0 e blu per +1;
- `GCD with N` colora il valore di \(\gcd(n,N)\);
- `Coprimes with N` seleziona invece soltanto le celle con \(\gcd(n,N)=1\).

La FFT di residui, τ, μ e GCD opera sul campo scalare centrato. Le altre modalità
continuano a usare lo spettro binario presenza/assenza, preservando la
definizione storica della v160.

Le modalità che richiedono fattorizzazione o iterazioni sulle cifre sono più
costose della maschera dei primi. Per esplorazioni interattive conviene iniziare
con volumi moderati e aumentare le dimensioni dopo aver verificato i tempi.

### Placement

- `Linear`: conserva le progressioni aritmetiche modulari e la teoria delle
  colonne modulo \(XY\).
- `Spiral inward`: su ogni piano XY parte dall'angolo superiore sinistro,
  percorre il bordo in senso orario e procede verso il centro. Il piano Z
  successivo riparte dal bordo e continua la numerazione.
- `Spiral outward (Ulam)`: parte dal centro e cresce a spirale; sulle dimensioni
  pari usa la cella centrale superiore-sinistra come origine convenzionale.
- `Boustrophedon`: alterna righe sinistra→destra e destra→sinistra.
- `Hilbert curve`: usa una curva di Hilbert su un quadrato virtuale di lato
  potenza di due e ritaglia le coordinate esterne alla griglia.
- `Morton Z-order`: visita ricorsivamente blocchi usando l'interlacciamento dei
  bit delle coordinate.
- `Diagonal zigzag`: attraversa le diagonali alternandone la direzione.
- `Corner expanding rings`: parte in alto a sinistra e aggiunge gusci
  rettangolari progressivi.
- `Concentric rings`: percorre i bordi dall'esterno al centro alternando il
  verso tra anelli consecutivi.
- `Radial spokes`: raggruppa le celle per raggio angolare e procede dal centro
  verso l'esterno lungo ciascun raggio.
- `Prime modulus weave`: raggruppa gli interi per classe `n mod N`, usando come
  N `Placement parameter / seed`.
- `Seeded random`: applica una permutazione pseudocasuale riproducibile; il seed
  è impostato con `Placement parameter / seed` e viene combinato con X e Y.
- `Bit reversal`: ordina gli indici in base all'inversione dei loro bit.
- `3D helix`: usa la spirale interna e ne ruota l'orientamento tra livelli Z;
  sulle griglie rettangolari usa riflessioni equivalenti che preservano la forma.

I placement non lineari sono esperimenti geometrici distinti. L'accumulo
ortogonale rimane disponibile su XY, XZ e YZ e somma geometricamente le celle
lungo l'asse scelto. I placement planari fissi conservano il passo XY lungo Z, ma non in generale
i passi lungo X/Y; 3D helix varia anche l’orientamento tra layer: le metriche modulari rapide non vengono mostrate e Module
scan continua a usare esclusivamente `Linear`.

### Confronto dei placement

Il comando `Compare placements` apre una tab che ricalcola la configurazione
corrente con tutti i placement. `Linear` è marcato `Protocol-valid`; gli altri
sono marcati `Exploratory`. Il confronto usa soltanto quantità geometriche
compatibili fra embedding: densità, entropia locale e globale, densità dei
bordi e quattro metriche FFT. `distance_from_linear` è la distanza euclidea
non standardizzata fra queste otto metriche e va letta come indicatore
descrittivo, non come significatività statistica.

Il calcolo procede un placement per volta, mostra l'avanzamento e può essere
annullato. `Export CSV` salva la tabella e un sidecar `.config.json` contenente
versione, dimensioni, modalità, parametri, Start, piano, livello, accumulo e
configurazione scientifica.

## 5. Proiezioni e navigazione

- `XY`: profondità lungo Z e passo modulare \(XY\);
- `XZ`: profondità lungo Y e passo X;
- `YZ`: profondità lungo X e passo 1.

Le matrici seguono sempre la convenzione `(righe, colonne)`: XY=`(Y,X)`,
XZ=`(Z,X)` e YZ=`(Z,Y)`.

Controlli:

- rotellina: zoom;
- `Shift+rotellina`: cambia livello;
- trascinamento: pan della griglia;
- frecce accanto al livello: livello precedente/successivo;
- `Reset view`: adatta nuovamente la griglia alla tab.

`Accumulate 0..k` sovrappone tutti i livelli dall'origine alla profondità selezionata.

## 6. Viste 2D

- `Classic`;
- `Heatmap`;
- `Normalized heatmap`;
- `Gradient`;
- `Local entropy`;
- `Entropy edges only`;
- `FFT 2D`.

`Numbers` e `Grid` controllano gli overlay vettoriali. Le etichette numeriche vengono create fino al limite `Maximum text labels` (12.000 per default) per evitare un numero eccessivo di oggetti grafici.

## 7. Backend CPU/GPU

### Auto

Usa la GPU oltre la soglia `Auto GPU threshold` (65.536 elementi per default) e la CPU per matrici più piccole.
È la modalità raccomandata nell'uso normale: evita il costo dei trasferimenti e
dei kernel CUDA quando il carico è troppo piccolo per compensarlo.

### CPU

Forza NumPy. Serve per confronti prestazionali, riproducibilità, diagnostica e
per lavorare quando la memoria della GPU è impegnata da altri processi.

### GPU

Forza CuPy quando CUDA è operativo. Sono accelerati:

- crivello principale e lookup della maschera dei primi;
- FFT 2D;
- gradienti;
- entropia locale;
- maschere GCD/coprime;
- componenti matriciali dello scan atlas.

Il piccolo elenco dei primi base fino a \(\sqrt N\), la GUI, i CSV e la costruzione delle tabelle rimangono sulla CPU.

La selezione GPU è un override, non una promessa di maggiore velocità. Nel
Module scan i piani possono essere piccoli e cambiare dimensione continuamente:
trasferimenti CPU/GPU, lanci dei kernel e creazione dei piani cuFFT possono
rendere la GPU forzata più lenta della CPU. Lo scan rilascia periodicamente i
piani FFT e i blocchi CuPy inutilizzati, e libera le cache al termine, per
evitare che forme FFT diverse mantengano diversi GiB senza lavoro utile.

Il pulsante `GPU diagnostics / setup` mostra lo stato completo del backend.
Il messaggio `CUDA runtime incomplete` indica che il probe CuPy dell'applicazione
non ha completato almeno una fra allocazione, riduzione, padding, FFT o crivello.
Non equivale necessariamente a un driver guasto. La diagnostica esatta va
eseguita dalla directory del progetto e nello stesso ambiente virtuale:

```bash
python -c "import cupy; cupy.show_config()"
python -c "from compute_backend import configure_backend,backend_error; print(configure_backend('GPU')); print(backend_error())"
```

Un runtime CUDA 12.x fornito dal pacchetto `cupy-cuda12x` può funzionare con un
driver che espone una versione CUDA successiva. `CUDA Root: None` e l'assenza di
`nvcc` non sono errori se CuPy trova runtime, header, NVRTC e cuFFT nel virtual
environment.

## 8. FFT

`FFT 2D` è disponibile direttamente in `View type` e usa la stessa area della
griglia. Il pulsante omonimo è una scorciatoia per selezionare questa vista. In
questa modalità numeri e griglia vengono nascosti perché i pixel rappresentano
frequenze, non celle numeriche. Il programma:

1. converte le maschere e gli overlay in presenza/assenza; residui, τ, μ e GCD mantengono invece i valori scalari;
2. sottrae la media;
3. calcola la FFT bidimensionale;
4. usa lo spettro di potenza;
5. rimuove la componente DC.

Metriche:

- peak power ratio;
- axis power ratio;
- low-frequency power ratio;
- spectral entropy normalizzata.

Le metriche principali compaiono nella barra di stato. `Save FFT` esporta lo
spettro in PNG. La trasformata usa CuPy quando il backend GPU selezionato è
attivo e supera la soglia configurata, con fallback NumPy.

## 9. Vista 3D

La tab 3D usa OpenGL. Opzioni e controlli:

- `3D selected only`: mostra soltanto i punti selezionati;
- `3D geometry`: seleziona `Cartesian grid`, `Spherical shells` oppure
  `Rotating spherical shells`;
- `Inner shell radius`: raggio del livello Z=0;
- `Shell spacing`: incremento radiale fra due livelli Z consecutivi;
- `Shell rotation`: rotazione longitudinale aggiunta a ogni livello nella
  geometria sferica rotante;
- trascinamento sinistro: rotazione;
- trascinamento centrale/destro: pan;
- rotellina: zoom;
- `Reset`, `Top`, `Front`, `Side`: camera;
- `Observer 0,0,0`: colloca la camera nell'origine, all'interno dei gusci,
  orientandola verso la sfera esterna;
- frecce e `Z±`: navigazione;
- `Zoom ±`: controllo preciso.

La finestra grafica è persistente: generazioni successive aggiornano lo stesso contesto OpenGL.

La vista interna mostra la volta dei primi dal centro dell'atlante. `Reset` e le
viste ortogonali riportano la camera all'esterno. Premendo nuovamente
`Observer 0,0,0` si ripristina esattamente il punto di osservazione centrale.

Nelle geometrie sferiche X rappresenta la longitudine, Y usa un campionamento
equal-area fra i poli e Z identifica gusci concentrici sempre più esterni. La
trasformazione cambia soltanto il rendering: numeri, primalità, placement e
proiezioni 2D restano invariati. Tre cerchi massimi mostrano il limite del
guscio esterno. Con `Linear 71×30×30`, ogni direzione radiale contiene 30 valori
separati da 2130 e conserva quindi la stessa classe residua modulo 30.

La FFT corrente continua a riferirsi alla mappa rettangolare srotolata; non è
ancora un'analisi in armoniche sferiche.

Per sicurezza la visualizzazione viene campionata al valore `Maximum 3D points` (due milioni per default). Anche la dimensione dei punti è configurabile.

## 10. Module scan

La tab Module scan esplora intervalli di X e Y a Z fissato. Lo scan avviene in un worker separato dalla GUI.
Gli aggiornamenti di avanzamento sono consegnati tramite slot Qt accodati nel
thread principale; la griglia viene temporaneamente congelata per impedire
repaint o cambi di backend concorrenti con il worker.
Se si chiude l'applicazione durante uno scan, viene richiesto l'arresto; la
finestra resta aperta qualora il passo numerico corrente non sia ancora terminato,
evitando di distruggere un thread attivo.

Controlli:

- intervalli X/Y;
- Z fisso;
- numero di baseline;
- backend Auto/CPU/GPU;
- avanzamento e annullamento.

`Trials` indica quante disposizioni casuali di controllo vengono generate per
ogni combinazione X/Y. Ogni trial conserva il numero di celle vive e campiona i
valori positivi osservati, ma ne randomizza le posizioni. Le metriche casuali
salvate sono le medie dei trial. I delta sono calcolati come metrica osservata
meno media casuale; un delta diverso da zero è un segnale esplorativo, non una
prova di significatività statistica.

Il numero indicativo di passaggi completi è:

```text
combinazioni X/Y × (Trials + 2)
```

I due passaggi aggiuntivi sono la griglia osservata e la maschera coprima. La GUI
mostra questo costo prima dell'avvio. Valori di 1–2 trial sono adatti alla prima
esplorazione; 10–20 a un confronto preliminare; valori superiori vanno usati su
un insieme ristretto di candidati. Il tempo cresce approssimativamente in modo
lineare con Trials.

Il numero di combinazioni non ha un limite applicativo: tutti gli intervalli
X/Y richiesti vengono accettati. Scansioni molto estese possono richiedere tempi
e memoria considerevoli; `Cancel` resta sempre disponibile tra un passo
numerico e il successivo.

Lo scan produce 58 campi, comprendenti:

- proprietà del modulo;
- metriche prime;
- baseline casuali;
- delta dalla baseline;
- metriche della maschera coprima;
- delta prime/coprimi;
- residui L1/L2;
- conteggi delle classi.

Sono disponibili:

- export CSV; insieme al CSV viene scritto un file `.config.json` con tutti i parametri e le impostazioni della scansione;
- un unico selettore `Heatmap metric` per tutte le metriche visualizzabili;
- `Show heatmap` per aprire la metrica selezionata;
- `Save screenshot` per esportare in PNG la metrica selezionata;
- `Save all metric screenshots` per esportare con una sola scelta della cartella
  tutti i 22 PNG elencati nel selettore.

Il selettore comprende score strutturali, densità, rapporti coprimi, entropie,
metriche FFT, delta dalle baseline e residui coprimi. Non esistono più pulsanti
di salvataggio separati per ogni tipo di heatmap.

L'esportazione completa usa nomi numerati, da
`01_structural_score.png` a `22_delta_coprime_fft_axis_ratio.png`, e scrive
`metric_screenshots.json`. Il file JSON registra versione dell'applicazione,
nome e chiave di ciascuna metrica, intervalli dello scan, Z, Trials, piano e
configurazione scientifica. Non rigenera lo scan e non esporta una griglia per
ogni coppia X/Y: fotografa le 22 matrici di risultati già calcolate.

Le heatmap interattive ed esportate usano la stessa palette `viridis`, la
stessa normalizzazione lineare min/max della FFT e l'origine Y in basso. Le
combinazioni mancanti, per esempio dopo una scansione annullata, sono grigie e
non partecipano alla normalizzazione.

## 11. Configuration

La tab applica i parametri senza riavviare il programma. `Reset defaults`
ripristina i valori numerici validati nella v170; `Load JSON` e `Save JSON`
caricano e salvano profili. Se nella directory dell'applicazione esiste
`prime_atlas_config.json`, viene caricato automaticamente all'avvio.

I parametri sono divisi logicamente in:

- calcolo: soglia Auto GPU, volume massimo, baseline predefinite e seed (`-1` usa il seed deterministico derivato dall'esperimento);
- metriche: bin dell'entropia, soglia edge, raggio FFT a bassa frequenza e coefficienti del beauty score;
- rendering: limite delle etichette, punti e dimensione punti 3D, ritardo di redraw e lato massimo dei PNG batch.

Cambiare un parametro scientifico cambia legittimamente le immagini analitiche e
gli score. Per confrontare due scansioni occorre usare lo stesso profilo JSON.
Durante una scansione la tab viene disabilitata, così una singola serie non può
contenere righe calcolate con profili differenti.

## 12. Definizioni implementative delle metriche

### Entropia locale

- finestra 3×3;
- padding dei bordi per replica;
- numero di bin configurabile (8 per default);
- quantizzazione rispetto al minimo/massimo del campo;
- logaritmo in base 2.

### Edge density

La soglia è:

\[
T=H_{min}+r(H_{max}-H_{min}),
\]

con `r=0.72` per default.

### Global entropy

È l'entropia della distribuzione dei valori di hit, non una misura diretta della loro disposizione spaziale.

### Beauty score

Score euristico interno; la formula seguente mostra i valori predefiniti, mentre
i coefficienti sono modificabili nella tab Configuration:

\[
B=\max(0,R_c-R_n)
(1+0.35H_{loc}+0.65E)
e^{-18(\rho-0.27)^2}.
\]

Non è un invariante matematico né una misura statistica di significatività.

### Structural score

\[
S=B_{obs}-\overline{B}_{random}.
\]

## 13. Limitazioni

- Le baseline correnti sono esplorative e predefinite a 12 trial.
- Non vengono ancora prodotti automaticamente intervalli di confidenza e p-value.
- I residui L1/L2 combinano metriche non standardizzate.
- L'analisi coprima su YZ è degenere perché il passo è 1.
- La formula di Linear è fissa; Start, dimensioni e placement sono configurabili.
- Il rendering GPU 3D e il calcolo CUDA sono backend distinti.

Per il protocollo scientifico e le modifiche previste consultare [research_protocol.md](research_protocol.md).

## 14. Moduli principali

```text
main.py             entry point
qt_app.py           interfaccia PySide6
app_config.py       configurazione validata e serializzazione JSON
atlas_engine.py     motore headless e scan
compute_backend.py  selezione NumPy/CuPy e crivello GPU
metrics.py          metriche geometriche e spettrali
mode_catalog.py     gruppi Prime/Controls/Diagnostics
grid_model.py       embedding e proiezioni
number_theory.py    funzioni aritmetiche CPU
```

La distribuzione v1.0.0 contiene soltanto moduli appartenenti alla pipeline attiva.
Il materiale teorico precedente non è stato eliminato: è conservato in
[`archive/`](archive/README.md) e indicizzato da [`README.md`](README.md). I
paper storici devono essere letti con le limitazioni dichiarate nell'indice
dell'archivio.
