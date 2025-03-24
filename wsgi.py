from os import abort
from pathlib import Path
import xml.dom.minidom
import urllib.parse

import flask
from lxml import etree
from flask import Flask, Response #,send_file

app = Flask(__name__,template_folder="data/static")

from flask import send_from_directory, render_template


import os
import requests


# https://www.mail-archive.com/lxml@python.org/msg00035.html
class SimpleResolver(etree.Resolver):
    def resolve(self, url, pubid, context):
        res = requests.get(url)
        return self.resolve_string(res.text, context)

def handle_bad_request(e):
    # TODO should load path from config JSON
    # notfound_page_path = "./data/static/404.html" # changed in flask app constructor
    return render_template("404.html"), 404

app.register_error_handler(404, handle_bad_request)

@app.route('/v1/transcriptions/plain/<path:path>')
def send_transcription_plain(path):
    return send_from_directory(Path('data/transcr/plain'), path, mimetype="text/html")

@app.route('/v1/transcriptions/structured/<docType>/<yearVersion>/<docKey>')
def send_transcription_struct_saxon(docType,yearVersion,docKey):

    STRUCT_TRASCR_PREFIX = "./data/transcr/struct/"
    #
    # len("data.xml") = 8
    #
    # s o m e / d a t a . x  m  l
    # 0 1 2 3 4 5 6 7 8 9 10 11 12
    #
    # s[-8] = 5
    # s[:-8] = s [0:5] (5 excluded)
    #
    # s o m e /
    # 0 1 2 3 4
    #
    if Path(docKey).parts[-1] == "data.xml":
        docKey = docKey[:- len("data.xml")]
    # Path traversal attack should be covered
    PROBABLE_CONTENT = send_from_directory(STRUCT_TRASCR_PREFIX, Path(docKey) / "data.xml", mimetype="text/xml")
    print(f"From {STRUCT_TRASCR_PREFIX} serving {Path(docKey) / 'data.xml'}", flush=True)
    if PROBABLE_CONTENT.status_code == 404:
        flask.abort("Directory traversal", 404)
    # Sending the file would pass sanity check. But since i need to read the file
    # in memory to read schema url and validate against and send_from_directory
    # sets direct_sendthrough=True i need an explicit file.open
    # PROBABLE_CONTENT.get_data(as_text=True) doesn't work

    xml_path = Path(STRUCT_TRASCR_PREFIX) / docKey / "data.xml"
    print(f"Opening {xml_path}",flush=True)
    with open(xml_path, "r") as xml_fd:
        document_content = xml_fd.read()
        file_dom = xml.dom.minidom.parseString(document_content)
    root_el : xml.dom.minidom.Element = file_dom.documentElement
    print(f"{root_el}",flush=True)

    schema_url = root_el.getAttribute("xsi:noNamespaceSchemaLocation")

    print(f"{schema_url}", flush=True)

    url_path_parts = Path(urllib.parse.urlparse(schema_url).path).parts

    print(f"{url_path_parts}", flush=True)
    if (not(docType in url_path_parts)) or (not(yearVersion in url_path_parts)):
        return "Schema declared in url and the one declared in xml content do not match"

    custom_parser = etree.XMLParser(load_dtd=True, no_network=False, huge_tree=True, resolve_entities=True)
    custom_parser.resolvers.add(SimpleResolver())

    schema= etree.XMLSchema(etree.fromstring(requests.get(schema_url).content, custom_parser))
    struct_data = etree.parse(xml_path)

    print(f"{schema}", flush=True)
    if not schema.validate(struct_data):
        return '''Semantic error in URL : The document corresponding to the requested ID
                    cannot be processed with the tools relative to the requested DOC type'''

    print("Returning probable content",flush=True)
    style_url : str = struct_data.xpath("//processing-instruction('xml-stylesheet')")[0].get("href")
    same_origin_mirror = style_url.replace("https://gitlab.tools.iit.cnr.it",f"{os.environ['ROOT_URL']}/mirror_gitlab_tools_iit_cnr_it")
    return Response(document_content.replace(style_url,same_origin_mirror),200,mimetype="text/xml")
