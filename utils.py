import json
import os


def get_unique_parties(politicians):
    unique_parties = set()
    for name in politicians.keys():
        for current_year, current_party_list in politicians[name].items():
            for i in current_party_list:
                unique_parties.add(i)

    return unique_parties


def export_politicians_to_json_file(data, filename='scraped_data'):
    with open('scraped_data%s%s.json' % (os.sep, filename), 'w',
              encoding='utf8') as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True, ensure_ascii=False)
        print('Exported JSON file to %s' % os.path.abspath('scraped_data%s%s.json' % (os.sep, filename)))
        print('Found %s politicians, members of the following unique political parties: %s ' % (
            len(data), ', '.join([x for x in get_unique_parties(data)])))
