**This Git repo may contain confidential information. Sharing its contents is prohibited.**

# Pyteria
<img src="https://github.com/Uraxii/pyteria/blob/main/Data/etc/logo.png?raw=true" width="200" height="200">
## About
This program is designed to scan setup.py file, idenitfy potenitally malicious code, and provide a severity rating.\
All generated reports are stored in /Modules/Reports\
   Readable HTML report is called 'report.html'

## Flags
|  --target    TARGET       Target file to run analysis on.\
|  --filters   FILTERS     Filter file to run target against.\
|  --outDir    PATH        Directory to store generated report in.\
|  --outName   NAME        Path to store generated report in.
|  --jsonDir   PATH        Directory to store generated json file.\
|  --jsonName  NAME        Name for generated json file.\
|  --keepNegatives         Retains extracted data when compared against filters for use in report. Use this to get a breakdown of what the target contains.\
|  --cssFile   PATH        Path to CSS file to pair with html report.\
|  --test                  Test report generation using a test file and test filters.\

## Usage
pyteria.py --target <path to target file>
