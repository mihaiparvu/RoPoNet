import json
import os
from utils import get_unique_parties

party_equivalency = {
    "PSDR": 1,
    "PDSR": 1,
    "PSD": 1,
    "ALDE": 2,
    "FSN": 3,
    "PD": 3,
    "PDL": 3,
    "PMP": 3,
    "UNPR": 4,
    "PNL": 5,
    "PNTCD": 6,
    "UDMR": 7,
    "PUNR": 8,
    "USR": 9,
    "PC": 10,
    "PRM": 11,
    "PAC": 12,
    "PDAR": 13,
    "PER": 14,
    "PP-DD": 15
}


class Computations:

    def __init__(self, input_file_path):
        self.input_file_path = input_file_path
        self.politicians = self._import_politicians()
        self.politicians_with_computed_ss = self._import_politicians()
        self.overall_party_performance = self._import_overall_party_performance()
        self.party_switcher_score_dictionary = {}

    def compute_politicians_switching_scores(self):
        for name in self.politicians.keys():
            switches = self._identify_party_switches(name)
            self.politicians_with_computed_ss[name]['switching_score'] = self._compute_politician_switching_score(
                switches)

    def compute_party_switcher_score(self):
        self.party_switcher_score_dictionary = self._build_party_switcher_score_dict()
        for party, items in self.party_switcher_score_dictionary.items():
            for year in items:
                if len(items[year]) > 1:
                    final_score = 1
                    for value in items[year]:
                        final_score *= value
                    final_score = final_score ** (1 / len(items[year]))
                    items[year] = final_score
                else:
                    items[year] = items[year][0]

    def _import_politicians(self):
        with open(self.input_file_path, encoding='utf8') as politicians_file:
            return json.load(politicians_file)

    @staticmethod
    def _import_overall_party_performance():
        with open('helper_data%soverall_party_performance.json' % os.sep) as overall_power_score_file:
            return json.load(overall_power_score_file)

    @staticmethod
    def _get_previous_party(dictionary, key):
        keys = list(dictionary.keys())

        index = keys.index(key) - 1
        if index < 0:
            return None

        return dictionary[keys[index]]

    def _identify_party_switches(self, name):
        # TODO - refactor this mess
        count_years_in_previous_party = 0
        output = []
        all_parties_member_of = self.politicians[name].items()
        for this_year, this_party_list in all_parties_member_of:
            count_years_in_previous_party += 1
            previous_party_list = self._get_previous_party(self.politicians[name], this_year)
            if previous_party_list:

                if len(this_party_list) > 1:
                    # party switch occurred current year
                    years_in_new_party = self._get_years_in_new_party(this_year, all_parties_member_of,
                                                                      this_party_list[-1])
                    switch = {'previous_party': this_party_list[0],
                              'years_in_previous_party': count_years_in_previous_party,
                              'switch_year': this_year,
                              'new_party': this_party_list[-1],
                              'years_in_new_party': years_in_new_party}
                    output.append(switch)
                    count_years_in_previous_party = 1  # reset for next iteration

                if len(previous_party_list) == 1 and len(
                        this_party_list) == 1 and previous_party_list != this_party_list:
                    # party switch occurred next year
                    years_in_new_party = self._get_years_in_new_party(this_year, all_parties_member_of,
                                                                      this_party_list[0])
                    switch = {'previous_party': previous_party_list[0],
                              'years_in_previous_party': count_years_in_previous_party - 1,
                              'switch_year': this_year,
                              'new_party': this_party_list[0],
                              'years_in_new_party': years_in_new_party}
                    output.append(switch)
                    count_years_in_previous_party = 1  # reset for next iteration
        return output

    @staticmethod
    def _get_years_in_new_party(year, parties_list, next_party):
        output = 0
        for party in parties_list:
            if int(party[0]) >= int(year):
                if next_party in party[1]:
                    output += 1
        return output

    def _compute_politician_switching_score(self, switches):
        politician_switching_score = 0
        for switch in switches:
            switching_type = self._compute_switching_type(switch['previous_party'], switch['new_party'])
            switching_weight = self._compute_switching_weight(switch['years_in_previous_party'],
                                                              switch['years_in_new_party'])
            switching_power = self._compute_switching_power(switch['new_party'], switch['previous_party'],
                                                            switch['switch_year'])
            politician_switching_score += switching_type * switching_weight * switching_power
        return politician_switching_score

    @staticmethod
    def _compute_switching_type(previous_party, new_party):
        return 0 if party_equivalency[previous_party] == party_equivalency[new_party] else 1

    @staticmethod
    def _compute_switching_weight(years_in_previous_party, years_in_new_party):
        return years_in_previous_party / years_in_new_party

    def _compute_switching_power(self, new_party, previous_party, year):
        return self.overall_party_performance[year][new_party] / self.overall_party_performance[year][previous_party]

    def _build_party_switcher_score_dict(self):
        unique_parties = get_unique_parties(self.politicians)
        party_switcher_score_dict = {}
        for party in unique_parties:
            party_switcher_score_dict[party] = {}
        for name in self.politicians.keys():
            switches = self._identify_party_switches(name)
            ss_score = self.politicians_with_computed_ss[name]['switching_score']
            if ss_score > 0:
                for switch in switches:
                    try:
                        party_switcher_score_dict[switch['previous_party']][switch['switch_year']].append(ss_score)
                    except KeyError:
                        party_switcher_score_dict[switch['previous_party']][switch['switch_year']] = []
                        party_switcher_score_dict[switch['previous_party']][switch['switch_year']].append(ss_score)
        return party_switcher_score_dict


if __name__ == '__main__':
    # TODO use commandline arguments

    path = os.path.join('scraped_data', 'scraped_data.json')
    computations = Computations(path)
    computations.compute_politicians_switching_scores()
    with open('outputs%spoliticians_switching_scores.json' % os.sep, 'w', encoding='utf-8') as ss_file:
        json.dump(computations.politicians_with_computed_ss, ss_file, ensure_ascii=False, indent=2, sort_keys=True)
    print('Computed Politicians Switching Scores and exported results to: %s' % os.path.abspath(
        'outputs%spoliticians_switching_scores.json' % os.sep))

    computations.compute_party_switcher_score()
    with open('outputs%sparty_switcher_score.json' % os.sep, 'w', encoding='utf-8') as party_switcher_score_file:
        json.dump(computations.party_switcher_score_dictionary, party_switcher_score_file, ensure_ascii=False, indent=2,
                  sort_keys=True)
    print('Computed Party Switcher Score and exported results to: %s' % os.path.abspath(
        'outputs%sparty_switcher_score.json' % os.sep))
