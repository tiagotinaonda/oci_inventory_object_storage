#!/usr/bin/env python3
import oci
import csv
from oci.pagination import list_call_get_all_results
from oci.exceptions import ServiceError

# ==============================
# CONFIG
# ==============================
# Preço estimado por GB (ajuste conforme seu contrato)
# Com base na imagem, o SKU B91628 é o Storage padrão.
PRECO_GB_MES = 0.13 # Exemplo: R$ 0,13 por GB/mês

config = oci.config.from_file()
tenancy_id = config["tenancy"]

identity_client = oci.identity.IdentityClient(config)
object_storage_client = oci.object_storage.ObjectStorageClient(config)

# O namespace é único por Tenancy
try:
    namespace = object_storage_client.get_namespace().data
except Exception as e:
    print(f"Erro ao obter namespace: {e}")
    exit(1)

# ==============================
# Compartments
# ==============================
def get_all_compartments(compartment_id):
    try:
        compartments = list_call_get_all_results(
            identity_client.list_compartments,
            compartment_id,
            compartment_id_in_subtree=True,
            lifecycle_state="ACTIVE"
        ).data
    except Exception:
        compartments = []

    compartments.append(
        oci.identity.models.Compartment(id=tenancy_id, name="RootTenancy")
    )

    return compartments

print("⏳ Coletando compartments...")
compartments = get_all_compartments(tenancy_id)

# ==============================
# Regiões
# ==============================
regions = [
    r.region_name
    for r in list_call_get_all_results(
        identity_client.list_region_subscriptions,
        tenancy_id
    ).data
]

# ==============================
# CSV saída
# ==============================
csv_file = "oci_object_storage_report.csv"

with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter="\t")

    writer.writerow([
        "Cloud",
        "Region",
        "Compartment",
        "BucketName",
        "ObjectCount",
        "SizeGB",
        "EstimatedCost_BRL",
        "StorageTier"
    ])

    # ==============================
    # Loop regiões
    # ==============================
    for region in regions:

        print(f"\n🔎 Analisando Região: {region}")

        # Cliente específico para a região
        regional_client = oci.object_storage.ObjectStorageClient(
            config, 
            service_endpoint=f"https://objectstorage.{region}.oraclecloud.com"
        )

        for comp in compartments:

            comp_id = comp.id
            comp_name = comp.name

            # ==========================
            # LIST BUCKETS
            # ==========================
            try:
                buckets = list_call_get_all_results(
                    regional_client.list_buckets,
                    namespace_name=namespace,
                    compartment_id=comp_id
                ).data
            except ServiceError:
                buckets = []

            for b in buckets:
                try:
                    # Buscando detalhes do bucket para pegar o tamanho aproximado
                    # 'approximateSize' e 'approximateCount' são campos que evitam listar todos os objetos
                    bucket_details = regional_client.get_bucket(
                        namespace_name=namespace,
                        bucket_name=b.name,
                        fields=['approximateSize', 'approximateCount']
                    ).data

                    size_bytes = bucket_details.approximate_size if bucket_details.approximate_size else 0
                    size_gb = size_bytes / (1024**3)
                    obj_count = bucket_details.approximate_count if bucket_details.approximate_count else 0
                    cost = size_gb * PRECO_GB_MES

                    writer.writerow([
                        "OCI",
                        region,
                        comp_name,
                        b.name,
                        obj_count,
                        round(size_gb, 4),
                        round(cost, 2),
                        bucket_details.storage_tier
                    ])
                    print(f"  ✅ Bucket: {b.name} ({round(size_gb, 2)} GB)")
                    
                except ServiceError as e:
                    print(f"  ❌ Erro ao obter detalhes do bucket {b.name}: {e.message}")

print(f"\n✅ Relatório de Object Storage concluído: {csv_file}")
