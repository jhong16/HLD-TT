# Languages used
Back-end: Python3.6+
Front-end: HTML, Javascript

# How to install:
1. Clone the repository into a folder
2. Install requirements
   1. ```pip install -r requirements.txt```

# How to run server:
 * Set up Python path
   * Linux: ```export PYTHONPATH=${PYTHONPATH}:<your clone path>/truth_tree```
 * Run web_server.py in the src folder and go to the ip address
   * ```python3.6 web_server.py```
   * Development Mode (Auto-Template Refresh) ```FLASK_APP=web_server_test.py FLASK_DEBUG=1 python3.6 -m flask run```
 * Insert commands into Command to create the tree
   * Try typing ```help```

# How to run cli:
 * Set up Python path
   * Linux: ```export PYTHONPATH=${PYTHONPATH}:<your clone path>/truth_tree```
 * Run cli.py in the src folder
   * ```python3.6 cli.py```

# How to run tests:
 * Set up Python path
   * Linux: ```export PYTHONPATH=${PYTHONPATH}:<your clone path>/truth_tree```
 * Move into tests folder
 * Run a tests file
   * Example: ```python3.6 tests.py```

# Current Supported Commands:
* add_root_formula
    * Add a "premise" to the truth tree
        * Command to add a & b as a premise: 
            * add_root_formula and(a,b)
        * Command to add c | (d & e) as a premise:     
            * add_root_formula or(c, and(d,e))
* add_formula
    * Add a formula to the current node
        * Command to add a | b:
            * add_formula or(a,b)
        * Command to add ac -> bd:    
            * add_formula if(ac,bd)
* go_to
    * Change the current node
        * Command to set node 2 as current node:
            * go_to 2
        * Command to set node 1 as current node:
            * go_to 1

* delete_formula
    * Delete a formula using the formula id
        * Command to delete formula 1:
            * delete_formula 1

* undo
    * Undo the last command
        * Command to undo
           * undo 

* redo
    * Redo a command
        * Command to redo
            * redo

* close
    * Close the current node using formula's in its ancestry
        * Closing current node using formula 5 and 3:
            * close 5 3

* branch
    * Branch on the current node using a formula
        * Command to branch on current node using formula 1:
            * branch 1

* mark_parent
    * Allow user to mark the parent of a formula
        * Command to set formula 5 parent as 3
            * mark_parent 5 1

* checkmark
    * Allow user to checkmark a formula after decomposing it
        * Command to checkmark formula 3
            * checkmark 3

* mark_open
    * Allow user to mark the current node as open
        * Command to mark open
            * Mark open

* check_all_closed:
    * Allow user to check if all branches have been closed properly
        * Command to check
            * check_all_closed

* reset:
    * Reset the tree. (WARNING will not be able to undo)
        * Reset
            * reset