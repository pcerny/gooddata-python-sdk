# (C) 2023 GoodData Corporation
from gooddata_sdk.catalog.entity import CatalogAttribute, TitledAttributes

ca_from_api = CatalogAttribute.from_api(
    {
        "data": {
            "type": "attribute",
            "id": "id1",
            "meta": {"origin": {"originType": "NATIVE", "originId": "string"}},
            "attributes": {
                "title": "myAttr",
                "description": "Muj hezky atribut",
                "tags": ["toto jsou tagy"],
                "granularity": "MINUTE",
                "areRelationsValid": True,
                "sortColumn": "string",
                "sortDirection": "ASC",
                "sourceColumn": "string",
                "sourceColumnDataType": "INT",
            },
            "relationships": {
                "dataset": {"data": {"id": "string", "type": "dataset"}},
                "defaultView": {"data": {"id": "string", "type": "label"}},
                "labels": {"data": [{"id": "string", "type": "label"}]},
            },
            "links": {"self": "string"},
        },
        "links": {"self": "string", "next": "next"},
        "included": [
            {
                "type": "dataset",
                "id": "id1",
                "meta": {"origin": {"originType": "NATIVE", "originId": "string"}},
                "attributes": {
                    "title": "string",
                    "description": "string",
                    "tags": ["string"],
                    "type": "NORMAL",
                    "grain": [{"id": "string", "type": "attribute"}],
                    "referenceProperties": [
                        {
                            "identifier": {"id": "string", "type": "dataset"},
                            "multivalue": True,
                            "sourceColumns": ["string"],
                            "sourceColumnDataTypes": ["string"],
                        }
                    ],
                    "dataSourceTableId": "string",
                    "sql": {"statement": "string", "dataSourceId": "string"},
                    "areRelationsValid": True,
                    "workspaceDataFilterColumns": [{"name": "string", "dataType": "INT"}],
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
                "meta": {"origin": {"originType": "NATIVE", "originId": "string"}},
                "attributes": {
                    "title": "string",
                    "description": "string",
                    "tags": ["string"],
                    "primary": True,
                    "sourceColumn": "string",
                    "sourceColumnDataType": "INT",
                    "valueType": "TEXT",
                    "areRelationsValid": True,
                },
                "relationships": {"attribute": {"data": {"id": "string", "type": "attribute"}}},
                "links": {"self": "string"},
            },
        ],
    }
)

print(ca_from_api)
print(ca_from_api.relationships)
print(ca_from_api.meta)
print(ca_from_api.links)
print(ca_from_api._document)

print("--- Manual ---")
ca_manual = CatalogAttribute(id="prd", attributes=TitledAttributes(title="MujPeknyAtribut-rucne vyrobeny"))
print(ca_manual)


print("--- to_dict - auto ---")
print(ca_from_api.to_dict())

print("--- to_dict - MANUAL ---")
print(ca_manual.to_dict())
