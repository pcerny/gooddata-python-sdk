# (C) 2022 GoodData Corporation
from __future__ import annotations

import base64
import typing
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar, Dict, ForwardRef, Generic, List, Optional, Type, TypeVar, Union

import attr
import cattrs
from cattrs.gen import make_dict_unstructure_fn, override

from gooddata_api_client.model.json_api_attribute_out import JsonApiAttributeOut
from gooddata_api_client.model.json_api_attribute_out_document import JsonApiAttributeOutDocument
from gooddata_api_client.model.json_api_dataset_out import JsonApiDatasetOut
from gooddata_api_client.model.json_api_label_out import JsonApiLabelOut
from gooddata_sdk.catalog.base import Base, JsonApiEntityBase
from gooddata_sdk.compute.model.base import ObjId
from gooddata_sdk.utils import AllPagedEntities

T = TypeVar("T", bound="AttrCatalogEntity")

T2 = TypeVar("T2", bound="AttrCatalogEntity2")
A = TypeVar("A", bound="Attributes")
R = TypeVar("R", bound="Relationships")
INC = TypeVar("INC")
SL = TypeVar("SL")
D = TypeVar("D", bound="AttrCatalogEntityDocument")


@attr.s(auto_attribs=True)
class AttrCatalogEntity:
    id: str

    type: str = attr.field(default=attr.Factory(lambda self: self._get_type(), takes_self=True))

    def _get_type(self) -> str:
        allowed_values = getattr(self.client_class(), "allowed_values")
        if allowed_values:
            values = list(allowed_values.get(("type",), {}).values())
            if len(values) > 0:
                return values[0]
        raise ValueError(f"Unable to extract type from ${self.client_class().__name__}")

    # Optional, because write use case -
    # we need to pass only ID and some properties in attributes when creating an instance of this class
    json_api_entity: Optional[JsonApiEntityBase] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None

    @property
    def json_api_attributes(self) -> Dict[str, Any]:
        return self.json_api_entity.attributes if self.json_api_entity else {}

    @property
    def json_api_relationships(self) -> Dict[str, Any]:
        return self.json_api_entity.relationships if self.json_api_entity and self.json_api_entity.relationships else {}

    @property
    def json_api_side_loads(self) -> List[Dict[str, Any]]:
        return self.json_api_entity.side_loads if self.json_api_entity else []

    @property
    def json_api_related_entities_data(self) -> List[Dict[str, Any]]:
        return self.json_api_entity.related_entities_data if self.json_api_entity else []

    @property
    def json_api_related_entities_side_loads(self) -> List[Dict[str, Any]]:
        return self.json_api_entity.related_entities_side_loads if self.json_api_entity else []

    @property
    def obj_id(self) -> ObjId:
        return ObjId(self.id, type=self.type)

    @classmethod
    def from_api(
        cls: Type[T],
        entity: Dict[str, Any],
        side_loads: Optional[List[Any]] = None,
        related_entities: Optional[AllPagedEntities] = None,
    ) -> T:
        """
        Creates GoodData object from AttrCatalogEntityJsonApi.
        """
        json_api_entity = JsonApiEntityBase.from_api(entity, side_loads, related_entities)
        return cls(
            id=json_api_entity.id,
            json_api_entity=json_api_entity,
            title=json_api_entity.attributes.get("title"),
            description=json_api_entity.attributes.get("description"),
            tags=json_api_entity.attributes.get("tags", []),
        )

    @staticmethod
    def client_class() -> Any:
        return NotImplemented


@attr.s(auto_attribs=True, kw_only=True)
class Attributes:
    description: Optional[str] = attr.field(default=None)
    tags: Optional[List[str]] = attr.field(default=None)


@attr.s(auto_attribs=True, kw_only=True)
class TitledAttributes(Attributes):
    title: str


@attr.s(auto_attribs=True, kw_only=True)
class DatasetAttributes(TitledAttributes):
    type: str


@attr.s(auto_attribs=True)
class EntityLink:
    id: str
    type: str

    @staticmethod
    def structure_hook(data: Any, cls_type: Type[Any]) -> Any:
        entity_data = data.get("data", None)
        if entity_data is None:
            raise ValueError(f"Missing enclosing data key for ${cls_type}")
        return EntityLink(id=entity_data["id"], type=entity_data["type"])

    @staticmethod
    def unstructure_hook(obj: Any) -> Any:
        if obj is None:
            return None
        if not isinstance(obj, EntityLink):
            raise ValueError("Only EntityLink unstructure supported")
        return dict(data=dict(id=obj.id, type=obj.type))


class EntityLinkList(List[EntityLink]):
    @staticmethod
    def structure_hook(data: Any, cls_type: Type[Any]) -> Any:
        entity_data = data.get("data", None)
        if entity_data is None:
            raise ValueError(f"Missing enclosing data key for ${cls_type}")
        return [EntityLink(id=value["id"], type=value["type"]) for value in entity_data]

    @staticmethod
    def unstructure_hook(obj: Any) -> Any:
        if obj is None:
            return None
        if not isinstance(obj, List):
            raise ValueError("Only EntityLinkList unstructure supported")
        return dict(data=[dict(id=obj_item.id, type=obj_item.type) for obj_item in obj])


@attr.s(auto_attribs=True, kw_only=True)
class Relationships:
    pass


@attr.s(auto_attribs=True, kw_only=True)
class AttributeRelationships(Relationships):
    dataset: Optional[EntityLink] = attr.field(default=None)
    default_view: Optional[EntityLink] = attr.field(default=None)
    labels: Optional[EntityLinkList] = attr.field(default=None)


class OriginType(Enum):
    NATIVE = "NATIVE"
    PARENT = "PARENT"


@attr.s(auto_attribs=True)
class MetaOrigin:
    origin_id: str
    origin_type: OriginType


@attr.s(auto_attribs=True)
class Meta:
    origin: Optional[MetaOrigin]


@attr.s(auto_attribs=True)
class ObjectLink:
    self_key: str

    @staticmethod
    def structure_hook_user(data: Any, _cls_type: Type[Any]) -> Any:
        entity_data = data.get("self", None)
        if entity_data is None:
            raise ValueError("Missing self key in ObjectLink")
        return ObjectLink(self_key=entity_data)

    @staticmethod
    def structure_hook_oapi(data: Any, _cls_type: Type[Any]) -> Any:
        entity_data = data.get("_self", None)
        if entity_data is None:
            raise ValueError("Missing self key in ObjectLink")
        return ObjectLink(self_key=entity_data)

    @staticmethod
    def unstructure_hook_user(obj: Any) -> Any:
        if not isinstance(obj, ObjectLink):
            raise ValueError("Only ObjectLink unstructure supported")
        return dict(self=obj.self_key)

    @staticmethod
    def unstructure_hook_oapi(obj: Any) -> Any:
        if not isinstance(obj, ObjectLink):
            raise ValueError("Only ObjectLink unstructure supported")
        return dict(_self=obj.self_key)


@attr.s(auto_attribs=True)
class NextLink:
    self_key: str
    next: Optional[str] = attr.field(default=None)

    @staticmethod
    def structure_hook_user(data: Any, _cls_type: Type[Any]) -> Any:
        entity_data = data.get("self", None)
        if entity_data is None:
            raise ValueError("Missing self key in ObjectLink")
        return NextLink(self_key=entity_data, next=data.get("next", None))

    @staticmethod
    def structure_hook_oapi(data: Any, _cls_type: Type[Any]) -> Any:
        entity_data = data.get("_self", None)
        if entity_data is None:
            raise ValueError("Missing self key in ObjectLink")
        return NextLink(self_key=entity_data, next=data.get("next", None))

    @staticmethod
    def unstructure_hook_user(obj: Any) -> Any:
        if not isinstance(obj, NextLink):
            raise ValueError("Only NextLink unstructure supported")
        if next is not None:
            return dict(self=obj.self_key, next=obj.next)
        else:
            return dict(self=obj.self_key)

    @staticmethod
    def unstructure_hook_oapi(obj: Any) -> Any:
        if not isinstance(obj, NextLink):
            raise ValueError("Only NextLink unstructure supported")
        if next is not None:
            return dict(_self=obj.self_key, next=obj.next)
        else:
            return dict(_self=obj.self_key)


class AttributeIncludedType(List[Union["CatalogLabel", "CatalogDataset"]]):
    ...
    # @staticmethod
    # def structure_hook(data: Any, _cls_type: Type[Any]) -> Any:
    #     return structure(data, List[Union[CatalogLabel, CatalogDataset]])


# cattrs.register_structure_hook(AttributeIncludedType, AttributeIncludedType.structure_hook)
# cattrs.register_structure_hook(AttributeIncludedType, AttrCatalogEntity2.structure_hook_for_union)


@attr.s(auto_attribs=True)
class AttrCatalogEntityDocument(Generic[INC]):
    links: Optional[NextLink] = attr.field(default=None)
    included: Optional[INC] = attr.field(default=None)

    @staticmethod
    def client_class() -> Any:
        return NotImplemented


@attr.s(auto_attribs=True)
class AttrCatalogEntity2(Generic[A, R, D]):
    id: str
    attributes: A

    type: str = attr.field(default=attr.Factory(lambda self: self._get_type(), takes_self=True))

    relationships: Optional[R] = attr.field(repr=False, default=None)
    meta: Optional[Meta] = attr.field(repr=False, default=None)
    links: Optional[ObjectLink] = attr.field(repr=False, default=None)

    # included: Optional[INC] = attr.field(repr=False, default=None, metadata={"to_api": False})
    _document: Optional[D] = attr.field(init=False, repr=False, default=None)

    @classmethod
    def data_only_converter(cls, oapi_compatible: bool) -> cattrs.Converter:
        c = cattrs.Converter()
        omit_hook = make_dict_unstructure_fn(AttrCatalogEntity2, c, _document=override(omit=True))
        c.register_unstructure_hook(AttrCatalogEntity2, omit_hook)
        c.register_unstructure_hook(EntityLink, EntityLink.unstructure_hook)
        c.register_unstructure_hook(EntityLinkList, EntityLinkList.unstructure_hook)
        c.register_unstructure_hook(Optional[EntityLinkList], EntityLinkList.unstructure_hook)
        if oapi_compatible:
            c.register_unstructure_hook(ObjectLink, ObjectLink.unstructure_hook_oapi)
            c.register_unstructure_hook(NextLink, NextLink.unstructure_hook_oapi)
        else:
            c.register_unstructure_hook(ObjectLink, ObjectLink.unstructure_hook_user)
            c.register_unstructure_hook(NextLink, NextLink.unstructure_hook_user)

        return c

    @classmethod
    def structure_converter(cls, oapi_compatible: bool) -> cattrs.Converter:
        c = cattrs.GenConverter()
        c.register_structure_hook(EntityLink, EntityLink.structure_hook)
        c.register_structure_hook(EntityLinkList, EntityLinkList.structure_hook)
        if oapi_compatible:
            c.register_structure_hook(ObjectLink, ObjectLink.structure_hook_oapi)
            c.register_structure_hook(NextLink, NextLink.structure_hook_oapi)
        else:
            c.register_structure_hook(ObjectLink, ObjectLink.structure_hook_user)
            c.register_structure_hook(NextLink, NextLink.structure_hook_user)
        return c

    @staticmethod
    def client_class() -> Any:
        return NotImplemented

    @classmethod
    def _get_type(cls) -> str:
        allowed_values = getattr(cls.client_class(), "allowed_values")
        if allowed_values:
            values = list(allowed_values.get(("type",), {}).values())
            if len(values) > 0:
                return values[0]
        raise ValueError(f"Unable to extract type from ${cls.client_class().__name__}")

    @classmethod
    def structure_hook_for_union(cls, c: cattrs.Converter, data: Any, cls_type: Type[Any]) -> Any:
        # py37 get_origin - getattr(cls, "__origin__", None)
        # py37 get_args - cls.__args__
        type_field = data.get("type", None)
        if type_field is None:
            raise ValueError("Data are missing type key")

        origin = typing.get_origin(cls_type)
        args = typing.get_args(cls_type)
        if origin != typing.Union:
            raise ValueError("Class type origin must be Union")
        if len(args) == 0:
            raise ValueError("Union type must enclose at least one type")
        type_to_args = {}
        for arg in args:
            klass = arg
            if isinstance(arg, ForwardRef):
                if not arg.__forward_evaluated__:
                    # noinspection PyProtectedMember
                    typing._eval_type(arg, globals(), locals())
                klass = arg.__forward_value__
            if not hasattr(klass, "_get_type"):
                raise ValueError(f"Unable to find _get_type method for class ${klass}")
            klass_type = klass._get_type()
            type_to_args[klass_type] = klass

        final_klass = type_to_args.get(type_field, None)
        if final_klass is None:
            raise ValueError(
                f"Unable to match type ${type_field} to any of Union argument types ${type_to_args.keys()}"
            )

        return c.structure(data, final_klass)

    @classmethod
    def from_api(cls: Type[T2], entity: Dict[str, Any], oapi_compatible: bool = True) -> T2:
        """
        Creates GoodData object from AttrCatalogEntityJsonApi.
        """
        data = entity.get("data", None)
        if not data:
            raise ValueError(f'Missing top-level key "data" in entity ${entity}')
        c = cls.structure_converter(oapi_compatible)
        instance = c.structure(data, cls)
        # TODO: how to get around this call? Verify on py3.7
        origs = getattr(cls, "__orig_bases__", None)
        if origs is None or len(origs) < 1:
            raise ValueError(f"Unable to resolve Document type for ${cls}")
        # take 3rd TypeVar argument instance
        doc_cls = typing.get_args(origs[0])[2]
        print(doc_cls)
        instance._document = c.structure(entity, doc_cls)
        return instance

    @classmethod
    def from_dict(cls: Type[T2], data: Dict[str, Any], camel_case: bool = True) -> T2:
        """
        Creates object from dictionary. It needs to be specified if the dictionary is in camelCase or snake_case.
        """
        client_object = data
        if camel_case:
            # OAPI library expects self key with camel_case=True
            client_object = cls.client_class().from_dict(data, camel_case)
        return cls.from_api(client_object, False)

    @staticmethod
    def _is_attribute_private(attribute: attr.Attribute) -> bool:
        return attribute.name.startswith("_")

    def _get_snake_dict(self, oapi_compatible: bool) -> Dict[str, Any]:
        conv = self.data_only_converter(oapi_compatible)
        data_dict = conv.unstructure(self)
        doc_dict = conv.unstructure(self._document)
        doc_dict["data"] = data_dict
        return doc_dict

    def to_dict(self, camel_case: bool = True) -> Dict[str, Any]:
        if not camel_case:
            # this branch is crucial for self keys
            # OAPI client represents self key in snake_case as _self -> make sure, user gets self even for snake_case
            return self._get_snake_dict(False)
        return self.to_api().to_dict(camel_case)

    def to_api(self) -> Any:
        dictionary = self._get_snake_dict(True)
        return self._document.client_class().from_dict(dictionary, camel_case=False)

    @property
    def obj_id(self) -> ObjId:
        return ObjId(self.id, type=self.type)


class CatalogAttributeDocument(AttrCatalogEntityDocument[List[Union["CatalogLabel", "CatalogDataset"]]]):
    #    side_loads: Optional[SL] = attr.field(repr=False, default=None)
    @staticmethod
    def client_class() -> Any:
        return JsonApiAttributeOutDocument

    @classmethod
    def structure_converter(cls, c: cattrs.Converter) -> None:
        c.register_structure_hook(
            Union["CatalogLabel", "CatalogDataset"],
            lambda data, cls_type: AttrCatalogEntity2.structure_hook_for_union(c, data, cls_type),
        )


@attr.s(auto_attribs=True, kw_only=True)
class CatalogAttribute(
    AttrCatalogEntity2[TitledAttributes, AttributeRelationships, CatalogAttributeDocument]
    #    AttrCatalogEntity2[TitledAttributes, AttributeRelationships, List[Union["CatalogLabel", "CatalogDataset"]]]
):
    @staticmethod
    def client_class() -> Any:
        return JsonApiAttributeOut

    @classmethod
    def structure_converter(cls, oapi_compatible: bool) -> cattrs.Converter:
        c = super().structure_converter(oapi_compatible)
        CatalogAttributeDocument.structure_converter(c)
        return c


@attr.s(auto_attribs=True, kw_only=True)
class LabelRelationships(Relationships):
    attribute: Optional[EntityLink] = attr.field(default=None)


@attr.s(auto_attribs=True, kw_only=True)
class CatalogLabel(AttrCatalogEntity2[TitledAttributes, LabelRelationships, List["CatalogAttribute"]]):
    @staticmethod
    def client_class() -> Any:
        return JsonApiLabelOut


@attr.s(auto_attribs=True, kw_only=True)
class DatasetRelationships(Relationships):
    attributes: Optional[EntityLinkList] = attr.field(default=None)
    facts: Optional[EntityLinkList] = attr.field(default=None)
    references: Optional[EntityLinkList] = attr.field(default=None)


@attr.s(auto_attribs=True, kw_only=True)
class CatalogDataset(AttrCatalogEntity2[DatasetAttributes, DatasetRelationships, List["CatalogDataset"]]):
    @staticmethod
    def client_class() -> Any:
        return JsonApiDatasetOut


class CatalogEntity:
    def __init__(self, entity: dict[str, Any]) -> None:
        self._e = entity["attributes"]
        self._entity = entity
        self._obj_id = ObjId(self._entity["id"], type=self._entity["type"])

    @property
    def id(self) -> str:
        return self._entity["id"]

    @property
    def type(self) -> str:
        return self._entity["type"]

    @property
    def title(self) -> Optional[str]:
        # Optional, not all metadata objects contain title
        return self._e.get("title")

    @property
    def description(self) -> Optional[str]:
        # Optional, not all metadata objects contain description
        return self._e.get("description")

    @property
    def obj_id(self) -> ObjId:
        return self._obj_id


@attr.s(auto_attribs=True, kw_only=True)
class Credentials(Base):
    TOKEN_KEY: ClassVar[str] = "token"
    USER_KEY: ClassVar[str] = "username"
    PASSWORD_KEY: ClassVar[str] = "password"

    def to_api_args(self) -> dict[str, Any]:
        return attr.asdict(self)

    @classmethod
    def is_part_of_api(cls, entity: dict[str, Any]) -> bool:
        return NotImplemented

    @classmethod
    def create(cls, creds_classes: list[Type[Credentials]], entity: dict[str, Any]) -> Credentials:
        for creds_class in creds_classes:
            if creds_class.is_part_of_api(entity):
                return creds_class.from_api(entity)

        raise ValueError("No supported credentials found")

    @classmethod
    def validate_instance(cls, creds_classes: list[Type[Credentials]], instance: Credentials) -> None:
        passed = isinstance(instance, tuple(creds_classes))
        if not passed:
            classes_as_str = ",".join([str(creds_class) for creds_class in creds_classes])
            raise ValueError(f"Unsupported credentials type. Pick one of {classes_as_str}")


@attr.s(auto_attribs=True, kw_only=True)
class TokenCredentials(Credentials):
    token: str = attr.field(repr=lambda value: "***")

    @classmethod
    def is_part_of_api(cls, entity: dict[str, Any]) -> bool:
        return cls.USER_KEY not in entity

    @classmethod
    def from_api(cls, entity: dict[str, Any]) -> TokenCredentials:
        # Credentials are not returned for security reasons
        return cls(token="")


@attr.s(auto_attribs=True, kw_only=True)
class TokenCredentialsFromFile(Credentials):
    file_path: Path
    token: str = attr.field(init=False, repr=lambda value: "***")

    def __attrs_post_init__(self) -> None:
        self.token = self.token_from_file(self.file_path)

    def to_api_args(self) -> dict[str, Any]:
        return {self.TOKEN_KEY: self.token}

    @classmethod
    def is_part_of_api(cls, entity: dict[str, Any]) -> bool:
        return cls.USER_KEY not in entity

    @classmethod
    def from_api(cls, entity: dict[str, Any]) -> TokenCredentialsFromFile:
        # Credentials are not returned for security reasons
        raise NotImplementedError

    @staticmethod
    def token_from_file(file_path: Path) -> str:
        with open(file_path, "rb") as fp:
            return base64.b64encode(fp.read()).decode("utf-8")


@attr.s(auto_attribs=True, kw_only=True)
class BasicCredentials(Credentials):
    username: str
    password: str = attr.field(repr=lambda value: "***")

    @classmethod
    def is_part_of_api(cls, entity: dict[str, Any]) -> bool:
        return cls.USER_KEY in entity

    @classmethod
    def from_api(cls, attributes: dict[str, Any]) -> BasicCredentials:
        # Credentials are not returned from security reasons
        return cls(
            username=attributes[cls.USER_KEY],
            # Password is not returned from API (security)
            # You have to fill it to keep it or update it
            password="",
        )
