from typing import Any

import mongoengine as me
from pydantic import BaseModel


class ProjectBaseDocument(me.Document):
    meta = {
        "abstract": True,
    }

    def set_attrs(self, **attrs):
        for field_name, field_value in attrs.items():
            setattr(self, field_name, field_value)

    def to_dereferenced_dict(self, include_id=False) -> dict:
        """Convert a SON document to a normal Python dictionary instance.

        This is trickier than just *dict(...)* because it needs to be
        recursive.
        """

        def transform_value(document: Any) -> Any:
            son = document.to_mongo_patched()
            for field_name in self:
                value = document._data.get(field_name, None)
                field = document._fields.get(field_name)
                if isinstance(field, me.ReferenceField):
                    son[field_name] = transform_value(value)
            if not include_id:
                son.pop("id")
            return son

        dereferenced_son = transform_value(self)
        return dereferenced_son.to_dict()

    def to_mongo_patched(self, rename_id=True):
        data = self.to_mongo()
        if rename_id and "_id" in data:
            data["id"] = data.pop("_id")
        return data


class ProjectBaseSchema(BaseModel):
    class Config:
        ...
