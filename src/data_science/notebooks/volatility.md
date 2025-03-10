# Volatilitás

Volatility measures how much a stock (or any financial asset) price moves over time.

A **volatilitás** a pénzügyben azt méri, hogy egy pénzügyi eszköz (pl. részvény, deviza) árfolyama mennyire ingadozik az időben.

## Mit jelent a volatilitás?

Egyszerűen megfogalmazva:
- Ha egy részvény árfolyama **sokat változik** rövid idő alatt, akkor nagy a volatilitása (**kockázatosabb**).
- Ha az árfolyam **stabilabb**, kisebb a volatilitás (**kevésbé kockázatos**).

## Hogyan mérjük a volatilitást?

A volatilitást általában a **szórás** (*standard deviation, σ*) alapján számítják.  
Ez matematikailag azt mutatja meg, hogy az eszköz hozamai mennyire térnek el az **átlagos hozamtól**.

### Példa:

Tegyük fel, hogy egy részvény heti záróárai (*Adj Close*) így alakultak:

| Nap        | Záróár (P) |
|------------|-----------|
| Hétfő      | 100 Ft    |
| Kedd       | 105 Ft    |
| Szerda     | 95 Ft     |
| Csütörtök  | 110 Ft    |
| Péntek     | 98 Ft     |

A napi hozamokat az alábbi képlettel számoljuk:

**rₜ = (Pₜ / Pₜ₋₁) - 1**

ahol:  
- *rₜ* a napi hozam,  
- *Pₜ* az aktuális napi záróár,  
- *Pₜ₋₁* az előző napi záróár.  

### Napi hozamok kiszámítása:

| Nap        | Záróár (P) | Napi hozam (rₜ) |
|------------|-----------|----------------|
| Hétfő      | 100 Ft    | -              |
| Kedd       | 105 Ft    | (105/100) - 1 = **5,00%**  |
| Szerda     | 95 Ft     | (95/105) - 1 = **-9,52%** |
| Csütörtök  | 110 Ft    | (110/95) - 1 = **15,79%** |
| Péntek     | 98 Ft     | (98/110) - 1 = **-10,91%** |

### Átlagos hozam:

Az átlagos hozam kiszámítása:

**μ = (5,00% + (-9,52%) + 15,79% + (-10,91%)) / 4**  
**μ = 0,09% ≈ 0,001** *(decimális formában)*

### Volatilitás kiszámítása:

A szórás (σ) képlete:

**σ = sqrt( Σ (rₜ - μ)² / (N-1) )**

ahol:  
- *σ* a volatilitás,  
- *rₜ* a napi hozam,  
- *μ* az átlagos hozam,  
- *N* az időszakok száma.

Hozamok eltérése az átlagtól (rₜ - μ):

| Nap        | Hozam (rₜ) | rₜ - μ | (rₜ - μ)² |
|------------|-----------|--------|-----------|
| Kedd       | 5,00%     | 4,91%  | 0,00241   |
| Szerda     | -9,52%    | -9,61% | 0,00924   |
| Csütörtök  | 15,79%    | 15,70% | 0,02464   |
| Péntek     | -10,91%   | -11,00%| 0,01210   |

A variancia kiszámítása:

**Var = (0,00241 + 0,00924 + 0,02464 + 0,01210) / (4 - 1)**  
**Var = 0,0168**

A volatilitás (*σ*) pedig a variancia négyzetgyöke:

**σ = sqrt(0,0168) = 12,96%**

## Mit jelent a volatilitás a befektetők számára?

- **Magas volatilitás** → nagyobb kockázat, de lehetőség nagyobb hozamra.  
- **Alacsony volatilitás** → stabilabb befektetés, kisebb kockázat.  

A volatilitás fontos, mert a befektetők **nem szeretik a bizonytalanságot**, ezért egy nagyon ingadozó részvény általában **kockázatosabbnak** számít.
