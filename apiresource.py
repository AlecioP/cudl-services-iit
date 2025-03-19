from enum import Enum, unique

# Should come bundled with flask
from werkzeug.routing import BaseConverter, ValidationError

@unique
class apiXmlResource(str,Enum):
    SCHEMA = "schema.xsd"
    STYLE = "stylesheet.xsl"

class apiXmlResourceConverter(BaseConverter):
    def to_python(self, value):
        try:
            request_type = apiXmlResource(value)
            return request_type
        except ValueError:
            raise ValidationError("More specific error")

    def to_url(self, obj):
        return obj.value