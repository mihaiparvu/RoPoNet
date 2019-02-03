============================
Romanian Politicians Network
============================
.. contents::

Introduction
------------

This project can help explore the party switching in Romania from 1990-2018 by providing
tools to extract the data from an official source, the cdep.ro_ website, and run some computations on
it afterwards. The obtained results are:

- at an individual (politcian) level - a Switcher Score (SS)

- at an organizational (party) level - a Party Switcher Score (PSS)

A previous version of this project was used to obtain the data from the article `Exploring Party Switching in the
Post-1989 Romanian Politicians Network from a Complex Network Perspective
<https://www.ceeol.com/search/article-detail?id=707805>`_, published in the `Romanian Journal of Political Sciences`_.

Installation
------------
For running the code you only need Python 3 and the following packages: BeautifulSoup, requests and unidecode.
You can easily install them with pip::

    pip install beautifulsoup4 requests unidecode

Usage
-----
There are two commands you need to run::

    python scraper.py

This will extract by default data on the all members of the Romanian Chambers of Deputies from all legislatures from
1990-2018 (from the `official website`_) and it will dump them in a JSON file in `scraped_data` folder in root of the
project. You can change the arguments of the ``extract_for_legislation`` method to configure it to grab only a specific
legislation, or a year of a specific legislation.

The computations will take the `scraped_data.json` file as an input and can be run using the command::

    python computations.py

This will compute the Politicians Switcher Score (SS) and Party Switching Scores (PSS) and save them as JSON files
in the `outputs` folder. The algorithms used for the calculations are described below in the `Algorithm`_
section.

Data Format
-----------
The scraper will extract the data in the following format::

    {
        "politician_name1": {
            "year1" : list_of_parties_member_of,
            "year2" : list_of_parties_member_of,
            ...
            },
         "politician_name2": {
         ...
    }

An example is available in the `scraped_data` directory of the project.


After computing the Switcher Score a new field ``switching_score`` will be
added to each member::

    {
        "politician_name1": {
            "year1" : list_of_parties_member_of,
            ...
            "switching_score": 1.1210526315789473
            },
        ...
    }

The Party Switching Score computation will output a file in this format::

    {
        "party_name1": {
            "year1": 0.2303764710646282,
            "year2": 0.6990084309896356,
            ...
            },
         "party_name2":
         ...
     }

For the missing years, the value is ``0``.

Examples are available in the `outputs` directory of the project.

Algorithm
---------
A Politician's Switcher Score is computed using the following formula:

.. image:: https://raw.githubusercontent.com/mihaiparvu/RoPoNet/master/images/ss.gif

Where `SSx` is the individual politician switching score; `i` is the switch index for
politician `x`. At switch `i` politician goes from `ppi` (previous party) to `npi` (next party).

Switching type - `st`:

.. image:: https://raw.githubusercontent.com/mihaiparvu/RoPoNet/master/images/st.gif

Switching weight - `sw`:

.. image:: https://raw.githubusercontent.com/mihaiparvu/RoPoNet/master/images/sw.gif

Switching power, `sp`, of the parties:

.. image:: https://raw.githubusercontent.com/mihaiparvu/RoPoNet/master/images/sp.gif

This is computed externally of this repository and is imported from the
`overall_party_performance.json` from `helper_data` folder. For more information on how
the overall party performance is calculated you can check this article_ from
the `Romanian Journal of Political Sciences`_.

The Party Switcher Score is calculated as the geometric mean of the individual politicians'
switcher score, weighted by the size of the party:

.. image:: https://raw.githubusercontent.com/mihaiparvu/RoPoNet/master/images/pss.gif

It is only computed for the parties that have switchers.

Visualizing
-----------

This project also contains a helper method that transforms the Politicians
Switcher Scores computation output into an adjacency matrix in CSV format, that can be used
for easily visualization as a graph network.

Simply run::

    python visualize_helper.py

Note that it can take a while to generate the matrix depending on the configuration on the computer that is running on
and the number of politicians in the JSON file.

Such a tool that is capable of importing and displaying the CSV file is - for instance - Gephi_.


.. _article: https://www.ceeol.com/search/article-detail?id=707805
.. _Romanian Journal of Political Sciences: http://www.sar.org.ro/polsci/
.. _official website: http://cdep.ro
.. _cdep.ro: http://cdep.ro
.. _Gephi: https://gephi.org/

Acknowledgements
----------------
Many thanks to Silvia Fierascu (`@silviafierascu <https://github.com/silviafierascu>`__) who authored
most of the article_ and to Alexandru Topirceanu and Mihai Udrescu from the Department of Computer and Information
Technology, Politehnica University of Timisoara, Romania.
