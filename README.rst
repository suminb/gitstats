Gitstat
=======

.. image:: https://travis-ci.org/suminb/gitstats.svg?branch=develop
   :target: https://travis-ci.org/suminb/gitstats

.. image:: https://coveralls.io/repos/github/suminb/gitstats/badge.svg?branch=develop
   :target: https://coveralls.io/github/suminb/gitstats?branch=develop

Visualizes overall code commits for multiple Git repositories. The red
indicates my own commits whereas the blue indicates your teammates'.

.. image:: http://s1.postimg.org/mrnwnla3j/2014.png


Installation
============

The latest code can be cloned from GitHub as follows:

.. code-block:: console

   git clone https://github.com/suminb/gitstats

We are planning to register our project to PyPi in the near future, so please
stay tuned. Once the repository has been cloned, ``gitstats`` can be installed
as follows:

.. code-block:: console

   pip install -e gitstats

Usage
=====

Discover all Git repositories in the home directory to generate statistics.

.. code-block:: console

    gitstats analyze ~

It may be a single Git repository.

.. code-block:: console

    gitstats analyze ~/dev/projectx

If you would like to exclude certain repositories, put a ``.exclude`` file in
each directory you want to exclude from the statistics.
