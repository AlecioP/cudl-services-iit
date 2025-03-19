from apiresource import apiXmlResource

# MAYBE READ FROM FILE IN FUTURE
MAP_RUOTE_TO_FILESYSTEM = {
    "prefisso-filesystem" : "/home/myuser/somedirectory",
    "tipologie-documentali" : {
        "filetype1" : {
            "versioni-anni" : {
                "1800" : {
                    "tipologie-risorse" : {
                        apiXmlResource.SCHEMA.value : "/filetype1-1800/something.xsd",
                        apiXmlResource.STYLE.value : "/filetype1-1800/else.xsl"
                    }
                }
            }
        },
        "filetype2" : {
            "versioni-anni" : {
                "1700" : {
                    "tipologie-risorse" : {
                        apiXmlResource.SCHEMA.value : "/filetype2-1700/something.xsd",
                        apiXmlResource.STYLE.value : "/filetype2-1700/else.xsl"
                    }
                },
                "1600" : {
                    "tipologie-risorse" : {
                        apiXmlResource.SCHEMA.value : "/filetype2-1600/something.xsd",
                        apiXmlResource.STYLE.value : "/filetype2-1600/else.xsl"
                    }
                }
            }
        }
    }
}