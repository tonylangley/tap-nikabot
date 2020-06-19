from typing import List, Optional, Iterator, Any, Dict

from singer.schema import Schema

from .stream import Stream
from ..client import Client
from ..typing import JsonResult


class Groups(Stream):
    stream_id: str = "groups"
    key_properties: List[str] = ["id"]
    replication_key: Optional[str] = None

    def _map_to_schema(self, swagger: JsonResult) -> Schema:
        return Schema.from_dict(swagger["definitions"]["Group"])

    def get_records(self, client: Client, config: Dict[str, Any]) -> Iterator[List[JsonResult]]:
        return client.fetch_all_pages("/api/v1/groups")
