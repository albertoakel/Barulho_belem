# 🔊 Projeto: Barulho Belém — Mapa Colaborativo do Ruído Urbano

O **Barulho Belém** é uma aplicação interativa para **mapear, registrar e analisar ocorrências de poluição sonora em Belém-PA**.
A plataforma permite que qualquer cidadão registre pontos de barulho, contribuindo para um painel colaborativo que apoia pesquisas, planejamento urbano e ações de fiscalização.

## 🚀 Acesse o Aplicativo

A versão atual do protótipo está disponível online em:

👉 **[https://barulhodebelem92a.streamlit.app/](https://barulhodebelem92a.streamlit.app/)**

> Esta é uma versão inicial (protótipo). Alguns recursos ainda estão sendo refinados.

---

## 🎯 Objetivos

* Registrar ocorrências de ruído urbano de forma colaborativa.
* Mapear espacialmente os pontos de incômodo.
* Classificar tipos, intensidades e frequências de ruído.
* Construir uma base pública de dados sobre barulho urbano.
* Apoiar estudos acadêmicos, ambientais e urbanos.
* Fornecer insumos para políticas públicas e ações de fiscalização.

---

## 💡 Motivação

Belém convive diariamente com trânsito intenso, festas, obras, bares, caixas de som e múltiplas fontes de ruído.
A exposição constante ao som excessivo gera:

* estresse e irritabilidade;
* distúrbios do sono;
* prejuízos auditivos;
* impactos no aprendizado e bem-estar.

Apesar disso, **não existe uma base colaborativa** que registre onde e quando esses incômodos acontecem.
O Barulho Belém nasce para transformar relatos individuais em **informação georreferenciada**, visível e útil.

---

## 📌 O que o projeto faz

* **Coleta registros colaborativos** contendo:

  * localização via endereço ou clique no mapa;
  * categoria do ruído (trânsito, bares, obras, paredões etc.);
  * intensidade (Baixo, Médio, Alto);
  * frequência (Diário, Fins de semana, Ocasional);
  * horário e observações.

* **Geocodifica automaticamente** endereços usando OpenCage.

* **Armazena dados** em Google Sheets para persistência.

* **Exibe mapa interativo** com:

  * todos os pontos reportados;
  * concentração de ocorrências;
  * análise exploratória inicial.

* **Organiza o código em módulos** claros:

  * geocodificação (OpenCage),
  * integração com Google Sheets,
  * interface e UX no Streamlit.

---

## 🗺️ Visualização Interativa

Os registros aparecem em tempo real no mapa da aplicação online:

👉 **[https://barulhodebelem92a.streamlit.app/](https://barulhodebelem92a.streamlit.app/)**

---

## 📁 Estrutura do Projeto

```
Barulho_belem/
├── Principal/
│   ├── main.py                 # Aplicação principal (Streamlit)
│   ├── main_bkp.py
│   ├── gerador_requiremnts.py
│   ├── requirements.txt
│   ├── setup.py
│   └── teste_rotinas.ipynb
│
├── src/
│   ├── geocode_belem.py        # Módulo de geocodificação
│   └──  google_sheets.py        # Módulo para Google Sheets
│
├── sandbox/                    # Versões experimentais
│   ├── main.0.8.py
│   └── main_teste.py
│
└── README.md
```

---

## 💻 Como configurar o ambiente

> `requirements.txt` contém todas as dependências necessárias.

### Criar o ambiente

```bash
conda create -n barulho_belem python=3.11
conda activate barulho_belem
```

### Instalar dependências

```bash
pip install -r Principal/requirements.txt
```

Principais pacotes:

* streamlit
* folium / streamlit-folium
* opencage
* gspread + oauth2client
* pandas

---

## 🔐 Configuração de Credenciais

A aplicação utiliza:

* **OpenCage API** para geocodificação;
* **Google Service Account** para salvar dados.

As credenciais devem ser configuradas usando o painel de Secrets do Streamlit Cloud ou `secrets.toml` localmente.

---

## 🛠️ Status do Projeto

Esta é uma **versão protótipo**, focada em testes funcionais e coleta inicial de dados.
Próximas melhorias previstas:

* Filtros avançados no mapa;
* Visualizações estatísticas;
* Dashboard analítico;
* Exportação de dados;
* Sistema de denúncia para órgãos públicos.

---

## 📝 Licença

Este projeto está sob a licença **Creative Commons Attribution 4.0 (CC BY 4.0)**.
Você pode utilizar e adaptar o material livremente, desde que cite a fonte.
