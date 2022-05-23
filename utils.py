import argparse, os, zipfile
from androguard.core.bytecodes.axml import AXMLPrinter

def get_package_name(apk_file):
    return AXMLPrinter(extract_file_from_apk(apk_file, 'AndroidManifest.xml')['byte_value']).get_xml_obj().attrib['package']


def extract_file_from_apk(file_path, file_of_interest, destination=None):
    try:
        extract_file = {'name': os.path.basename(file_of_interest),
                        'byte_value': None}
        with zipfile.ZipFile(file_path, 'r') as zipObj:
            extract_file['byte_value'] = zipObj.read(file_of_interest, pwd=None)
            if destination:
                pathlib.Path(destination).parent.mkdir(parents=True, exist_ok=True)
                zip_info = zipObj.getinfo(file_of_interest)
                zip_info.filename = extract_file['name']
                zipObj.extract(zip_info,
                               os.path.join(destination),
                               pwd=None)
            return extract_file
    except Exception as e:
        raise e

def init_argparse():
    parser = argparse.ArgumentParser(
        usage="%(prog)s -D [DIRECTORY] --apk [APK_FILES]",
        description="Deobfuscate strings."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--apk', nargs='*',
        help=' apk  file or multiple if splitted.')
    group.add_argument('--pkg',  help='Package name of the application.')
    
    parser.add_argument('--dir',
        help='Directory of the jadx decompiled code. -> $ jadx -d dec_code example.apk',required=True)
    parser.add_argument('--config',
        help='config json with the classes', type=argparse.FileType('r'), required=True)
    return parser



#print(get_package_name(args.apk[0]))
