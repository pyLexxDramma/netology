from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import marshmallow
import marshmallow_dataclass

@dataclass
class Advertisement:
    title: str
    description: str
    owner: str
    creation_date: datetime = field(default=datetime.now())
    id: Optional[int] = field(default=None)

    class Meta:
        ordered = True

AdvertisementSchema = marshmallow_dataclass.class_schema(Advertisement)