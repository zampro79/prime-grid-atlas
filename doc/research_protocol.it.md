# Famiglie spettrali degli embedding modulari \(p\times 30\)

> **Stato di implementazione:** questo documento contiene anche un piano futuro.
> Permutazioni esatte degli hit, null prime-like, Moran's I, intervalli,
> p-value e correzioni multiple non sono implementati nella release.
> [RESEARCH.md](../RESEARCH.md) documenta ciò che il codice calcola realmente.

## Documento di lavoro per lo sviluppo teorico e sperimentale

**Progetto:** Prime Grid Atlas

**Versione software di riferimento:** v1.0.0 PySide6/GPU
**Stato:** bozza di ricerca

**Data:** 30 luglio 2026

---

## 1. Obiettivo

Questo documento sviluppa un programma di ricerca sulle configurazioni

\[
X=p,\qquad Y=30,\qquad Z\ge 1,
\]

dove \(p>5\) è primo. Il modulo associato alla proiezione XY è

\[
M=30p=2\cdot3\cdot5\cdot p.
\]

L'obiettivo non è formulare nuove leggi sulla distribuzione dei primi, ma studiare in modo quantitativo:

1. la geometria della maschera delle classi coprime modulo \(30p\);
2. la struttura spettrale indotta dall'embedding rettangolare \(p\times30\);
3. il modo in cui gli overlay finiti dei primi ereditano tale struttura;
4. l'eventuale presenza di un residuo non spiegato dalla sola geometria coprima;
5. la dipendenza delle geometrie dalla classe \(p\bmod30\).

Il caso \(p=71\), per cui

\[
71\equiv11\pmod{30},
\]

costituisce il punto di partenza empirico, non il risultato da dimostrare.

---

## 2. Dominio dell'analisi

Le affermazioni teoriche di questo documento valgono per:

- embedding lineare della v1.0.0 per gli esperimenti del protocollo;
- proiezione **XY**;
- valore iniziale esplicitamente dichiarato;
- embedding

\[
n_s(x,y,z)=s+zXY+yX+x,
\]

con

\[
0\le x<X,\qquad 0\le y<Y,\qquad 0\le z<Z.
\]

Nel caso principale:

\[
X=p,\qquad Y=30,
\]

e quindi

\[
n_s(x,y,z)=s+30pz+py+x.
\]

La v1.0.0 presenta anche tredici placement esplorativi; l'embedding `Linear`
resta obbligatorio per il protocollo perché conserva le progressioni
aritmetiche verticali.

Le proiezioni XZ e YZ possono essere studiate come controlli, ma non rappresentano lo stesso sistema di classi residue modulo \(30p\).

Nella v1.0.0 i gruppi `Prime research`, `Scientific controls` e
`Modular diagnostics` costituiscono il catalogo ammesso per il lavoro
principale. Le sequenze esplorative generiche della v180 possono suggerire
confronti o controlli aggiuntivi, ma un loro pattern visuale non entra nel
protocollo senza una nuova ipotesi esplicita, una baseline e un criterio di
falsificazione definiti prima dell'analisi.

---

## 3. Definizioni fondamentali

### 3.1 Residuo associato a una cella

Per una cella \((x,y)\) del piano XY definiamo

\[
r_s(x,y)=s+py+x.
\]

La colonna verticale corrispondente contiene

\[
n_k=r_s(x,y)+30pk,
\qquad 0\le k<Z.
\]

### 3.2 Maschera coprima

Definiamo

\[
C_{p,s}(x,y)=
\mathbf 1_{\gcd(r_s(x,y),30p)=1}.
\]

Questa è la geometria deterministica delle classi residue potenzialmente fertili.

### 3.3 Maschera binaria dei primi a profondità \(Z\)

Definiamo

\[
A_{p,s,Z}(x,y)=
\mathbf 1_{\exists\,0\le k<Z:\ r_s(x,y)+30pk\text{ è primo}}.
\]

Questa maschera registra se una colonna contiene almeno un primo entro la profondità osservata.

### 3.4 Campo degli hit

Definiamo anche il conteggio

\[
H_{p,s,Z}(x,y)=
\sum_{k=0}^{Z-1}
\mathbf 1_{\mathbb P}(r_s(x,y)+30pk).
\]

È necessario distinguere sempre:

- la maschera binaria \(A\);
- il campo dei conteggi \(H\);
- la maschera coprima \(C\).

Le tre quantità non sono intercambiabili.

### 3.5 Spettro di potenza

Per un campo bidimensionale \(U\), sottratta la media, definiamo

\[
\widetilde U=U-\langle U\rangle
\]

e

\[
P_U(k_x,k_y)=|\mathcal F_2(\widetilde U)|^2.
\]

Per confronti tra dimensioni differenti si usa lo spettro normalizzato

\[
\widehat P_U=
\frac{P_U}{\sum_{k_x,k_y}P_U(k_x,k_y)}.
\]

---

## 4. Risultati noti e conseguenze immediate

Questa sezione non contiene congetture nuove.

### 4.1 Sterilità delle classi non coprime

Se

\[
d=\gcd(r_s(x,y),30p)>1,
\]

allora ogni termine della colonna è divisibile per \(d\). La colonna può contenere al massimo il primo eccezionale \(d\), se questo compare nell'intervallo osservato.

### 4.2 Convergenza binaria per modulo fissato

Per ogni classe \(r\) coprima con \(30p\), il teorema di Dirichlet garantisce infiniti primi nella progressione

\[
r+30pk.
\]

Poiché le classi ridotte sono in numero finito, per ogni \(p\) e \(s\) fissati esiste una profondità finita \(Z_0(p,s)\) oltre la quale tutte le classi coprime sono state attivate almeno una volta.

Di conseguenza, salvo i primi eccezionali nelle classi non coprime,

\[
A_{p,s,Z}\longrightarrow C_{p,s}
\]

per \(Z\to\infty\).

La convergenza qualitativa non è quindi una congettura. Sono invece problemi sperimentali e teorici:

- la velocità di convergenza;
- la dipendenza uniforme da \(p\);
- il comportamento quando \(p\) e \(Z\) crescono insieme;
- la convergenza delle metriche e degli spettri normalizzati.

### 4.3 Densità coprima

Per \(p>5\):

\[
\frac{\varphi(30p)}{30p}
=
\left(1-\frac12\right)
\left(1-\frac13\right)
\left(1-\frac15\right)
\left(1-\frac1p\right)
=\frac4{15}\left(1-\frac1p\right).
\]

Per \(p=71\):

\[
\frac{\varphi(2130)}{2130}
=\frac{560}{2130}
\approx0.26291.
\]

### 4.4 Azione della classe \(p\bmod30\)

La maschera soddisfa simultaneamente

\[
r_s(x,y)\equiv s+x\pmod p
\]

e

\[
r_s(x,y)\equiv s+x+(p\bmod30)y\pmod{30}.
\]

La parte modulo \(p\) produce un'esclusione allineata lungo X, mentre la ruota modulo 30 viene traslata da una riga alla successiva di

\[
a=p\bmod30.
\]

Poiché \(p>5\), si ha

\[
a\in(\mathbb Z/30\mathbb Z)^\times
=\{1,7,11,13,17,19,23,29\}.
\]

Le 30 righe attraversano quindi un'orbita completa delle traslazioni modulo 30.

---

## 5. Congettura A — Otto famiglie spettrali

### Enunciato qualitativo

Le geometrie coprime \(p\times30\), dopo normalizzazione dell'asse X, si organizzano in otto famiglie spettrali determinate dalla classe

\[
p\bmod30.
\]

### Forma quantitativa preliminare

Siano \(p\) e \(q\) primi maggiori di 5 con

\[
p\equiv q\pmod{30}.
\]

Sia \(\mathcal R\) un operatore dichiarato di ricampionamento dello spettro su una griglia comune. Si congettura che

\[
d_{\mathrm{spec}}(p,q)
=
\left\|
\mathcal R(\widehat P_{C_{p,s}})
-
\mathcal R(\widehat P_{C_{q,s}})
\right\|_2
\]

sia, in media, minore della distanza tra primi appartenenti a classi differenti modulo 30.

Una versione asintotica più forte sarebbe

\[
d_{\mathrm{spec}}(p,q)\to0
\]

per \(p,q\to\infty\) nella stessa classe, ma questa formulazione richiede un operatore di normalizzazione geometrica rigoroso.

### Predizione per 71

Poiché

\[
71\equiv11\pmod{30},
\]

la configurazione \(71\times30\) dovrebbe risultare più simile a

\[
41\times30,\quad101\times30,\quad131\times30,\quad191\times30
\]

che a configurazioni di dimensione confrontabile appartenenti ad altre classi modulo 30.

### Criterio di falsificazione

La congettura viene indebolita o respinta se un classificatore addestrato esclusivamente sugli spettri delle maschere coprime non distingue le otto classi meglio del caso su un insieme di test separato.

---

## 6. Congettura B — Ereditarietà spettrale degli overlay primi

### Enunciato

Le principali strutture spettrali dell'overlay binario dei primi convergono alle strutture della corrispondente maschera coprima all'aumentare di \(Z\).

Definiamo

\[
\rho(p,s,Z)=
\operatorname{corr}
\left(
\widehat P_{A_{p,s,Z}},
\widehat P_{C_{p,s}}
\right).
\]

Si propone di verificare se

\[
\rho(p,s,Z)\to1
\]

e con quale velocità.

### Parte non banale

Per \(p\) fissato, la convergenza binaria finale segue da Dirichlet. L'oggetto interessante è una legge di scala uniforme, per esempio nel regime

\[
p\to\infty,
\qquad
Z=Z(p)\to\infty.
\]

Non si assume in anticipo una forma come \(1/\log Z\). Le leggi candidate devono essere confrontate tramite validazione fuori campione.

### Criterio di falsificazione

La congettura spettrale forte viene respinta se, anche dopo l'attivazione di quasi tutte le classi coprime, la correlazione spettrale non cresce o mostra dipendenze irregolari incompatibili con la densità delle celle non ancora attivate.

---

## 7. Congettura C — Equivalenza geometrica entro la stessa classe

### Enunciato

Sia \(G\) un vettore di osservabili standardizzate, comprendente almeno:

- FFT peak ratio;
- FFT axis ratio;
- low-frequency ratio;
- spectral entropy;
- autocorrelazione lungo X e Y;
- orientazione dei massimi spettrali;
- entropia locale media;
- edge density.

Per primi \(p,q\) nella stessa classe modulo 30, si congettura che

\[
d_G(p,q)
=
\left\|
\widetilde G(C_{p,s})-
\widetilde G(C_{q,s})
\right\|_2
\]

sia sistematicamente minore della distanza tra classi differenti.

Le componenti devono essere standardizzate su un insieme di addestramento:

\[
\widetilde G_i=
\frac{G_i-\mu_i}{\sigma_i}.
\]

### Test consigliato

Usare classificazione a otto classi con:

- split train/test per intervalli disgiunti di \(p\);
- nearest centroid come modello interpretabile;
- matrice di confusione;
- accuratezza bilanciata;
- test di permutazione delle etichette.

---

## 8. Congettura D — Estremalità dell'orientamento

### Domanda

A modulo fissato

\[
M=30p,
\]

la geometria dipende dalla fattorizzazione rettangolare

\[
M=XY.
\]

### Enunciato preliminare

Le orientazioni

\[
(X,Y)=(p,30)
\qquad\text{e}\qquad
(30,p)
\]

sono candidate a estremizzare misure di anisotropia rispetto alle altre fattorizzazioni di \(30p\), ma lungo direzioni differenti.

Una forma testabile è

\[
R_{\mathrm{axis}}(p,30)
\ge
R_{\mathrm{axis}}(X,Y)
\]

per le altre coppie \((X,Y)\) con \(XY=30p\), oppure una variante basata sull'autovalore principale del tensore spettrale.

### Controllo essenziale

Il confronto non deve confondere anisotropia aritmetica e rapporto d'aspetto. Tutte le matrici devono essere:

- ricampionate su una griglia comune;
- confrontate anche con maschere casuali dello stesso rapporto d'aspetto;
- analizzate tramite metriche corrette per la forma rettangolare.

---

## 9. Congettura E — Assenza o persistenza del residuo primo-specifico

Questa è la domanda centrale del progetto.

### Ipotesi nulla

Dopo aver controllato:

- maschera coprima;
- densità delle celle vive;
- distribuzione esatta degli hit;
- dimensioni della matrice;
- profondità \(Z\);

il residuo geometrico specifico dei primi tende a zero:

\[
D(p,s,Z)	o0.
\]

### Definizione proposta

Sia \(G\) il vettore delle metriche e siano \(\mu_0,\Sigma_0\) media e covarianza stimate da un ensemble nullo. Si definisce la distanza di Mahalanobis

\[
D^2=
(G_{\mathrm{prime}}-G_{\mathrm{coprime}})^T
\Sigma_0^{-1}
(G_{\mathrm{prime}}-G_{\mathrm{coprime}}).
\]

Questa formulazione sostituisce la somma L1/L2 di metriche non normalizzate.

### Due esiti scientificamente validi

1. **Residuo compatibile con il nullo.** La geometria osservata è spiegata quasi interamente dalle classi coprime e dagli effetti di occupazione.
2. **Residuo persistente.** Alcune componenti prime-specifiche rimangono fuori dall'ensemble nullo e richiedono un modello più preciso.

Nessuno dei due esiti deve essere considerato un fallimento.

---

## 10. Disegno sperimentale

### 10.1 Insieme dei primi

Costruire otto gruppi bilanciati:

\[
\mathcal P_a=
\{p\text{ primo}:p\equiv a\pmod{30}\},
\]

con

\[
a\in\{1,7,11,13,17,19,23,29\}.
\]

Usare almeno:

- 30 primi per classe per analisi esplorativa;
- 100 primi per classe per analisi confermativa;
- intervalli di grandezza comparabili tra le classi.

### 10.2 Profondità

Usare una scala logaritmica, per esempio:

\[
Z\in\{1,2,4,8,16,32,64,128,256,512,1024\}.
\]

Per ogni configurazione registrare sia \(A\) sia \(H\).

### 10.3 Valori iniziali

L'esperimento principale deve fissare

\[
s=1.
\]

Esperimenti secondari possono usare più valori di \(s\), dichiarandoli come test di traslazione e robustezza.

### 10.4 Baseline

Usare almeno tre modelli nulli:

1. **Permutazione spaziale esatta:** permuta tutte le celle conservando esattamente i valori degli hit.
2. **Maschera coprima randomizzata:** conserva il numero di classi coprime ma ne randomizza le posizioni.
3. **Modello prime-like:** probabilità dipendente da \(n\) e condizionata alla coprimalità, ispirata a un modello di Cramér corretto per la ruota.

Per analisi preliminari usare almeno 200 repliche; per risultati finali almeno 1.000 repliche per configurazione o una strategia adattiva basata sulla precisione dell'intervallo.

### 10.5 Separazione esplorativa/confermativa

- Le metriche e le soglie si scelgono sull'insieme esplorativo.
- Le ipotesi vengono registrate prima dell'analisi confermativa.
- I primi dell'insieme confermativo non devono essere usati per tarare score o visualizzazioni.

---

## 11. Metriche da registrare

### 11.1 Metriche di occupazione

- alive density;
- coprime alive ratio;
- non-coprime alive ratio;
- frazione di classi coprime non ancora attivate;
- media e varianza degli hit sulle classi coprime.

### 11.2 Metriche spaziali

- Moran's I o altra autocorrelazione spaziale dichiarata;
- autocorrelazione lungo X e Y;
- entropia locale con finestra e bin esplicitati;
- edge density con soglia preregistrata;
- connected-component statistics.

### 11.3 Metriche spettrali

- peak power ratio;
- axis power ratio;
- low-frequency power ratio;
- spectral entropy normalizzata;
- orientazione del massimo non DC;
- tensore del secondo momento spettrale;
- correlazione tra spettro prime e spettro coprimo.

### 11.4 Metriche di distanza

- distanza L2 dopo standardizzazione;
- distanza di Mahalanobis;
- Jensen-Shannon divergence tra spettri normalizzati;
- earth mover's distance spettrale, se computazionalmente sostenibile.

---

## 12. Analisi statistica

Per ogni metrica \(T\), calcolare rispetto alla baseline:

\[
z_T=
\frac{T_{\mathrm{obs}}-\mu_T}{\sigma_T}.
\]

Riportare:

- media;
- deviazione standard;
- intervallo di confidenza;
- quantili 2.5%, 50%, 97.5%;
- p-value empirico;
- correzione per confronti multipli;
- effect size.

Per le otto famiglie modulo 30 usare:

- ANOVA o alternativa non parametrica;
- modello con \(\log p\), classe modulo 30 e \(\log Z\);
- interazione classe × profondità;
- validazione su primi non usati in fase esplorativa.

Non usare il termine “significativo” senza una procedura statistica dichiarata.

---

## 13. Esperimenti di controllo

### Controllo A — Trasposizione

Confrontare

\[
p\times30
\qquad\text{e}\qquad
30\times p.
\]

### Controllo B — Numeri composti vicini

Confrontare \(p\) con valori composti di dimensione simile, distinguendo:

- coprimi con 30;
- non coprimi con 30;
- quadrati e prodotti di due primi.

### Controllo C — Altre ruote

Ripetere il protocollo con:

\[
6p,\qquad 30p,\qquad 210p.
\]

### Controllo D — Permutazioni geometriche

Applicare trasformazioni che preservano il multinsieme dei valori:

- permutazione delle righe;
- permutazione delle colonne;
- traslazioni cicliche;
- rotazione e trasposizione.

### Vincolo E — Embedding

Tutti gli esperimenti del protocollo v1.0.0 usano l'embedding lineare. I
placement non lineari sono disponibili per confronti geometrici esplorativi,
ma i loro risultati non sono direttamente confrontabili con le metriche lineari
del protocollo.

---

## 14. Output riproducibili

Ogni riga del dataset deve includere almeno:

- versione software e commit;
- seed;
- \(p,X,Y,Z,M\);
- \(p\bmod30\);
- start;
- embedding (`Linear`, valore fisso registrato automaticamente);
- piano e profondità;
- tipo di campo: prime, coprime o baseline;
- numero di trial;
- definizione/versione delle metriche;
- tempi CPU/GPU;
- tutte le metriche osservate;
- media, deviazione standard e quantili delle baseline.

Gli output minimi del progetto dovrebbero essere:

```text
experiments/
├── protocol.yaml
├── primes_by_class.csv
├── raw_metrics.csv
├── baseline_summary.csv
├── spectral_fingerprints.npz
├── figures/
└── logs/
```

---

## 15. Figure necessarie

1. Maschera coprima \(71\times30\).
2. Overlay primi per più valori di \(Z\).
3. FFT affiancate prime/coprime/random.
4. Correlazione spettrale in funzione di \(Z\).
5. Confronto delle otto classi modulo 30.
6. Matrice di confusione del classificatore delle famiglie.
7. Confronto \(p\times30\) contro \(30\times p\).
8. Distribuzione delle baseline e posizione del valore osservato.
9. Residuo standardizzato in funzione di \(p\) e \(Z\).
10. Tempi CPU/GPU e soglia di convenienza della GPU.

---

## 16. Struttura proposta per un paper

1. Introduzione e domanda di ricerca.
2. Definizione dell'embedding con parametro start.
3. Geometria esatta della maschera coprima \(p\times30\).
4. Azione delle classi \(p\bmod30\).
5. Definizione completa delle metriche.
6. Modelli nulli e protocollo statistico.
7. Esperimento sulle otto famiglie.
8. Convergenza in profondità.
9. Confronto prime/coprimi/random.
10. Dipendenza dall'orientamento.
11. Risultati fuori campione.
12. Limitazioni.
13. Conclusioni.

---

## 17. Piano operativo

### Fase 1 — Specifica

- [ ] Congelare le definizioni delle metriche.
- [ ] Correggere la baseline affinché permuti esattamente gli hit.
- [ ] Aggiungere deviazione standard e quantili.
- [ ] Definire il formato del protocollo esperimentale.

### Fase 2 — Motore headless

- [ ] Aggiungere un comando CLI indipendente dalla GUI.
- [x] Salvare seed e configurazione applicativa con ogni CSV tramite sidecar JSON.
- [ ] Aggiungere test CPU/GPU di equivalenza.
- [ ] Aggiungere benchmark automatici.

### Fase 3 — Studio pilota

- [ ] Selezionare 30 primi per ciascuna classe modulo 30.
- [ ] Eseguire la scala preliminare di profondità.
- [ ] Valutare stabilità e ridondanza delle metriche.
- [ ] Stimare il costo delle baseline confermative.

### Fase 4 — Preregistrazione interna

- [ ] Congelare congetture e criteri di falsificazione.
- [ ] Separare train e test.
- [ ] Congelare figure e analisi statistiche previste.

### Fase 5 — Studio confermativo

- [ ] Eseguire almeno 100 primi per classe.
- [ ] Eseguire baseline sufficienti per la precisione richiesta.
- [ ] Generare automaticamente tabelle e figure.
- [ ] Conservare integralmente i risultati negativi.

---

## 18. Interpretazione dei possibili risultati

### Risultato 1 — Otto famiglie chiaramente distinguibili

Questo sosterrebbe l'esistenza di una classificazione geometrico-spettrale dell'embedding determinata dall'azione di \((\mathbb Z/30\mathbb Z)^\times\).

### Risultato 2 — Famiglie visive ma non statisticamente robuste

Le immagini sarebbero principalmente conseguenza di rapporto d'aspetto, ricampionamento o selezione visiva. Il modello dovrebbe essere ridotto.

### Risultato 3 — Residuo prime-specifico nullo

Il risultato mostrerebbe quantitativamente che le strutture osservate sono spiegate dalla geometria coprima e dall'occupazione finita.

### Risultato 4 — Residuo stabile fuori baseline

Il passo successivo sarebbe identificare quali statistiche aritmetiche note non sono rappresentate dal modello nullo, prima di parlare di nuova struttura.

---

## 19. Principio guida

Il progetto non deve cercare conferme visive della configurazione \(71\times30\). Deve tentare attivamente di falsificare l'ipotesi che 71 sia speciale.

Il risultato scientificamente più solido sarà quello che sopravvive a:

- confronto tra classi modulo 30;
- variazione di \(Z\);
- trasposizione della griglia;
- normalizzazione spettrale;
- baseline esatte;
- test fuori campione;
- correzione per confronti multipli.

La domanda finale non è:

> Perché \(71\times30\) produce una bella immagine?

ma:

> Quali componenti della sua geometria sono conseguenze necessarie della ruota modulo 30, quali dipendono dall'embedding e quali, se esistono, rimangono specifiche dell'occupazione dei primi a profondità finita?
