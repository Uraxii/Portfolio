# Namespacing issue when running from main if 'from Modules' is not used.
#   But the 'from Modules' breaks running this script directly
if __name__ == '__main__':
    import extract_data
else:
    from Modules import extract_data

from os.path import abspath, dirname, join, exists
from pathlib import Path
from shutil import copyfile
import json

entropy_threshhold_value = 5.296014741


def get_data(file_path):
    """
    Purpose: Collects formatted data from ast node tree
    """
    ast_node_tree = extract_data.generate_tree(file_path)
    import_data = extract_data.get_imports(ast_node_tree)
    method_call_data = extract_data.get_method_calls(ast_node_tree)
    constant_data = extract_data.get_constants(ast_node_tree)
    formatted_all_data = {}
    formatted_all_data["imports"] = extract_data.format_imports(import_data)
    formatted_all_data["method_calls"] = extract_data.format_calls(
        method_call_data)
    formatted_all_data["constants"] = extract_data.format_constants(
        constant_data)

    return formatted_all_data


def next_available_path(f_name, f_dir):
    """
    Purpose: Finds the next avaialable file name number for a file
    """
    path_pattern = f_dir + '/' + f_name

    if exists(path_pattern):
        extension_start = f_name.index('.')
        f_name = f_name[:extension_start] + \
            '-%s' + f_name[extension_start:]
        path_pattern = f_dir + '/' + f_name

        i = 1
        while exists(path_pattern % i):
            i = i * 2

        a, b = (i//2, i)
        while a + 1 < b:
            c = (a+b) // 2
            if exists(path_pattern % c):
                a, b = (c, b)
            else:
                a, b = (a, c)

        path_pattern = path_pattern % b

    return path_pattern


def aggrigate_data(extracted_data, json_out):
    """
    Purpose: places extracted data into a list dictionaries and appends them to a .json file.
    """

    json_out_dir = Path(json_out).parent

    try:
        Path(json_out_dir).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print("ERROR CANNOT JSON DATA FILE.\n\tINFO:", e)
        exit()

    try:
        with open(json_out, 'a') as report:
            report.write(json.dumps(extracted_data))
    except Exception as e:
        print("ERROR: CANNOT OPEN FILE.\n\tINFO:", e)
        print("Exiting...")
        exit()

    return json_out


def filter_data(json_data_file, filters_file, remove_negatives=True):
    """
    Purpose: compairs generated report with Filters IOA/IOC
    TO DO: try, except file reading
    """
    try:
        with open(json_data_file, 'r') as _data_file:
            report_list = json.load(_data_file)

        with open(filters_file, 'r') as _filter_file:
            filter_list = json.load(_filter_file)
    except Exception as e:
        print("ERROR: CANNOT OPEN FILE.\n\tINFO:", e)
        print("Exiting...")
        exit()

    match_list = []

    try:
        import_list = compare_filters(
            "imports", report_list, filter_list, remove_negatives)
        match_list.extend(import_list)
    except:
        print("No imports to report...")
    try:
        method_call_list = compare_filters(
            "method_calls", report_list, filter_list, remove_negatives)
        match_list.extend(method_call_list)
    except:
        print("No method_calls to report...")

    constant_list = compare_filters(
        "constants", report_list, filter_list, remove_negatives)
    match_list.extend(constant_list)

    return match_list


def compare_filters(target_kind, target_dict, filter_dict, negatives):
    filter_items = []
    for extracted_k, extracted_v in target_dict[target_kind].items():
        found_match = False
        extracted_item = extracted_v
        extracted_item["note"] = ""
        extracted_item["severity"] = '-1'
        for filter_k, filter_v in filter_dict[target_kind].items():
            if extracted_k == filter_k:
                found_match = True
                extracted_item["note"] = filter_v["note"]
                extracted_item["severity"] = filter_v["severity"]
                filter_items.append(extracted_item)
                break

        if not negatives and not found_match:
            filter_items.append(extracted_item)

    return filter_items


def calculate_sevirity_score(match_list):
    """
    Purpose: Calculates a severy score
    """
    try:
        # This sorts the match_list dicts by severity and returns the highest value as an int
        max_score = int(sorted(
            match_list, key=lambda k: k['severity'])[-1]['severity'])
    except Exception as e:
        print(
            "ERROR: SEVERITY SCORE ERROR, SETTING TO DEFAULT VALUE OF 0.\n\tINFO:", e)
        max_score = 0

    return max_score


def print_report(match_list, severity_score, entropy_value):
    """
    Purpose: prints matches to the STDOUT
    """
    print("Entropy Value: {entropy:.2f}".format(entropy=entropy_value))
    if entropy_value > entropy_threshhold_value:
        print("!!!WARNING!!! Entropy value above 2 standard devation threshold")
    print("Sevity Score: {severity:.2f}".format(severity=severity_score))
    print("Imports:")
    for item in match_list:
        # if item_counter % 2 == 0 :
        #   print ("\n", end="")
        if item["type"] == "import":
            print(" "*2 + "{value}".format(value=item["value"]))
            if not item["note"] == "":
                print(" "*4, "Note:", item["note"])

    print("Methods:")
    for item in match_list:
        if item["type"] == "method_call":
            print(" "*2 + "{value}".format(value=item["value"]))
            print(" "*2, "- call count:", item["count"])
            if not item["note"] == "":
                print(" "*4, "Note:", item["note"])

    print("Constants:")
    for item in match_list:
        if item["type"] == "constant":
            print(" "*2 + "{value}".format(value=item["value"]))
            if not item["note"] == "":
                print(" "*4, "Note:", item["note"])


def generate_html_report(match_list, severity_score, entropy_value, html_file):
    """
    Purpose: Makes HMTL file containing report data
    Note: HEY THIS IS SUSEPTABLE TO AN XSS ATTACK FROM THE AST NODE CONSTANT DATA. FIX THAT.
    """
    html_report_path = Path(html_file).parent

    try:
        Path(html_report_path).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print("ERROR CANNOT CREATE REPORT OUTPUT PATH.\n\tINFO:", e)
        exit()

    try:
        with open(html_file, 'w+') as report_file:
            html_code = """<!DOCTYPE html> <!-- HTML 5 DOCTYPE Declarations-->
            <!-- Webpage code written by: Brandon, Alex -->
            <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
            <head>
                <link rel="stylesheet" href="main.css">
                <title>Secure-pip report</title>
                <meta charset="utf-8">
            </head>
                <header>
                    <div id="logo">
                        <img src="pyteria-logo.png" alt="logo">
                    </div>
                </header>
            <body>
                <div id="container">
                    <!-- Use the main area to add the main content of the webpage -->
                    <main>
                        <section>"""
            report_file.write(html_code + "\n")
            report_file.write("<h2>Severity score: {severity:.2f}<h2>".format(
                severity=severity_score) + "\n")
            report_file.write("<h2>Entropy Value: {entropy:.2f}<h2>".format(
                entropy=entropy_value) + "\n")
            if entropy_value > entropy_threshhold_value:
                report_file.write(
                    "!!!WARNING!!! Entropy value above 2 standard devation threshold")
            report_file.write("\t"*5 + "<h2>Imports:</h2>" + "\n")

            for item in match_list:
                # if item_counter % 2 == 0 :
                #   print ("\n", end="")
                if item["type"] == "import":
                    report_file.write("\t"*6 + "<article>" + "\n" + "\t"*7 + "<h4>" + "\n" +
                                      "\t"*8 + str(item["value"]) + "\n" + "\t"*7 + "</h4>" + "\n")
                    if not item["note"] == "":
                        report_file.write("\t"*7 + "<p>"+"\n" + "\t"*8 + "Note: " + str(
                            item["note"]) + "\n" + "\t"*7 + "</p>")

                    report_file.write("\n" + "\t"*6 + "</article>" + "\n")

            report_file.write("\t"*5 + "<h2>Methods:</h2>" + "\n")

            for item in match_list:
                if item["type"] == "method_call":
                    report_file.write("\t"*6 + "<article>" + "\n" + "\t"*7 + "<h4>" + "\n" +
                                      "\t"*8 + str(item["value"]) + "\n" + "\t"*7 + "</h4>" + "\n")
                    report_file.write("\t"*7 + "<p>"+"\n" + "\t"*8 + "- call count: " +
                                      str(item["count"]) + "\n" + "\t"*7 + "</p>" + "\n" + "\t"*6 + "\n")
                    if not item["note"] == "":
                        report_file.write("\t"*7 + "<p>"+"\n" + "\t"*8 + "Note: " + str(
                            item["note"]) + "\n" + "\t"*7 + "</p>")

                    report_file.write("\n" + "\t"*6 + "</article>" + "\n")

            report_file.write("\t"*5 + "<h2>Constants:</h2>" + "\n")
            for item in match_list:

                if item["type"] == "constant":
                    report_file.write("\t"*6 + "<article>" + "\n" + "\t"*7 + "<h4>" + "\n" +
                                      "\t"*8 + str(item["value"]) + "\n" + "\t"*7 + "</h4>" + "\n")

                    if not item["note"] == "":
                        report_file.write("\t"*7 + "<p>"+"\n" + "\t"*8 + "Note: " + str(
                            item["note"]) + "\n" + "\t"*7 + "</p>")

                    report_file.write("\t"*7 + "<p>"+"\n" + "\t"*8 + "SHA256: " + str(
                        item["SHA256"]) + "\n" + "\t"*7 + "</p>")

                    report_file.write("\n" + "\t"*6 + "</article>" + "\n")
            html_code = """
                        </section>
                    </main>
                    <!-- Use the footer area to add webpage footer content -->
                    <footer>

                    </footer>
                </div>
            </body>
            </html>
            """
            report_file.write(html_code + "\n")

    except Exception as e:
        print("ERROR: CANNOT OPEN FILE.\n\tINFO:", e)


def copy_report_etc(etc_file_tuple_list):
    """
    Purpose: Copy etc files like logos or CSS files to report location
    Arguments: etc_file_tuple_list, list of tuples (<origianl path>, <target path>)
    """
    try:
        for etc_file in etc_file_tuple_list:
            copyfile(etc_file[0], etc_file[1])
    except Exception as e:
        print("ERROR: CANNOT COPY ETC FILES TO REPORT DIR.\n\tINFO:", e)


def report_test():
    """
    Purpose: Tests report genreation
    """
    test_file = abspath(
        join(dirname(__file__), './Test Files/test_cases.py'))
    extracted_data = get_data(test_file)
    test_json_data_dir = filters_file = abspath(
        join(dirname(__file__), '../Generated/Json Data'))
    test_json_data_name = 'generate_report_test_data.json'
    test_json_data_path = next_available_path(
        test_json_data_name, test_json_data_dir)
    data_file = aggrigate_data(
        extracted_data, test_json_data_path)
    filters_file = abspath(
        join(dirname(__file__), '../Data/Filters/test_filters.json'))
    filtered_data = filter_data(data_file, filters_file)
    severity = calculate_sevirity_score(filtered_data)
    print_report(filtered_data, severity, 3)
    test_report_path = abspath(
        join(dirname(__file__), '../Generated/Reports/Generate Report Test/generate_report_test_report.html'))
    generate_html_report(filtered_data, severity, 0, test_report_path)


if __name__ == '__main__':
    report_test()
