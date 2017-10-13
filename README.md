# Projeto: Analise de dados do Open Street Map 
## Curso: Data Science for Busines - Udacity

### Área do Mapa

Belo Horizonte - Minas Gerais - Brasil

Download do OSM: [Overpass API](http://overpass-api.de/api/map?bbox=-44.0758,-20.0282,-43.8258,-19.7493)

Escolhi a cidade de Belo Horizonte para analise de dados por ser a minha cidade natal. Por esta razão está é uma cidade que tenho um grande conhecimento, permitindo que eu realize uma análise mais crítica dos seus dados.

## Problemas Encontrados no Mapa

### Tipos de rua.

Pelo fato dos dados cadastrados no Open Street Map serem feitos por diferentes pessoas, foi comum encontrar a descrição do tipo de ruas com diversos formatos. Essas divergencias podiam ser causadas por digitação errada, abreviação ou, em alguns casos, pela ausênia do tipo de rua no nome registrado. 

Para tratar esta questão preparei 2 tipos de ajustes: uma para os casos em que era necessário substituir o nome, como  no exemplo abaixo:

```
street_type_mapping_replace = {
    "Av" : "Avenida",
    "Avendia" : "Avenida",
    "Anél" : "Anel",
    "Avenid" : "Avenida",
    "Eua" : "Rua",
    "Alamedas": "Alameda"
}
```
No outro tipo de ajuste, foi necessário um tratamento particular, no qual eu verificava o valor digitado e analisava qual tipo de rua deveria ser inserido na frente do nome, como mostrado abaixo:

```
street_type_mapping_add = {
    "Br" : "Rodovia",
    "Br-381" : "Rodovia",
    "Dos": "Rua",
    "Francisco": "Rua",
    "Paraíba": "Rua",
    "Montes": "Rua",
    "Contorno": "Avenida",
    "Pium-i": "Rua",
    "Riachuelo": "Rua",
    "São" : "Rua"
}
```

Esta avaliação foi feita de forma iterativa, através do script audit_address.py.

### Número das casas

### CEP

Foram encontrados diversos formatos para os CEPs cadastrados no [Open Street Map](https://www.openstreetmap.org/#map=11/-19.8839/-43.9570). Os CEPs das cidades brasileiras possuem o seguinte formato: XXXXX-XXX, onde X é um digito entre 0 e 9. Utilizei uma *regex* para identificar os CEPs no formato correto. 

```
ZIPCODE_RE = re.compile(r'[0-9]{5}\-[0-9]{3}')
```

Muitos dos CEPs cadastrados se encontravam com uma formatação diferente da apresentada acima. A partir de uma auditoria no dados feita com o script audit_address.py, encontrei os seguintes casos, com as respectivas solucões:

1. CEPs com 5 digitos. Ex: 30411. Neste caso o CEP foi completado com o final "-000".
2. CEPs com 8 digitos, sem separação com hifen (-). Ex: 30411080. Neste caso o hifen (-) foi adicionado, separando os 5 primeiros digitos dos 3 ultimos.
3. CEPs com separador de milhar (.) nos primeiros 5 digitos. Ex: 30.411-080. Neste caso o sinal de milhar (.) foi removido do CEP.

Além dos casos acima citados que possuiam um formato possível de se identificar um CEP válido, foram encontrados também alguns dados inválidos, os quais precisaram ser tratados de forma particular. 

### Número de Telefone

Assim como ocorreu com o CEP, foram encontrados telefones cadastrados com diversas formatações. O primeiro passo foi identificar os telefones válidos e homogeneizá-los para manter a consistência dos dados. Os formatos validos são aqueles com 8 ou 9 digitos, com ou sem DDD (31) e DDI (55). Nesta situação, usei o sript audit_contact.py e foram encontrados os seguintes formatos:

1. Telefones completos, com DDI e DDD. Ex: +55 31 3333-3333
2. Telefones completos, sem DDI e com DDD. Ex: 31 3333-3333
3. Telefones completos, sem DDI e DDD. Ex: 3333-3333
4. 

Para conistência das informações, todos os telefones foram colocados no formato +55 31 XXXX-XXXX (fixo) ou +55 31 XXXXX-XXXX (móvel).

##### Listas de telefone

Uma outra possibilidade era a presença de listas de telefones no lugar de um único número para contato. As listas eram separadas por ponto-e-virgula (;). Separei estes casos em listas e cada um dos telefones registrados eram comparados com o formato permitido.

## Visão Geral dos Dados

## Outras Idéias

## Conclusão