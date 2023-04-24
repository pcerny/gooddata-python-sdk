# (C) 2023 GoodData Corporation
import gooddata_api_client as api_client
import gooddata_api_client.apis as apis
from gooddata_sdk.catalog.entity import CatalogAttribute

token = "YWRtaW46Ym9vdHN0cmFwOmFkbWluMTIz"
host = "http://localhost:3000"

my_api_config = api_client.Configuration(host=host)
my_api_client = api_client.ApiClient(
    configuration=my_api_config,
    header_name="Authorization",
    header_value=f"Bearer {token}",
)


entity_api = apis.EntitiesApi(my_api_client)
result = entity_api.get_entity_attributes("demo", "campaign_channels.category", include=["ALL"])
print(result)
print(result.to_dict())
print(CatalogAttribute.from_api(result))
