Controller v1.5 for OKBQA
=============================

This module links inputs and outputs of all modules (TGM, DM, QGM) and returns final answers of an input question string using AGM embedded in the controller. This module supports the address configuration of each module and SPARQL endpoints.
The controller v1.5 is enhanced version of the controller v1.0 w.r.t. concurrency control and load control. The capability of load control is achieved by adjusting the number of answers to be returned by the additional configuration field ("answer_num"). By adjusting the number of answers, testers can trade off the output time against the output size.


Prerequisite
-----
You need to install Python v2.7

Interpreter
-----
Python v2.7

Install
-----
(after cloning)
bundle install

Deploy
-----
python controller_rest.py

Input
-----

* A question string: a question to be answered for users 
* A Language: a language of a question string
* Configuration: addresses of template generation modules (TGMs), disambiguation modules (DMs), and query generation modules (QGMs), the upper limit of the size of answers to be returned

Output
------

* Log: the internal log message to be used for tracing the cause of errors
* Answers: the final answers obtained from the pipeline with TMs, DMs, QGMs, and answer generation modules

AUTHOR(S)
---------

* Jiseong Kim, MachineReadingLab@KAIST

License
-------

Released under the MIT license (http://opensource.org/licenses/MIT).