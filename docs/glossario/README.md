# Glossário histórico da leitura modernizada

Algumas palavras dos documentos caíram de uso e não têm forma atual: o modernizador as deixa
como estão. O glossário explica essas palavras numa nota numerada (¹²³) colocada logo depois da
palavra na aba **Textos**, com a lista das notas embaixo da leitura modernizada. A numeração
recomeça em cada fólio, na ordem em que os termos aparecem, e o mesmo termo repetido usa o mesmo
número. Copiar e Baixar .txt levam os números em sobrescrito e as notas no fim.

## Como acrescentar um verbete

Edite [`glossario.json`](glossario.json). O app relê o arquivo quando ele muda, sem reiniciar.

```json
{
  "termo": "rocio",
  "formas": ["rocio", "rossio"],
  "situacao": "rascunho",
  "nota": "Rocio (rossio): terreno público de uso comum junto à vila.",
  "fontes": ["Moraes Silva, Diccionario da lingua portugueza (1789), verbete \"rocio\"."]
}
```

- `formas`: as grafias como aparecem na **leitura modernizada**. Acento e maiúscula não contam.
- `situacao`:
  - `hipotese`: a leitura ou o sentido ainda estão em discussão. Vale registrar as hipóteses.
  - `rascunho`: o sentido foi proposto, mas a fonte ainda não foi conferida.
  - `conferida`: a equipe conferiu na fonte. Só nesse caso a palavra deixa de aparecer
    sublinhada como "palavra a conferir".
- `fontes`: dicionário de época, edição ou estudo consultado (ex.: Bluteau, *Vocabulario
  portuguez e latino*, 1712–1728; Moraes Silva, *Diccionario da lingua portugueza*, 1789).

A nota explica a palavra. Ela não corrige a transcrição diplomática, que continua sendo a leitura
conferida na imagem.
