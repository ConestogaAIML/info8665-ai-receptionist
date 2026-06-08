from pydantic import BaseModel


class VisitorRequest(BaseModel):
    name: str
    purpose: str
    host: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"name": "Jane Doe", "purpose": "Job interview", "host": "Alice Smith"}
            ]
        }
    }


class VisitorResponse(BaseModel):
    message: str
    visitor: str
    status: str
