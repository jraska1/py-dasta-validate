# py-dasta-validate
Validation tools for DASTA ver.3 and ver.4 written in python.

## How to install scripts on your host
The easiest way is to clone the GitHub repository and build virtual environment for launching the script:
```
cd <some directory on your choice>
git clone https://github.com/jraska1/py-dasta-validate.git
cd py-dasta-validate
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## ds3-validate - How to get general overview of script features
To launch the script, you have to activate the venv and run it as python script.
For argument and options overview, use -h or --help option as follows:

```
(.venv) [raska@localhost py-dasta-validate]$ python ds3_validate.py --help
Usage: ds3_validate.py [OPTIONS] SRC

  Validates DASTA ver.3 document against appropriate DTD.

Options:
  --dtd FILENAME  DTD file to validate against
  --dtd-dir TEXT  Local file system directory, where can be DTD found
                  [default: ./dtd]

  --dtd-url TEXT  Web URL base, where can be DTD found  [default:
                  http://ciselniky.dasta.mzcr.cz/CD_DS3/dtd/historie/]

  -v, --verbose   To be more verbose
  -h, --help      Show this message and exit.
```

As an example, how it works, can be:
```
(.venv) [raska@localhost py-dasta-validate]$ python ds3_validate.py -v data/dasta3-01.xml 
document parsed
validation against URL http://ciselniky.dasta.mzcr.cz/CD_DS3/dtd/historie/ds032002.dtd
document is valid
```

## ds4-validate - How to get general overview of script features
To launch the script, you have to activate the venv and run it as python script.
For argument and options overview, use -h or --help option as follows:

```
(.venv) [raska@localhost py-dasta-validate]$ python ds4_validate.py --help
Usage: ds4_validate.py [OPTIONS] SRC

  Validates DASTA ver.4 document against appropriate XSDs.

Options:
  --xsd-dir TEXT  Local file system directory, where can be XSD found
                  [default: ./xsd]

  -v, --verbose   To be more verbose
  -h, --help      Show this message and exit.
```

As an example, how it works, can be:
```
(.venv) [raska@localhost py-dasta-validate]$ python ds4_validate.py -v data/dasta4-01.xml 
document parsed
XML schema involved: ns=urn:cz-mzcr:ns:dasta:ds4:ds_dasta, uri=http://ciselniky.dasta.mzcr.cz/xmlschema/ds_dasta-4.03.21.xsd
XML schema involved: ns=urn:cz-mzcr:ns:dasta:ds4:ds_ip, uri=http://ciselniky.dasta.mzcr.cz/xmlschema/ds_ip-4.10.02.xsd
document is valid
```
