# Roadmap de estudo — maritime-logistics

Este repositório é um estudo prático de **Domain-Driven Design (DDD)**. Cada
tarefa constrói uma peça do domínio marítimo e exercita um conceito de DDD.
Todo o domínio é escrito com **TDD** (teste primeiro, red → green).

Legenda: ✅ concluído · 🔜 a fazer

---

## Parte concluída — a camada de Domínio (✅ Tarefas 1 a 4)

O coração do DDD: um modelo de domínio puro, sem banco, sem HTTP, testável
isoladamente. Tudo em `domain/`.

### ✅ Tarefa 1 — Value Objects folha
Arquivo: `domain/value_objects.py` · Teste: `tests/test_value_objects.py`

| Peça | Conceito DDD | O que ensina |
|---|---|---|
| `Coordinate`, `Tonnage`, `IMONumber` | **Value Object** | Objeto definido pelo valor, imutável (`frozen`), auto-validante. A regra mora junto do dado — é impossível existir um valor inválido no sistema. |

Destaque: o `IMONumber` valida formato **e** dígito verificador real (checksum),
mostrando um VO que encapsula uma regra de negócio de verdade.

### ✅ Tarefa 2 — Value Objects compostos
Arquivo: `domain/value_objects.py`

| Peça | Conceito DDD | O que ensina |
|---|---|---|
| `Distance`, `Cargo`, `Port`, `Route` | **Value Object (composição)** | Um VO contém outros VOs. Cada um valida só o que é dele; confia nos VOs que compõe. Invariantes empilhadas. |
| `Route.waypoints` (tuple) | **First-class collection** | Coleção encapsulada e imutável dentro de um objeto, não solta. |
| `VoyageStatus` | **Value Object (enum)** | O ciclo de vida como conjunto fechado de estados. |

### ✅ Tarefa 3 — O Aggregate `Ship`
Arquivo: `domain/ship.py` · Teste: `tests/test_ship.py`

| Peça | Conceito DDD | O que ensina |
|---|---|---|
| `Ship` | **Entity** / **Aggregate Root** | Identidade (`IMONumber`) em vez de valor: dois `Ship` são o mesmo navio se têm o mesmo IMO, mesmo com atributos diferentes. Igualdade e hash pela identidade. Estado mutável, identidade imutável. |
| `Ship.can_carry(cargo)` | **Comportamento no domínio** | O navio conhece a própria capacidade e responde "esse cargo cabe?". A lógica mora onde está o dado. |

### ✅ Tarefa 4 — O Aggregate `Voyage` + Domain Events
Arquivos: `domain/voyage.py`, `domain/events.py` · Testes: `tests/test_voyage.py`, `tests/test_events.py`

| Peça | Conceito DDD | O que ensina |
|---|---|---|
| `Voyage` | **Aggregate Root** | Protege as **invariantes** e as transições de estado válidas (`PLANNED → DEPARTED → ARRIVED`). O mundo externo só muda o estado por métodos (`depart`, `arrive`), nunca direto. |
| `ship_id: IMONumber` dentro do Voyage | **Referência entre aggregates por ID** | O `Voyage` referencia o `Ship` pela identidade, não pelo objeto. Regra de ouro dos aggregates. |
| `ShipDeparted` | **Domain Event** | Um fato no passado, imutável. O aggregate **registra** o evento (não publica); quem orquestra publica depois. Desacopla o domínio de quem reage. |
| `pull_events()` | **Record-and-dispatch** | Separar registrar de publicar garante consistência (só avisa "zarpou" se o estado foi salvo). |

---

## Parte a fazer — Serviços, Aplicação, Infra e API (🔜 Tarefas 5 a 9)

Aqui o domínio ganha orquestração, persistência e uma porta de entrada (API),
sem nunca sujar o modelo puro.

### 🔜 Tarefa 5 — Domain Services
Camada: `domain/`

| Peça | Conceito DDD | O que vai ensinar |
|---|---|---|
| `RouteCalculator`, `FuelEstimator` | **Domain Service** | Lógica de domínio que **não pertence a um único objeto** (calcular a rota entre dois portos não é do `Ship` nem do `Voyage`). Fica num serviço sem estado, nomeado com o verbo do domínio. |

### 🔜 Tarefa 6 — Repository ports
Camada: `domain/` (interface) + testes

| Peça | Conceito DDD | O que vai ensinar |
|---|---|---|
| `ShipRepository`, `VoyageRepository` (interfaces) | **Repository** | Ilusão de uma coleção em memória de aggregates. O domínio define **o que** precisa (`get`, `save`); a infra decide **como**. |
| `InMemory...Repository` | **Dependency Inversion** | Implementação fake pros testes — o domínio nunca depende do banco. |

### 🔜 Tarefa 7 — Use Cases (Application)
Camada: `application/`

| Peça | Conceito DDD | O que vai ensinar |
|---|---|---|
| `PlanVoyage`, `DepartVoyage` | **Application Service / Use Case** | Orquestra o fluxo: carrega aggregates pelo repositório, aplica a regra que **cruza aggregates** (`ship.can_carry(cargo)` antes de criar o `Voyage`), salva e publica eventos. Fina camada de coordenação, sem regra de negócio própria. |

### 🔜 Tarefa 8 — Infraestrutura
Camada: `infrastructure/`

| Peça | Conceito DDD | O que vai ensinar |
|---|---|---|
| `Postgres...Repository` (SQLAlchemy) | **Repository (implementação)** | O "como" da persistência, isolado do domínio. |
| Event publisher (structlog → JSON) | **Fronteira de efeito colateral** | Log/eventos só na borda, nunca no domínio. Preparado para o futuro (Projeto 3 escuta os eventos). |

### 🔜 Tarefa 9 — API (FastAPI)
Camada: `api/`

| Peça | Conceito DDD | O que vai ensinar |
|---|---|---|
| Endpoints REST | **Adapter de entrada** | Traduz HTTP → use case → HTTP. A API é só uma porta; a inteligência está no domínio. É o que será registrado no IDP (Backstage / OpenChoreo). |

---

## Mapa rápido: onde cada bloco DDD vive

```
domain/value_objects.py   -> Value Objects
domain/ship.py            -> Aggregate Root (Entity)
domain/voyage.py          -> Aggregate Root (Entity) + ciclo de vida
domain/events.py          -> Domain Events
domain/services.py        -> Domain Services            (Tarefa 5)
domain/repositories.py    -> Repository (interfaces)     (Tarefa 6)
application/               -> Use Cases                  (Tarefa 7)
infrastructure/           -> Repository (Postgres), logs (Tarefa 8)
api/                      -> Adapter de entrada (HTTP)   (Tarefa 9)
```

Regra que atravessa tudo: **as dependências apontam para dentro**. A API depende
da aplicação, que depende do domínio. O domínio não depende de ninguém — é puro.
