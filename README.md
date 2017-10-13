# Projeto: Analise de dados do Open Street Map 
## Curso: Data Science for Busines - Udacity

### Área do Mapa

Belo Horizonte - Minas Gerais - Brasil

Download do OSM: [Overpass API](http://overpass-api.de/api/map?bbox=-44.0758,-20.0282,-43.8258,-19.7493)

Escolhi a cidade de Belo Horizonte para analise de dados por ser a minha cidade natal. Por esta razão está é uma cidade que tenho um grande conhecimento, permitindo que eu realize uma análise mais crítica dos seus dados.

## Problemas Encontrados no Mapa

### Tipos de Rua



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

Assim como ocorreu com o CEP, foram encontrados telefones cadastrados com diversas formatações. O primeiro passo foi identificar os telefones válidos e homogeneizá-los para manter a consistência dos dados. Os formatos validos são aqueles com 8 ou 9 digitos, com ou sem DDD (31) e DDI (55). Neste situação foram encontrados os seguintes formatos:

1. Telefones completos, com DDI e DDD. Ex: +55 31 3333-3333
2. Telefones completos, sem DDI e com DDD. Ex: 31 3333-3333
3. Telefones completos, sem DDI e DDD. Ex: 3333-3333
4. 

## Visão Geral dos Dados

## Outras Idéias

## Conclusão