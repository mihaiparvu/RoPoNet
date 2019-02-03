import requests
from bs4 import BeautifulSoup
from utils import export_politicians_to_json_file

legislations = [('1990', '1992'),
                ('1992', '1996'),
                ('1996', '2000'),
                ('2000', '2004'),
                ('2004', '2008'),
                ('2008', '2012'),
                ('2012', '2016'),
                ('2016', '2018')]


class Scraper:

    def __init__(self):
        self.politicians = {}

    def extract_for_legislation(self, legislation, only_year='all'):
        if only_year != 'all' and int(legislation[0]) < int(only_year) > int(legislation[1]):
            raise ValueError('Invalid value for `per_year`!')
        page = requests.get('http://cdep.ro/pls/parlam/structura2015.de?leg=%s' % legislation[0])
        soup = BeautifulSoup(page.text, 'html.parser')
        tables = soup.find_all("div", attrs={"class": "grup-parlamentar-list grupuri-parlamentare-list"})

        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if cells:
                    name = cells[1].text
                    try:
                        membership_dict = self.politicians[name]
                    except KeyError:
                        membership_dict = {}
                    if legislation == ('2008', '2012') or legislation == ('2012', '2016'):
                        party = cells[4].text.strip('\n')
                    else:
                        party = cells[3].text.strip('\n')
                    member_from = member_until = None
                    # if first table
                    if tables.index(table) == 0:
                        if legislation == ('2008', '2012') or legislation == ('2012', '2016'):
                            # table inconsistency on cdep.ro
                            try:
                                member_from = cells[5].text.split('.')[-1]
                            except IndexError:
                                continue
                        else:
                            member_from = cells[4].text.split('.')[-1]
                    else:
                        if legislation == ('2008', '2012') or legislation == ('2012', '2016'):
                            # table inconsistency on cdep.ro
                            try:
                                member_until = cells[6].text.split('.')[-1]
                            except IndexError:
                                continue
                        else:
                            member_until = cells[4].text.split('.')[-1]

                    party = self._parse_party_names(party)
                    if party == 'neafiliat' \
                            or party == 'Minorităţi' \
                            or party == 'Minoritati' \
                            or party == 'Mino.' \
                            or party == 'Prog.' \
                            or party == 'Socialist' \
                            or party == 'Neafiliaţi' \
                            or party == '':
                        # ignore them
                        continue
                    years_list = list(range(int(legislation[0]), int(legislation[1]) + 1))
                    for year in years_list:
                        if only_year != 'all' and str(year) != only_year:
                            continue
                        if member_from:
                            if str(year) < member_from:
                                continue
                        if member_until:
                            if str(year) > member_until:
                                continue
                        try:
                            if party not in membership_dict[str(year)]:
                                membership_dict[str(year)].append(party)
                        except KeyError:
                            membership_dict[str(year)] = []
                            membership_dict[str(year)].append(party)

                    if membership_dict:
                        self.politicians[name] = membership_dict

    @staticmethod
    def _parse_party_names(party):
        if party == 'PD-L':
            party = 'PDL'
        if party == 'USD-PD':
            party = 'PD'
        if party == 'USD-PSDR':
            party = 'PSDR'
        if party == 'Ecologist-SD':
            party = 'PER'
        if party == 'PNŢCD/PER':
            party = 'PNTCD'
        if party == 'PNŢCD':
            party = 'PNTCD'
        if party == 'PL\'93/PAC':
            party = 'PAC'
        if party == 'PSD (membru UNPR)':
            party = 'PSD'
        return party


if __name__ == '__main__':
    # TODO use commandline arguments

    scraper = Scraper()
    for i in range(len(legislations)):
        # extract for all legislations
        scraper.extract_for_legislation(legislations[i])
    politicians = scraper.politicians
    export_politicians_to_json_file(politicians)
