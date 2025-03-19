from apiresource import apiXmlResourceConverter, apiXmlResource

from pathlib import Path

from flask import Flask, Response #,send_file

app = Flask(__name__,template_folder="data/static")

from flask import send_from_directory, render_template

from lxml import etree
from saxonche import PySaxonProcessor #, PySaxonApiError
    
app.url_map.converters.update(api_xmlResource=apiXmlResourceConverter)

def handle_bad_request(e):
    #notfound_page_path = "./data/static/404.html" # changed in flask app constructor TODO should load path from config JSON
    return render_template("404.html"), 404

app.register_error_handler(404, handle_bad_request)

from config import MAP_RUOTE_TO_FILESYSTEM

@app.route('/v1/transcriptions/plain/<path:path>')
def send_transcription_plain(path):
    return send_from_directory(Path('data/transcr/plain'), path, mimetype="text/html")

@app.route('/v1/transcriptions/structured/<docType>/<yearVersion>/<docKey>')
def send_transcription_struct_saxon(docType,yearVersion,docKey):
    # FIXME directory traversal attack
    STRUCT_TRASCR_PREFIX = "./data/transcr/struct/"

    data_xml_path = STRUCT_TRASCR_PREFIX + docKey + "/data.xml"

    schema_path = MAP_RUOTE_TO_FILESYSTEM["prefisso-filesystem"] + MAP_RUOTE_TO_FILESYSTEM["tipologie-documentali"][docType]["versioni-anni"][yearVersion]["tipologie-risorse"][apiXmlResource.SCHEMA.value]

    transform_path = MAP_RUOTE_TO_FILESYSTEM["prefisso-filesystem"] + MAP_RUOTE_TO_FILESYSTEM["tipologie-documentali"][docType]["versioni-anni"][yearVersion]["tipologie-risorse"][apiXmlResource.STYLE.value]

    with PySaxonProcessor(license=False) as proc:
        xsltproc = proc.new_xslt30_processor()
        with open(data_xml_path,"r") as f:
            document = proc.parse_xml(xml_text=f.read())

        # IF data.xml is a DOCTYPE1/YEAR1 should be validated with the 
        # proper schema and processed with the proper XSL
        # 
        # Anyway nothing prevents one for making a request to the url
        # DOCTYPE2/YEAR2/DOCID_1
        # this way DOCID_1 which is valid against schema DOCTYPE1/YEAR1
        # would be processed with XSL for DOCTYPE2/YEAR2
        # which could lead to unwanted results.
        #
        # To solve this we test that the xml data validates against the
        # schema for the type DOCTYPE2/YEAR2 which is not true


        # ALL THIS IS NOT LICENSED WITH SAXONC home edition 
        # xsd_proc = proc.new_schema_validator()
        # xsd_proc.register_schema(xsd_file=schema_path)
        # try:
        #     xsd_proc.validate(xdm_node=document)#(file_name=data_xml_path)
        # except PySaxonApiError :
        #     return "The document corresponding to the requested ID cannot be processed with the tools relative to the requested DOC type"
        #
        # REPLACING WITH lxml 
        with open(data_xml_path) as f:
            struct_data = etree.parse(f)
        with open(schema_path) as f:
            schema = etree.XMLSchema(etree.parse(f))
        if not schema.validate(struct_data):
            return "Semantic error in URL : The document corresponding to the requested ID cannot be processed with the tools relative to the requested DOC type"
        
        executable = xsltproc.compile_stylesheet(stylesheet_file=transform_path)
        output = executable.transform_to_string(xdm_node=document)
    return Response(output,mimetype="text/html")

#@app.route('/v1/transcriptions/structured/<docType>/<yearVersion>/<docKey>')
def send_transcription_struct(docType,yearVersion,docKey):

    # TODO 
    # as pointed out in this comment
    # https://stackoverflow.com/questions/46785786/how-to-convert-xml-into-html-using-xslt-2-transformation-from-python3#comment80518546_46785786
    # lxml python library is based on libxslt which only supports XSLT 1.0
    # Stylesheets like tabella/1882/stylesheet.xsl need some Xpath functions to handle date formats properly
    # those functions are only available on XSLT 2.0 
    #
    # We need to use an external processor who supports XSLT 2.0
    # Probably Saxon processor. Needs JVM though
    #
    # Edit: SaxonC is Saxon compiled for C/C++ platforms 
    # SaxonC API for python is available here https://pypi.org/user/saxonica/
    # Only Home edition (saxonc-he) is non commercial but license should be studied because 
    # some components are under mozilla license
    #
    # Here for more https://www.saxonica.com/saxon-c/index.xml

    # NOTE
    # One could easily request a trascription generated with an improper stylesheet.
    # There is nothing indicating the doc type of ID/data.xml 

    STRUCT_TRASCR_PREFIX = "./data/transcr/struct/"

    data_xml_path = STRUCT_TRASCR_PREFIX + docKey + "/data.xml"

    schema_path = MAP_RUOTE_TO_FILESYSTEM["prefisso-filesystem"] + MAP_RUOTE_TO_FILESYSTEM["tipologie-documentali"][docType]["versioni-anni"][yearVersion]["tipologie-risorse"][apiXmlResource.SCHEMA.value]

    transform_path = MAP_RUOTE_TO_FILESYSTEM["prefisso-filesystem"] + MAP_RUOTE_TO_FILESYSTEM["tipologie-documentali"][docType]["versioni-anni"][yearVersion]["tipologie-risorse"][apiXmlResource.STYLE.value]


    with open(data_xml_path) as f:
        struct_data = etree.parse(f)

    with open(schema_path) as f:
        schema = etree.XMLSchema(etree.parse(f))

    with open(transform_path) as f:
        transform = etree.XSLT(etree.parse(f))

    if not schema.validate(struct_data):
        return "Error : data did not validate against candidate schema"

    result = transform(struct_data)
    binc = etree.tostring(result, pretty_print=True, encoding='utf-8')
    return binc.decode('utf-8')



@app.route("/v1/schema/<docType>/<yearVersion>/<api_xmlResource:resourceType>")
def send_schema(docType,yearVersion,resourceType):
    path_str = None
    try:
        path_str = MAP_RUOTE_TO_FILESYSTEM["prefisso-filesystem"] + MAP_RUOTE_TO_FILESYSTEM["tipologie-documentali"][docType]["versioni-anni"][yearVersion]["tipologie-risorse"][resourceType]
    except KeyError :
        return "Some Error"
    
    # TODO Sanitizing path still looks like a good idea

    content = None
    with open(Path(path_str),"r") as fd:
        content = fd.read()
    if not (content is None) :
        return Response(content,mimetype="text/xml")
    else:
        return "Some other Error"