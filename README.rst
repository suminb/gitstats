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

.. code-block:: console

   pip install gitstats

Usage
=====

The following example shows how `gitstats` discovers all Git repositories
in the home directory to consolidate all commit logs.

Git Repository Analysis
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    gitstats analyze ~ > gitstats.json

The target directory may be a single repository.

.. code-block:: console

    gitstats analyze ~/work/project_x > gitstats.json

If you would like to exclude certain repositories, put a ``.exclude`` file in
each directory you want to exclude from the statistics. Note that the content
of the file is irrelevant.

Generating Commit Graphs
~~~~~~~~~~~~~~~~~~~~~~~~

`gitstats` generates annual commit graphs that are similar to what GitHub
shows on each user's page. However, the major difference is that `gitstats`
differentiates your commits from others based on your email address(es).

.. code-block:: console

    gitstats generate_graph gitstats.json 2017 --email ${your_email} > 2017.svg

If you have multiple email addresses, you may pass them as follows:

.. code-block:: console

    gitstats generate_graph gitstats.json 2017 --email ${your_email1} --email ${your_email2} > 2017.svg
