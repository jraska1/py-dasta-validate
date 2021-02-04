
import os
import click
import requests
import sys
from lxml import etree
from io import BytesIO
from bs4 import BeautifulSoup

DTD_DIR = '.'
DTD_URL = 'http://ciselniky.dasta.mzcr.cz/CD_DS3/dtd/historie/'
VERSION_DTD_MAPPING_URL = "http://ciselniky.dasta.mzcr.cz/CD_DS3/hypertext/WWBLJ.htm"
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def set_verbose(ctx, param, value):
    click.get_current_context().obj = {'verbose': value}


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('dtd_file', '--dtd', type=click.File(), help='DTD file to validate against')
@click.option('dtd_dir', '--dtd-dir', default=DTD_DIR, show_default=True, help='Local file system directory, where can be DTD found')
@click.option('dtd_url', '--dtd-url', default=DTD_URL, show_default=True, help='Web URL base, where can be DTD found')
@click.option('-v', '--verbose', count=True, callback=set_verbose, expose_value=False, help='To be more verbose')
@click.argument('src', type=click.File('rb'))
def main(dtd_file, dtd_dir, dtd_url, src):
    """
    Validates DASTA ver.3 document against appropriate DTD.
    """

    try:
        doc = etree.parse(src)
    except etree.XMLSyntaxError as e:
        verbose("document cannot be parsed, error detail: '{0}'".format(e))
        sys.exit(-1)
    else:
        verbose("document parsed")

    if dtd_file:
        verbose(f"validation against file {dtd_file.name}")
        dtd = etree.DTD(dtd_file)
    else:
        dtd_name = dtd_file_name(doc)
        if dtd_name:
            with dtd_source(dtd_name, dtd_dir, dtd_url) as f:
                dtd = etree.DTD(f)
        else:
            verbose("cannot find out DTD file name, validations is not possible")
            sys.exit(-1)

    try:
        dtd.assertValid(doc)
    except etree.DocumentInvalid as e:
        verbose("document is not valid, error detail: '{0}'".format(e))
        sys.exit(-1)
    else:
        verbose("document is valid")



def dtd_file_name(doc):
    """
    Provides DTD file name based on docinfo system_url or /dasta/@version_ds attribute.

    :param doc:     parsed document
    :return:        DTD file name
    """
    if doc.docinfo.system_url:
        return os.path.basename(doc.docinfo.system_url)
    else:
        version = doc.getroot().attrib.get('verze_ds')
        file_name = suck_dtd_file_name(version)
        verbose(f"document version: {version}, dtd file name: {file_name}", 2)
        return file_name


def dtd_source(file_name, dir_name, dir_url):
    """
    Returns DTD content as file-like object.

    :param file_name:   DTD file name
    :param dir_name:    directory in local filesystem to search for DTD file
    :param dir_url:     URL base to download DTD file
    :return:            DTD as file-like object
    """
    file_path = os.path.join(dir_name, file_name)
    if os.path.isfile(file_path):
        verbose(f"validation against file {file_path}")
        return open(file_path, 'rb')

    resp = requests.get(dir_url + file_name)
    if resp.ok:
        verbose(f"validation against URL {dir_url + file_name}")
        resp.encoding = 'windows-1250'
        return BytesIO(resp.text.encode('utf-8'))
    else:
        verbose(f"validation against empty DTD")
        return BytesIO(b"")


def suck_dtd_file_name(version):
    """
    Sucks DTD file name from standard web page based on version number.

    @param version:  version number
    @return:         DTD file name
    """
    if version.startswith('0'):
        version = version[1:]
    req = requests.get(VERSION_DTD_MAPPING_URL)
    if req:
        soup = BeautifulSoup(req.content, 'html.parser')
        for row in soup.table.find_all("tr"):
            if row.span.text == version:
                return "ds0{}.dtd".format(row.find_all("span")[-1].text.split()[0].replace('.', ''))
    return None


def verbose(message, level=1):
    """
    Write a message to stdout, if the verbose flag is set on.

    :param message: message to be written
    :param level:   required level of verbosity
    """
    if click.get_current_context().obj and click.get_current_context().obj.get('verbose', 0) >= level:
        print(message)


if __name__ == '__main__':
    main()
