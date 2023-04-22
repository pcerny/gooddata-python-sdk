# (C) 2023 GoodData Corporation
from gooddata_sdk.catalog.entity import CatalogAttribute, TitledAttributes

ca_from_api = CatalogAttribute.from_api(
    {
        "data": {
            "type": "attribute",
            "id": "id1",
            "meta": {"origin": {"origin_type": "NATIVE", "origin_id": "string"}},
            "attributes": {
                "title": "myAttr",
                "description": "Muj hezky atribut",
                "tags": ["toto jsou tagy"],
                "granularity": "MINUTE",
                "are_relations_valid": True,
                "sort_column": "string",
                "sort_Direction": "ASC",
                "source_column": "string",
                "source_column_data_type": "INT",
            },
            "relationships": {
                "dataset": {"data": {"id": "string", "type": "dataset"}},
                "default_view": {"data": {"id": "string", "type": "label"}},
                "labels": {"data": [{"id": "string", "type": "label"}]},
            },
            "links": {"self": "string"},
        },
        "links": {"self": "string", "next": "next"},
        "included": [
            {
                "type": "dataset",
                "id": "id1",
                "meta": {"origin": {"origin_type": "NATIVE", "origin_id": "string"}},
                "attributes": {
                    "title": "string",
                    "description": "string",
                    "tags": ["string"],
                    "type": "NORMAL",
                    "grain": [{"id": "string", "type": "attribute"}],
                    "reference_properties": [
                        {
                            "identifier": {"id": "string", "type": "dataset"},
                            "multivalue": True,
                            "source_columns": ["string"],
                            "source_column_data_types": ["string"],
                        }
                    ],
                    "data_source_table_id": "string",
                    "sql": {"statement": "string", "dataSourceId": "string"},
                    "are_relations_valid": True,
                    "workspace_data_filter_columns": [{"name": "string", "dataType": "INT"}],
                },
                "relationships": {
                    "attributes": {"data": [{"id": "string", "type": "attribute"}]},
                    "facts": {"data": [{"id": "string", "type": "fact"}]},
                    "references": {"data": [{"id": "string", "type": "dataset"}]},
                },
                "links": {"self": "string"},
            },
            {
                "type": "label",
                "id": "id1",
                "meta": {"origin": {"origin_type": "NATIVE", "origin_id": "string"}},
                "attributes": {
                    "title": "string",
                    "description": "string",
                    "tags": ["string"],
                    "primary": True,
                    "source_column": "string",
                    "source_column_data_type": "INT",
                    "value_type": "TEXT",
                    "are_relations_valid": True,
                },
                "relationships": {"attribute": {"data": {"id": "string", "type": "attribute"}}},
                "links": {"self": "string"},
            },
        ],
    },
    False,
)

print(ca_from_api)
print(ca_from_api.relationships)
print(ca_from_api.meta)
print(ca_from_api.links)
print(ca_from_api._document)

print("--- Manual ---")
ca_manual = CatalogAttribute(id="prd", attributes=TitledAttributes(title="MujPeknyAtribut-rucne vyrobeny"))
print(ca_manual)

print("--- to_snake_dict - auto ---")
print(ca_from_api._get_snake_dict(oapi_compatible=False))

print("--- to_dict - auto ---")
print(ca_from_api.to_dict())

print("--- to_dict - MANUAL ---")
print(ca_manual.to_dict())
