
import os
import sys

import click
import requests
from lxml import etree
from bs4 import BeautifulSoup


XSD_DIR = './xsd'
XSD_URL = 'http://ciselniky.dasta.mzcr.cz/xmlschema/'
XSI_NAMESPACE = 'http://www.w3.org/2001/XMLSchema-instance'
XSI_PREFIX = "{" + XSI_NAMESPACE + "}"
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
VERSION_SCHEMA_MAPPING_URL = "http://ciselniky.dasta.mzcr.cz/CD_DS4/hypertext/WWBLK.htm"


def set_verbose(ctx, param, value):
    click.get_current_context().obj = {'verbose': value}


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('xsd_dir', '--xsd-dir', default=XSD_DIR, show_default=True, help='Local file system directory, where can be XSD found')
@click.option('-v', '--verbose', count=True, callback=set_verbose, expose_value=False, help='To be more verbose')
@click.argument('src', type=click.File('rb'))
def main(xsd_dir, src):
    """
    Validates DASTA ver.4 document against appropriate XSDs.
    """

    try:
        doc = etree.parse(src)
    except etree.XMLSyntaxError as e:
        verbose("document cannot be parsed, error detail: '{0}'".format(e))
        sys.exit(-1)
    else:
        verbose("document parsed")

    schema_def = pick_out_schema(doc, xsd_dir)
    schema = etree.XMLSchema(etree.XML(etree.tostring(schema_def)))
    verbose(etree.tostring(schema_def, pretty_print=True).decode(), 3)

    try:
        schema.assertValid(doc)
    except etree.DocumentInvalid as e:
        verbose("document is not valid, error detail: '{0}'".format(e))
        sys.exit(-1)
    else:
        verbose("document is valid")
    sys.exit(0)


def pick_out_schema(doc, xsd_dir):
    """
    Picks out XML schema from xsi:schemaLocation attribute of the root element

    @param doc:     parsed XML document
    @param xsd_dir: local directory where xsd can be found
    @return:        XML schema as a etree.Element object
    """
    loc = doc.getroot().attrib.get(XSI_PREFIX + "schemaLocation")

    schema_def = etree.Element("schema", attrib={
        "elementFormDefault": "qualified",
        "version": "1.0.0",
    }, nsmap={
        None: "http://www.w3.org/2001/XMLSchema"
    })

    if loc:
        loc = loc.split()
        for i in range(0, len(loc), 2):
            ns, uri = loc[i:i+2]
            file_name = os.path.join(xsd_dir, uri.split('/')[-1])
            if os.path.isfile(file_name):
                uri = file_name
            verbose(f"XML schema involved: ns={ns}, uri={uri}", 2)
            etree.SubElement(schema_def, "import", attrib={
                "namespace": ns,
                "schemaLocation": uri
            })
    else:
        version_number = doc.getroot().attrib.get('verze_ds')
        verbose(f"Dasta version number from document: {version_number}", 2)
        if defs := suck_schema_definitions(version_number, xsd_dir):
            for ns, uri in defs:
                verbose(f"XML schema involved: ns={ns}, uri={uri}", 2)
                etree.SubElement(schema_def, "import", attrib={
                    "namespace": ns,
                    "schemaLocation": uri
                })
    return schema_def


def suck_schema_definitions(version, xsd_dir):
    """
    Sucks schema definitions from standard web page based on version number.

    @param version: version number
    @param xsd_dir: local directory where xsd can be found
    @return:        list of tuples (namespace, schema-location)
    """
    if version.startswith('0'):
        version = version[1:]
    req = requests.get(VERSION_SCHEMA_MAPPING_URL)
    if req:
        schemas = None
        soup = BeautifulSoup(req.content, 'html.parser')
        for row in soup.table.find_all("tr"):
            if row.span.text == version:
                schemas = [p.text for p in row.find_all("td")[-2].find_all("p")]
                break
        verbose(f"Schemas for version number: {schemas}", 3)
        res = []
        for schema in schemas:
            uri = XSD_URL + schema
            file_name = os.path.join(xsd_dir, schema)
            if os.path.isfile(file_name):
                uri = file_name
            try:
                doc = etree.parse(uri)
                ns = doc.getroot().attrib.get('targetNamespace')
                if ns:
                    res.append((ns, uri))
            except etree.XMLSyntaxError as e:
                verbose("Schema cannot be parsed, error detail: '{0}'".format(e), 1)
        return res
    return None


def verbose(message, level=1):
    """
    Write a message to stdout, if the verbose flag is set on.

    @param message: message to be written
    @param level:   required level of verbosity
    """
    if click.get_current_context().obj and click.get_current_context().obj.get('verbose', 0) >= level:
        print(message)


if __name__ == '__main__':
    main()
