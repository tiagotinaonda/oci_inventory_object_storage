# OCI Object Storage Report

Script em Python para gerar um relatório de utilização de Object Storage na Oracle Cloud Infrastructure (OCI), percorrendo todas as regiões assinadas e todos os compartments ativos da tenancy.

O resultado é exportado para um arquivo `.csv` contendo:

- Região
- Compartment
- Nome do Bucket
- Quantidade de Objetos
- Tamanho em GB
- Custo estimado mensal
- Storage Tier

---

# Funcionalidades

- Descobre automaticamente todos os compartments ativos
- Percorre todas as regiões subscribed da OCI
- Coleta:
  - Nome do bucket
  - Quantidade de objetos
  - Tamanho aproximado em GB
  - Storage Tier
  - Estimativa de custo mensal
- Utiliza `approximateSize` e `approximateCount` para otimizar performance
- Exporta para CSV separado por TAB
- Trata erros de permissão ou acesso em compartments

---

# Requisitos

- Python 3.8+
- OCI Python SDK
- Configuração OCI CLI válida

---

# Instalação

## Instalar dependências

```bash
pip install oci
```

---

# Configuração OCI

O script utiliza a configuração padrão do OCI SDK:

```python
config = oci.config.from_file()
```

Configure seu arquivo:

```bash
~/.oci/config
```

Exemplo:

```ini
[DEFAULT]
user=ocid1.user.oc1..
fingerprint=xx:xx:xx
key_file=/home/user/.oci/oci_api_key.pem
tenancy=ocid1.tenancy.oc1..
region=sa-saopaulo-1
```

---

# Permissões Necessárias

O usuário/grupo OCI deve possuir permissões para:

- Compartments
- Object Storage Buckets
- Object Storage Namespace
- Region subscriptions

Exemplo de policy:

```text
Allow group Administrators to inspect compartments in tenancy
Allow group Administrators to read buckets in tenancy
Allow group Administrators to read objectstorage-namespaces in tenancy
```

---

# Configuração de custo

O cálculo do custo estimado utiliza um valor por GB/mês:

```python
PRECO_GB_MES = 0.13
```

Ajuste conforme o valor do seu contrato OCI.

---

# Uso

Execute:

```bash
python3 oci_object_storage_report.py
```

---

# Saída

O script gera:

```text
oci_object_storage_report.csv
```

Formato:

```text
Cloud    Region    Compartment    BucketName    ObjectCount    SizeGB    EstimatedCost_BRL    StorageTier
```

---

# Exemplo de saída

```text
OCI	sa-saopaulo-1	Production	backup-bucket	15230	540.21	70.23	Standard
OCI	us-ashburn-1	Development	logs-bucket	8450	120.56	15.67	Archive
```

---
