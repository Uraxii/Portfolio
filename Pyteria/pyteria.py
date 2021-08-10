from Modules import generate_report
from Modules import file_entropy_calculator
from os.path import abspath, dirname, join, exists
from pathlib import Path
import argparse

# To the future developers...
# I'm sorry for the mess you have inherited.

# FORMERLY the main.py file, renamed for aestetics


def main():
    # Arguemt stuff
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--target', help='Target file to run analysis on.', required=False)
    parser.add_argument(
        '--filters', help='Filter file to run target against.', required=False)
    parser.add_argument(
        '--outDir', help='Directory to store generated report in.', required=False)
    parser.add_argument(
        '--outName', help='Path to store generated report in.', required=False)
    parser.add_argument(
        '--jsonDir', help='Directory to store generated json file.', required=False)
    parser.add_argument(
        '--jsonName', help='Name for generated json file.', required=False)
    parser.add_argument(
        '--keepNegatives', help='Retains extracted data when compared against filters for use in report. Use this to get a breakdown of what the target contains.', required=False, action='store_false')
    parser.add_argument(
        '--cssFile', help='Path to CSS file to pair with html report.', required=False)
    parser.add_argument(
        '--test', help='Test report generation using a test file and test filters.', required=False, action='store_true')
    parser.add_argument(
        '--rollTheCredits', action='store_true')
    args = parser.parse_args()

    if args.rollTheCredits:
        __credit_roll()
        exit()

    # Want to rewitre these checks to be a little more efficient
    if not args.filters:
        args.filters = './Data/Filters/filters.json'

    if args.test:
        args.target = './Modules/Test Files/test_cases.py'
        args.filters = './Data/Filters/test_filters.json'
        args.outName = 'report_test.html'
        args.outDir = './Generated/Reports/Test-Report'

    if not args.outDir:
        args.outDir = './Generated/Reports/' + Path(args.target).stem
    if not args.outName:
        args.outName = Path(args.target).stem + "_report.html"

    if not args.jsonDir:
        args.jsonDir = './Generated/Json Data'
    if not args.jsonName:
        args.jsonName = Path(args.target).stem + '.json'

    json_path = args.jsonDir + '/' + args.jsonName

    if exists(json_path):
        json_path = generate_report.next_available_path(
            args.jsonName, args.jsonDir)

    extracted_data = generate_report.get_data(args.target)
    data_file = generate_report.aggrigate_data(
        extracted_data, json_path)
    filtered_data = generate_report.filter_data(
        data_file, args.filters, remove_negatives=args.keepNegatives)
    severity = generate_report.calculate_sevirity_score(filtered_data)
    file_entropy = file_entropy_calculator.entropy_calculator(args.target)
    generate_report.print_report(filtered_data, severity, file_entropy)

    etc_data_dir = './Data/etc'
    logo_file = etc_data_dir + '/logo.png'
    if not args.cssFile:
        args.cssFile = etc_data_dir + '/Reports/main.css'

    generate_report.generate_html_report(
        filtered_data, severity, file_entropy, args.outDir + '/' + args.outName)
    etc_file_tuples = [(args.cssFile, args.outDir+'/main.css'),
                       (logo_file, args.outDir + '/pyteria-logo.png')]
    generate_report.copy_report_etc(etc_file_tuples)


def __credit_roll():
    import time

    def __slow_print(string):
        for character in string:
            print(character, end="", flush=True)
            time.sleep(0.1)
        print()

    # Contributers, add names here.
    contributors = {
        "EMU, IA 495, 2021":
            [
                "Brandon Paul",
                "Alex Peplinski",
                "Antonio Bally",
                "Kyle Purchase"
            ],
        # <---- Put your names here when you finish your project.
    }

    __slow_print("--- PYTERIA CONTRIBUTORS ---")
    for year, nerds in contributors.items():
        __slow_print(year)
        time.sleep(0.5)
        for nerd in nerds:
            __slow_print("\t- "+nerd)
            time.sleep(0.5)


if __name__ == '__main__':
    main()
