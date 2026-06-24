# Ubiquitous Language — maritime-logistics

> Estes termos são a linguagem única entre código e negócio.
> Toda classe, método e variável usa exatamente estes nomes. Sem sinônimos.

## Conceitos do domínio

| Termo | Tipo DDD | Definição |
|---|---|---|
| **Ship** (Navio) | Aggregate Root | Embarcação que transporta carga. Tem identidade (IMO), capacidade máxima e consumo de combustível. |
| **IMO Number** | Value Object | Identidade global do navio. Formato `IMO` + 7 dígitos (ex: `IMO9074729`). |
| **Tonnage** (Tonelagem) | Value Object | Peso em toneladas métricas. Nunca negativo. Usado para capacidade e carga. |
| **Cargo** (Carga) | Value Object | O que o navio transporta: um tipo (ex: soja) e um peso (Tonnage). |
| **Port** (Porto) | Value Object | Local de embarque/desembarque. Tem nome, código UN/LOCODE e uma Coordinate. |
| **Coordinate** (Coordenada) | Value Object | Ponto geográfico em graus (latitude, longitude). |
| **Voyage** (Viagem) | Aggregate Root | Uma travessia planejada: navio + carga + porto de origem + porto de destino + rota + status. É o coração do domínio. |
| **Route** (Rota) | Value Object | Sequência de Coordinates (waypoints) que o navio percorre. Tem distância total em milhas náuticas. É o "GPS" que vai para o Projeto 1. |
| **Voyage Status** | Value Object (enum) | Ciclo de vida da viagem: `PLANNED` → `DEPARTED` → `ARRIVED`. |

## Ações do domínio (verbos = métodos)

| Verbo | Sujeito | Regra (invariante) |
|---|---|---|
| **plan a voyage** (planejar viagem) | use case | Carga não pode exceder a capacidade do navio. |
| **depart** (zarpar) | Voyage | Só zarpa se status = `PLANNED` e a rota já foi calculada. Não zarpa duas vezes. |
| **arrive** (chegar) | Voyage | Só chega se status = `DEPARTED`. |
| **calculate route** (calcular rota) | RouteCalculator (Domain Service) | Dados origem e destino, produz a Route. |
| **estimate fuel** (estimar combustível) | FuelEstimator (Domain Service) | Dada a rota e o navio, calcula combustível necessário. |

## Eventos do domínio (fatos no passado)

| Evento | Quando | Quem ouve (futuro) |
|---|---|---|
| **ShipDeparted** ("Navio Zarpou") | Quando uma Voyage zarpa com sucesso | Projeto 3 (rastreamento), notificações |

## Fronteira (Bounded Context)

Este é o contexto **Maritime Logistics** (Core Domain — onde mora a inteligência do produto).
- NÃO conhece projeção de mapa (metros X/Y) — isso é o contexto Cartográfico (Projeto 1, Generic Subdomain).
- Comunica com o Cartográfico entregando `Route` em graus (Lat/Lon). A tradução graus→metros é feita FORA daqui.
- Contextos não compartilham código — conversam por contratos. Por isso `Coordinate` aqui é próprio, mesmo o Projeto 1 já tendo `Latitude`/`Longitude`.

---

## Padrões de modelagem (building blocks)

Como cada peça do domínio se comporta. Estas são as regras que o código deve respeitar.

### Value Object
Definido pelo **valor**, não por identidade. Imutável (`frozen`). Dois com o mesmo valor são iguais.
- Auto-validante: nasce válido ou não nasce (erro na construção). A regra mora junto do dado.
- Ex: `Tonnage(500)` é igual a qualquer outro `Tonnage(500)`. Impossível existir `IMONumber` inválido no sistema.

### Aggregate (e Aggregate Root)
Cluster de objetos tratado como **uma unidade**, com um **Root** que protege as **invariantes** (regras que devem ser sempre verdadeiras).
- O mundo externo só fala com o Root. Nunca acessa objeto interno direto.
- Toda mudança passa por método do Root, que valida a regra ANTES de mudar o estado. Estado inválido vira impossível.
- O Root tem identidade global (ex: `VoyageId`). Referência a OUTRO aggregate é por **ID**, nunca pelo objeto inteiro (ex: `Voyage` guarda `ShipId`, não o `Ship`).
- Uma transação salva um aggregate por vez.
- Aggregates do projeto: **Ship** e **Voyage**. São separados porque um navio faz muitas viagens ao longo do tempo.

Exemplo de invariante protegida pelo Root:
- `Voyage.depart()` só zarpa se status = `PLANNED` e rota já calculada; nunca zarpa duas vezes.
- carga (`Cargo`) nunca excede a capacidade (`Tonnage`) do navio.

### Repository
Ilusão de uma **coleção em memória** de aggregates. Esconde o banco (Postgres) do domínio.
- Um repository por Aggregate Root: `ShipRepository`, `VoyageRepository`. Nunca de objeto interno.
- O domínio define a **interface** (o que precisa: `get(id)`, `save(aggregate)`). A infraestrutura define a **implementação** (como faz com Postgres).
- Domínio nunca importa infra (inversão de dependência). Isso permite testar com um repositório em memória (um `dict`) sem subir banco.
- Devolve o aggregate reconstruído inteiro, com invariantes válidas.

### Domain Event
Um **fato que aconteceu** no domínio, modelado como objeto imutável. Nome sempre no **passado**.
- Carrega os dados do fato + quando ocorreu (`occurred_on`).
- O aggregate **registra** o evento numa lista interna durante a regra — não dispara na hora. Quem orquestra (use case) **coleta e publica** depois de salvar.
- Separar registrar de publicar garante consistência: só publica "navio zarpou" se o save deu certo.
- Permite outras partes reagirem sem o aggregate conhecê-las (desacoplamento).
- Evento do projeto: **ShipDeparted** ("Navio Zarpou"). Hoje só loga; no futuro vira mensagem entre contextos (Projeto 3 escuta).
