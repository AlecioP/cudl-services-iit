# CUDL services IIT

IIT ( Istituto di Informatica e Telematica) implementation of an API which our instance of cudl-viewer calls to get all the data shown within the website.

## Entrypoints


`/v1/transcriptions/<path>`

Serves static html pages extracted from manuscript's TEI xml `<facsimile>` section using **cudl-data-processing-xslt** automatic tool. 

*Later the API could serve HTML pages dynamically generated using facsimile XML schemas and related stylesheets. (Manuscript page's xml digital version, trasformed with the right XSL stylesheet)*

`/v1/schema/<document-category>/<year-version>/schema.xsd`

Here are hosted the XML schema (xsd) files used to validate xml files containing structured data extracted from certain categories of documents in our archive which are basically forms (not all documents in archive are forms, therefore structuring the data doesn't make sense). Parameter `<document-category>` can have value **tabella** , **fascicolo** , **modula**. Parameter `<year-version>` is more of an informative parameter. Do not expect to insert any year and always have some data. To learn more about this parameter read `<xs:annotation>` for attribute **form-year** in schema's source file.

### Internal notes

Made a soft symbolic link to project directory in the workspace of a third party XML enterprise editor. The command was:

~~~bat
mklink /d c:/Users/<USER>/<XML-EDITOR-WORKSPACE>/Cartella\ Schema c:/Users/<USER>/<PATH-HERE>/data/schema
~~~