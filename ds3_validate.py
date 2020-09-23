
import os
import click
import requests
import sys
from lxml import etree
from io import BytesIO

DTD_DIR = './dtd'
DTD_URL = 'http://ciselniky.dasta.mzcr.cz/CD_DS3/dtd/historie/'
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
        with dtd_source(dtd_file_name(doc), dtd_dir, dtd_url, verbose) as f:
            dtd = etree.DTD(f)

    res = dtd.validate(doc)
    verbose("document is valid" if res else "document is not valid")
    sys.exit(0 if res else -1)


def dtd_file_name(doc):
    """
    Provides DTD file name based on docinfo system_url or /dasta/@version_ds attribute.

    :param doc:     parsed document
    :return:        DTD file name
    """
    if doc.docinfo.system_url:
        return os.path.basename(doc.docinfo.system_url)
    else:
        return "ds{}.dtd".format(doc.getroot().attrib.get('verze_ds').replace('.', ''))


def dtd_source(file_name, dir_name, dir_url, verbose):
    """
    Returns DTD content as file-like object.

    :param file_name:   DTD file name
    :param dir_name:    directory in local filesystem to search for DTD file
    :param dir_url:     URL base to download DTD file
    :param verbose:     be more verbose
    :return:            DTD as file-like object
    """
    if os.path.isfile(file_name):
        verbose(f"validation against file {file_name}")
        return open(file_name, 'rb')

    file_name = os.path.basename(file_name)
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
