Gitstat
=======

Visualizes overall code commits for multiple Git repositories.

.. image:: http://s1.postimg.org/mrnwnla3j/2014.png

Usage
-----

Discover all Git repositories in the home directory to generate statistics.

.. code-block:: console

    python stat.py ~

It may be a single Git repository.

.. code-block:: console

    python stat.py ~/dev/projectx

If you would like to exclude certain repositories, put a ``.exclude`` file in
each directory you want to exclude from the statistics.
