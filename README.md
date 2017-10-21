# Projeto: Analise de dados do Open Street Map 
## Curso: Data Science for Busines - Udacity

### Área do Mapa

Belo Horizonte - Minas Gerais - Brasil

Download do OSM: [Overpass API](http://overpass-api.de/api/map?bbox=-43.808,-20.0843,-44.1197,-19.7829)

Para este projeto foi escolhida a cidade de Belo Horizonte para analise de dados, mais precisamente a Região Metropolitana de Belo Horizonte, que inclui também outras cidades como Betim, Contagem, Ibirité, Nova Lima, Santa Luzia e Sabará. Por ser a minha cidade natal, esta é uma região da qual tenho um grande conhecimento, permitindo que eu realize uma análise mais crítica dos seus dados. Os scripts utilizados para esta analise foram os seguintes:

- convert\_osm\_json.py: responsável pela leitura do arquivo OSM e gravação do JSON
- audit\_address.py: responsável pela validação dos dados de endereço
- audit\_contact.py: responsável pela validação dos dados de contato

## Problemas Encontrados no Mapa

Os dados inseridos no Open Street Map são alimentados por diferentes usuários e, por essa razão, é comum encontrar descrições de mesmos tipos de dados com diversos formatos. Essas divergencias podiam ser causadas por digitação errada, abreviação ou, em alguns casos, pela ausência de alguma palavra no informação registrad. Desta forma, é importante uma analise dos dados e corrção ou padronização dos mesmos para obter uma analise mais apurada dos dados.

### Tipos de rua.

Para os tipos de rua, foi necessário extrair esta informação do início do nome das ruas informados na estrutura do OSM, uma vez que não se possuia um campo específico para este dado.

Feita a extração, foram encontrados algumas divergências nas informações, como já se esperava. Para tratar esta questão preparei 2 tipos de ajustes: uma para os casos de abreviação do tipo da rua ou correção do nome informado e outro para os casos em que o tipo de rua não haviam sido informados no nome da rua.

Para o primeiro caso, em que era necessário substituir o tipo encontrado, fiz um mapeamento para os tipos que deveria ser subsitituidos, conforme apresentado abaixo:

```python
street_type_mapping_replace = {
    "Av" : "Avenida",
    "Avendia" : "Avenida",
    "Anél" : "Anel",
    "Avenid" : "Avenida",
    "Eua" : "Rua",
    "Alamedas": "Alameda"
}
```

No segundo caso, onde era necessário inserir o tipo de rua, foi necessário um tratamento particular. Foi verificado o valor regitrado, realizando uma analisava sobre qual tipo de rua deveria ser inserido na frente do nome, que seria feito com base num dicionário de mapeamento, como mostrado abaixo:

```python
street_type_mapping_add = {
    "Br" : "Rodovia",
    "Br-381" : "Rodovia",
    "Dos": "Rua",
    "Francisco": "Rua",
    "Paraíba": "Rua",
    "Montes": "Rua",
    "Contorno": "Avenida",
    "Pium": "Rua",
    "Riachuelo": "Rua",
    "São" : "Rua"
}
```

Esta avaliação foi feita de forma iterativa, até que todos os casos existentes fossem tratados. Para isso foi utilizado o script `audit\_address.py`.

### Número das casas

Um outro problema encontrado foi em relação aos números dos endereços (chave *addr:housenumber*). Varios números foram registrados incluindo seus complementos (letras, numeoros de sala, etc.) e foi necessário fazer a separação destes campos.

Alguns exemplos de números fora do padrão esperado (numérico), identificados pelo script `audit\_addess.py`:

- 2515.7149 - Aperentemente um número de telefone
- 1534 A - Número: 1534 / Complemento: A
- 1452/Sala 206 - Número: 1452 / Complemento: Sala 206

Primeiramente foram tratados todos corretamente formatados com base na expressão regular abaixo:

```python
ADDRESS_NUMBER_RE = re.compile(r'^[0-9]+')
```

Em seguida, procurou-se tratar os numeros que apresentavam os complementos na sequência do número, ou separados por espaço, virgula(,),  hifen(-) ou barra (/) com a expressão regular a seguir:

```python
ADDRESS_NUMBER_WITH_NAME_RE = re.compile(r'^([0-9]+) ?[, \-/]? ?([A-Z0-9 º]+)', re.IGNORECASE)
```

Desta forma o número registrado como _1452/Sala 206_ seria separado entre _1452_ (número) e _Sala 206_ (complemento).

Os demais números que possuiam formato que não permitiam a identificação do número do endereço foram ignorados.

### CEP

Foram encontrados diversos formatos para os CEPs cadastrados no [Open Street Map](https://www.openstreetmap.org/#map=11/-19.8839/-43.9570). Os CEPs da cidade de  Belo Horizonte possuem o seguinte formato: 3XXXX-XXX, onde X é um digito entre 0 e 9. Foi utilizada a expressão abaixo para identificar os CEPs no formato correto. 

```python
ZIPCODE_RE = re.compile(r'^3[0-9]{4}\-[0-9]{3}')
```

Muitos dos CEPs cadastrados se encontravam com uma formatação diferente da apresentada acima. A partir de uma auditoria no dados feita com o script `audit_address.py`, foram encontrados os seguintes casos, com as respectivas solucões:

1. CEPs com 5 digitos. Ex: 30411. Neste caso o CEP foi completado com o final "-000".
2. CEPs com 8 digitos, sem separação com hifen (-). Ex: 30411080. Neste caso o hifen (-) foi adicionado, separando os 5 primeiros digitos dos 3 ultimos.
3. CEPs com separador de milhar (.) nos primeiros 5 digitos. Ex: 30.411-080. Neste caso o sinal de milhar (.) foi removido do CEP.

Além dos casos acima citados que possuiam formatos a partir dos quais era possível a identificação de um CEP válido, foram encontrados também alguns formatos de dados, os quais foram ignorados na conversão.

### Número de Telefone

O primeiro passo foi identicar quais os elementos que continha os dados a serem importados como telefone. Através de uma analise da estrutura de dados do OSM com o script `audit_contact.py`, foram selecionadas para conversão as tags com as seguintes chaves:

- *addr:phone*
- *addr:phone_1*
- *phone* 

Assim como ocorreu com o CEP, foram encontrados telefones cadastrados com diversas formatações. O primeiro passo foi identificar os telefones válidos e homogeneizá-los para manter a consistência dos dados. Os formatos validos são aqueles com 8 (fixo) ou 9 (móvel) digitos, com ou sem DDD (31) e DDI (55). Nesta situação, usei o sript `audit_contact.py` para identificar telefones válidos a partir da seguinte expressão regular:

```python
PHONENUMBER_RE = re.compile(r'\+?[5]{0,2} *.?31.? *(9?[0-9]{4}[\- ]?[0-9]{4})$')
```

Para este padrão é necessário que pelo menoso DDD de Belo Horizonte (31) deva ser informado, junto com o telefone. O número pode ser precedido ou não pelo DDI (+55).   

O segundo padrão identificado foram aqueles em que apenas o número do telefone foi informado, com ou sem separador. Este números deveriam possuir 8 (fixo) ou 9 (móvel) digitos. No caso de números com 9 digitos, ele deveria ser iniciado com o 9, identificado como um número de celular.

```python
PHONENUMBER_ONLYNUMBER_RE = re.compile(r'(9?[0-9]{4}[\- ]?[0-9]{4}$)')
```

Os números que não se adequaram a nenhuma das duas expressões usadas, foram desconsiderados.

A partir dos telefones encontrados, extraiu-se dos dados informados no arquivo OSM a parte dos telefones sem DDD ou DDI, os quais foram inseridos ao final da limpeza, considerando que o DDI do Brasil é 55 e o DDD de Belo Horizonte é 31. Abaixo 2 exemplos de como a limpeza foi realizada:

1) Número: **31 3123-1234**:
  - Extração do número do telefone (3123-1234) 
  - Inserção do prefixo "+55 31 " no início do número (+55 31 3123-1234)

2) Número: **55 31 981231234**:
  - Extração do número do telefone (981231234)
  - Separação do número de telefone com o hífen (98123-1234)
  - Inserção do prefixo "+55 31 " no início do número (+55 31 98123-1234)

##### *Listas de telefone*

Uma outra entrada encontrada era a presença de listas de telefones no lugar de um único número para contato. As listas eram separadas por ponto-e-virgula (;). Para o tratamento dessa situação, o primeiro passo foi retornar o valor encontrado no número do telefone no formato de lista. Posteriormente cada número da lista é validado com os formatos esperados para o telefone.

## Visão Geral dos Dados

### Arquivos utilizados

```
1. bh_map.osm - Arquivo OSM com os dados da cidade de Belo Horizonte - Tamanho: 67MB
2. bh_node.json - Arquivo JSON com elementos *node* a serem importados para o MongoDB - Tamanho: 71MB
3. bh_way.json - Arquivo JSON com elementos *way* a serem importados para o MongoDB - Tamanho: 19MB
4. bh_relation.json - Arquivo JSON com elementos *realtion* a serem importados para o MongoDB - Tamanho: 1MB
```

### Quantidade de elementos importados para o MongoDB

#### Node

```
db.bh.find({"data_type":"node"}).count()
```
> *287113*

#### Way

```
db.bh.find({"data_type":"way"}).count()
```
> *51785*

#### Relation

```
db.bh.find({"data_type":"relation"}).count()
```
> *2179*

### Colaborações

#### 10 maiores colaboradores

```
> db.bh.aggregate([ 
    {$group: {
        "_id":"$created.user", 
        "count":{$sum:1}
    }},
    {$sort:{count:-1}},
    {$limit:10} 
])
```

Resultado:
```
{ "_id" : "Vítor Dias", "count" : 87428 }
{ "_id" : "patodiez", "count" : 34207 }
{ "_id" : "Gerald Weber", "count" : 31668 }
{ "_id" : "BladeTC", "count" : 24503 }
{ "_id" : "lmpinto", "count" : 16849 }
{ "_id" : "andrellym", "count" : 14970 }
{ "_id" : "Samuel Vale", "count" : 10393 }
{ "_id" : "Djavan Fagundes", "count" : 7861 }
{ "_id" : "Vítor Dias - importação de dados", "count" : 7269 }
{ "_id" : "Tebeling", "count" : 5972 }
```
#### Quantidade de contribuições por ano

```
> db.bh.aggregate([
      {"$project":{"year":{"$substr":["$created.timestamp",0,4]},}},
      {"$group": {"_id":"$year", "count":{"$sum":1}}},
      {"$sort":{"count":-1}}
 ])
```
Resultado:
```
{ "_id" : "2017", "count" : 105214 }
{ "_id" : "2013", "count" : 75278 }
{ "_id" : "2015", "count" : 43580 }
{ "_id" : "2014", "count" : 30257 }
{ "_id" : "2012", "count" : 24775 }
{ "_id" : "2016", "count" : 19093 }
{ "_id" : "2011", "count" : 14829 }
{ "_id" : "2008", "count" : 10807 }
{ "_id" : "2009", "count" : 7597 }
{ "_id" : "2007", "count" : 5208 }
{ "_id" : "2010", "count" : 4439 }
```

## Outras Idéias

### Cervejarias Artesanais (microbrewery)

>“Minas não tem mar, mas tem bar.”

Belo Horizonte é conhecida pela sua fama de ser uma cidade boêmia, apresentando também uma grande vocação na fabricação de cervejas artesanais, como se pode ver nesta [matéria do Estado de Minas](https://www.em.com.br/app/noticia/economia/2017/04/02/internas_economia,859102/cerveja-artesanal-cresce-producao-em-minas-e-grande-bh.shtml) e neste [artigo do Melhores Destinos](https://guia.melhoresdestinos.com.br/noite-de-belo-horizonte-203-2580-p.html).

Desta forma decidi fazer uma pesquisa na base de dados do **Open Street Map**, com intuíto de verificar sua completude:

#### Quantidade de cervejarias artesanais

```
db.bh.find({ "microbrewery" : { "$exists":1 } }).count()
```
Resultado:
```
2
```

#### Quantidade de bares

```
db.bh.find( { "amenity" : {"$exists":1}, "amenity" : "bar"} ).count()
```
Resultado:
```
139
```

Com base na pesquisa realizada, pode-se perceber uma grande defasagem dos dados registrados em relação a quantidade de bares e cervejarias artesanais de Belo Horizonte. 

A fama boêmia de Belo Horizonte é vista como um dos atrativos turísticos para a cidade e desta forma poderia haver um esforço da Prefeitura de BH para atualização deste e disponibilização das informações como roteiro de noite de BH. Muito provavelmente estas informações já existem em base de dados de estatísticas da cidade e precisariam apenas de ser tratados e registrados no Open Street Map.

### 10 maiores areas de lazer por tipo:

```
> db.bh.aggregate([
    {"$match":{
        "leisure":{"$exists":1}
    }},
    {"$group":{
        "_id":"$leisure",
        "count":{"$sum":1}
    }},
    {"$sort":{"count":-1}},
    {"$limit":10}
])
```
Resultado:
```
{ "_id" : "park", "count" : 576 }
{ "_id" : "pitch", "count" : 339 }
{ "_id" : "sports_centre", "count" : 163 }
{ "_id" : "swimming_pool", "count" : 116 }
{ "_id" : "garden", "count" : 77 }
{ "_id" : "recreation_ground", "count" : 31 }
{ "_id" : "stadium", "count" : 28 }
{ "_id" : "playground", "count" : 16 }
{ "_id" : "fitness_centre", "count" : 12 }
{ "_id" : "dance", "count" : 9 }
```

### 5 principais espaço de prática de esportes, por tipo:

```
> db.bh.aggregate([
    {"$match":{
        "sport":{"$exists":1},
        "leisure":{"$exists":1}
    }},
    {"$unwind":"$sport"},
    {"$group":{
        "_id":"$sport",
        "count":{"$sum":1}
    }},
    {"$sort":{"count":-1}},
    {"$limit":5}
    ])
```
Resultado:
```
{ "_id" : "soccer", "count" : 237 }
{ "_id" : "multi", "count" : 53 }
{ "_id" : "tennis", "count" : 26 }
{ "_id" : "swimming", "count" : 24 }
{ "_id" : "volleyball", "count" : 19 }
```
## Conclusão

Com a realização da analise de dados deste trabalho, percebe-se que as informações registrada para a área de Belo Horizonte está bem defasada. Vemos também que existem um aumento nas contribuições em datas mais recentes, mas ainda concentrada em sua grande parte na mão de poucos usuários.

Para o efeito do exercício proposto, acredito que o tratamento de dados foi bem realizado, com uma limpeza das informações e boa consitência dos dados convertidos. Com a diferentes fontes de entrada de informações, foram encontradas várias divergencias nos dados, os quais foram devidamente tratados.