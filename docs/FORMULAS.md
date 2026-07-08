# Fórmulas matemáticas — maritime-logistics

Este documento registra as fórmulas matemáticas usadas no domínio.

**Padrão do projeto:** quando o código espelha uma fórmula matemática
conhecida, é aceitável usar nomes de variável de uma letra (`a`, `c`, `R`),
desde que a fórmula esteja documentada aqui. As letras têm proveniência — são
a notação padrão da fórmula, não nomes soltos. Toda função que implementa uma
fórmula deve referenciar a seção correspondente deste arquivo.

---

## Haversine — distância great-circle entre dois pontos

**Onde no código:** `Coordinate.distance_to()` em `domain/value_objects.py`.

**Para que serve:** calcular a distância real entre duas coordenadas sobre a
superfície da Terra (uma esfera). Não se usa Pitágoras porque a Terra é curva.
O resultado sai em milhas náuticas (nm).

### Fórmula

```
a = sin²(Δφ / 2) + cos(φ₁) · cos(φ₂) · sin²(Δλ / 2)
c = 2 · atan2(√a, √(1 − a))
d = R · c
```

### Proveniência das variáveis

| Símbolo | Significado | Nome no código |
|---|---|---|
| φ₁, φ₂ | latitudes dos dois pontos, em radianos | `lat1`, `lat2` |
| Δφ | diferença de latitude, em radianos | `distance_lat` |
| Δλ | diferença de longitude, em radianos | `distance_lon` |
| R | raio médio da Terra em milhas náuticas (3440.065) | `earth_radius_nautical_miles` |
| a | quadrado de metade do comprimento da corda entre os pontos | `a` |
| c | distância angular em radianos | `c` |
| d | distância na superfície (valor retornado) | — (retornado como `Distance`) |

### Notas

- `R = 3440.065 nm` vem do raio médio da Terra: 6371 km ÷ 1.852 km/nm.
- 1 milha náutica é definida como 1 minuto de arco de latitude, então 1 grau
  de latitude ≈ 60 nm — usado como caso de teste conhecido.
- Referência: https://en.wikipedia.org/wiki/Haversine_formula

---

<!--
Padrão para novas fórmulas (ex.: consumo de combustível no FuelEstimator):

## Nome da fórmula

**Onde no código:** ...
**Para que serve:** ...

### Fórmula
```
...
```

### Proveniência das variáveis
| Símbolo | Significado | Nome no código |
|---|---|---|
-->
