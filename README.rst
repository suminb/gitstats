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

Discover all Git repositories in the home directory to generate statistics.
Here your email address is used to differentiate your commits from others.

.. code-block:: console

    gitstats analyze --email ${your_email} ~

It may be a single Git repository.

.. code-block:: console

    gitstats analyze --email ${your_email} ~/work/project_x

If you would like to exclude certain repositories, put a ``.exclude`` file in
each directory you want to exclude from the statistics.

If you have multiple email addresses, you may pass them as follows:

.. code-block:: console

    gitstats analyze --email ${your_email1} --email ${your_email2} ~
