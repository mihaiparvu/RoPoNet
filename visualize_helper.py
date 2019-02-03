import json
import os
import csv
import unidecode


class Visualize:

    def __init__(self, input_file_path):
        self.input_file_path = input_file_path
        self.politicians = self._import_politicians()

    def _import_politicians(self):
        with open(self.input_file_path, encoding='utf8') as politicians_file:
            return json.load(politicians_file)

    def _create_header(self):
        header = []
        for politician, values in self.politicians.items():
            politician = unidecode.unidecode(politician)
            parties = []
            if 'switching_score' in values:
                ss = values['switching_score']
                del values['switching_score']
                for year, party_list in values.items():
                    for party in party_list:
                        if party not in parties:
                            parties.append(party)
                final = "%s SS=%.2f " % (politician, ss) + '[' + ' '.join(parties) + ']'
                header.append(final.replace(' ', '_'))
            else:
                print('Error! Switching Score not computed! Use an input file with computed score.')
                exit(0)
        return header

    def create_adj_matrix(self):
        # TODO - refactor this mess
        header = self._create_header()
        nb_of_pol = len(self.politicians) + 1
        adj_matrix = [[0 for _ in range(nb_of_pol)] for _ in range(nb_of_pol)]
        for i in range(nb_of_pol - 1):
            adj_matrix[0][i + 1] = header[i]
            for j in range(nb_of_pol - 1):
                adj_matrix[j + 1][0] = header[j]
        adj_matrix[0][0] = ''

        for politician1, membership1 in self.politicians.items():
            for year1, party_list1 in membership1.items():
                for party in party_list1:
                    for politician2, membership2 in self.politicians.items():
                        for year2, party_list2 in membership2.items():
                            if politician1 != politician2:
                                if year1 == year2:
                                    if party in party_list2:
                                        adj_matrix[list(self.politicians.keys()).index(politician1) + 1][
                                            list(self.politicians.keys()).index(politician2) + 1] = int(
                                            adj_matrix[list(self.politicians.keys()).index(politician1) + 1][
                                                list(self.politicians.keys()).index(politician2) + 1]) + 1
        return adj_matrix


if __name__ == '__main__':
    # TODO use commandline arguments

    path = os.path.join('outputs', 'politicians_switching_scores.json')
    visualize = Visualize(path)
    adj_mat = visualize.create_adj_matrix()

    with open('visualize%sadj_matrix.csv' % os.sep, 'w', newline='') as adj_matrix_file:
        writer = csv.writer(adj_matrix_file)
        writer.writerows(adj_mat)
    print('Created adjacency matrix to: %s' % os.path.abspath(
        'visualize%sadj_matrix.csv' % os.sep))
