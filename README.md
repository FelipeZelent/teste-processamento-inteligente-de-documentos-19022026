# Teste Técnico (Extração de informações em Faturas de Energia)

Para garantir o eficiente gerenciamento dos créditos de energia provenientes de usinas de energia renovável, é fundamental a extração precisa e automática de dados das notas fiscais de energia elétrica. Além disso, possuir conhecimento sobre faturas de energia elétrica é importante para o sucesso na gestão desses recursos.

Logo, é proposto dois testes como parte da avaliação dos conhecimentos técnicos e teóricos dos candidatos. Essa avaliação tem o objetivo de medir a compreensão do participante no contexto da extração de dados de notas fiscais e no entendimento básico de faturas de energia elétrica.

# Teste 1

Em busca pela eficiência na leitura de faturas, a equipe de desenvolvimento propõe a criação de uma rotina que, a partir de faturas de energia elétrica em formato de PDF, seja capaz de extrair importantes informações.

Nesta atividade, você deve editar o arquivo read.py e desenvolver uma rotina capaz de realizar a leitura da fatura fatura_cpfl.pdf em formato de PDF e retornar as seguintes informações:

- Titular da fatura (Nome e Documento)
- Endereço completo do titular da fatura
- Classificação da Instalação
- Número da instalação
- Valor a Pagar para a distribuidora
- Data de Vencimento
- Mês ao qual a fatura é referente
- Tarifa total com tributos
- Tarifa total Aneel
- Quantidade em kWh do Consumo da fatura
- Saldo em kWh acumulado na Instalação
- Somatório das quantidades das energias compensadas (injetadas)
- Somatório dos Valores Totais das Operações R$
- Contribuição de iluminação Pública
- Alíquotas do ICMS, PIS e COFINS em %
- Linha digitável para pagamento

Organize a saída e visualização das informações extraídas.

# Documentação do Teste 1

Como Executar o Projeto

Criar ambiente virtual
```
python3 -m venv venv
source venv/bin/activate
```
Instalar dependências
```
pip install pdfplumber
```
Executar o script
```
python read.py
```

A solução para a extração de dados foi desenvolvida utilizando a biblioteca pdfplumber para a conversão precisa do documento PDF em texto estruturado. Em seguida, foi implementado um parser baseado em Expressões Regulares (Regex) nativas da biblioteca re do Python.

Arquitetura e Decisões Técnicas:

Identificação Dinâmica: Foi criada a função central process_invoice que varre o texto extraído, identifica automaticamente se a fatura pertence à CPFL ou CEMIG, e direciona o texto para a função de parsing específica, tornando o código modular e escalável.

Sanitização de Dados: Funções auxiliares (clean_currency e clean_number) foram construídas para higienizar strings de moedas e grandezas físicas no padrão brasileiro (ex: "1.234,56"), convertendo-as para o tipo float para permitir cálculos e formatações consistentes.

Tratamento de Exceções Layout: Diferenças textuais, como textos encavalados na mesma linha ("10.10.2023 às 06:30:49" na 2ª via da Cemig) foram previstos e contornados pelas expressões regulares, garantindo a robustez na captura do "Número de Instalação".

Apresentação: Foi criada uma função dedicada (print_formated_data) que atende estritamente ao requisito de "organizar a saída e visualização", imprimindo os 16 campos solicitados de maneira amigável no terminal.

Visão de Produção:
Para cenários de grande escala, soluções baseadas em Regex podem requerer manutenção frequente devido a mudanças nos layouts das concessionárias. A evolução recomendada seria a adoção de APIs de Document AI ou OCR Cognitivo, utilizando o script atual como validador (fallback)



# Teste 2

Contexto: Você recebeu a fatura "fatura_cemig.pdf" e deve desenvolver um script para extrair seus dados. Antes de iniciar a programação, é essencial compreender e interpretar as informações presentes nesta fatura.

Atividade: Analise a fatura e redija um documento respondendo os pontos abaixo. As respostas podem ser inseridas neste 'README'.

 - Identifique as principais diferenças entre a fatura "fatura_cemig.pdf" e uma fatura convencional de energia elétrica "fatura_cemig_convencional.pdf".
 - Descreva e explique os termos e valores apresentados na seção "Valores Faturados" da fatura "fatura_cemig.pdf".
 - Considerando que a instalação da "fatura_cemig.pdf" participa do Sistema de Compensação de Energia Elétrica, identifique e explique qual informação na seção "Informações Gerais" da fatura é considerada a mais importante.
 - Identifique o consumo da instalação referente ao mês de julho de 2023.

# Resposta para o Teste 2
1. Diferenças entre a fatura GD ("fatura_cemig.pdf") e a convencional ("fatura_cemig_convencional.pdf"):
A diferença primordial é a participação no Sistema de Compensação de Energia Elétrica (SCEE). Na fatura convencional, o fluxo é unidirecional (o cliente consome da rede e paga o total). Na fatura GD, o cliente injeta energia na rede. Assim, a fatura evidencia os créditos gerados pela usina ("Energia compensada") utilizados para abater o consumo da unidade no mês, restando o custo de disponibilidade e tributos não compensáveis (como iluminação pública).

2. Termos e valores na seção "Valores Faturados":
- Energia Elétrica: Tarifa de Energia (TE) + Tarifa de Uso do Sistema de Distribuição (TUSD) aplicadas sobre o consumo bruto medido pela concessionária.
- Energia SCEE s/ ICMS: Montante de energia consumida da rede equivalente ao que foi injetado (compensado). Ocorre a isenção de ICMS sobre essa parcela, justificando a sua separação no demonstrativo.
- Energia compensada GD II / Energia comp. adicional: Créditos de energia (em kWh) da geração própria usados para abater o valor da conta. Eles entram como um valor dedutível (negativo).
- Contrib. Ilum. Publica Municipal: Taxa obrigatória das prefeituras. Não pode ser abatida com créditos de energia GD.

3. Informação mais importante na seção "Informações Gerais":
Considerando o Sistema de Compensação, a informação mais crítica é o SALDO ATUAL DE GERAÇÃO (que consta como 234,63 kWh). Essa métrica indica o "banco de créditos" ativo da instalação, vital para o monitoramento da saúde financeira e da eficiência da usina (se ela está gerando superávit ou déficit de energia ao longo dos meses).

4. Consumo da instalação referente ao mês de julho de 2023:
Consultando o quadro de "Histórico de Consumo" na fatura_cemig.pdf, o consumo medido referente ao mês JUL/23 foi de 199 kWh.

# Requisitos dos Desafios:

1. Utilize a linguagem Python para desenvolver a solução.
2. No mesmo README, inclua uma seção detalhada que explique claramente os passos necessários para executar o código. Certifique-se de que as instruções sejam precisas, organizadas e fáceis de entender, pois os avaliadores seguirão essa documentação.
3. Faça um fork do repositório, para iniciar o desenvolvimento.
4. A entrega deve ser realizada por meio de um pull request para o repositório original. Caso não consiga, os arquivos podem ser enviados para o email falecom@dg.energy, porém com penalidade de pontos.
5. Abra o pull request também faltando 5 minutos para o prazo final da entrega do teste. Se o pull request for realizado antes dos 5 minutos restantes haverá eliminação do candidato.
6. A entrega deve ser realizada até às 12:30h.
