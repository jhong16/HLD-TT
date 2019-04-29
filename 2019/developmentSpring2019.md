# Goal
The goal of the project is to create a replacement or alternative to the
java TruthTree generator on BramHub.

# Development
Currently, the program allows for basic commands for making the truth tree.
Compared to the java program, users can checkmark off formulas after it has been successfully decompose.  
  
For this semester, the front end and back end was develop using Matt Peveler work as a base. The tree class was altered to allow for manual editing and verification for marking parents and checkmarking was added. The front end uses flask to give a view of the tree.

## Currently Known Bugs
* Mark_close is not edit safe
    * If a user closes a node based on two formula, and then delete one of the
    formula, the node would still be marked as closed.
* Mark_open is not edit safe
    * If a user were to verify a branch is open, then delete or add a formula
    which violate the branch being open, the branch would remain open.
* Form Resubmission is still allowed

# Possible Future Improvements
* Use a better formula parser
    * forsetti isn't the most reliable
* Print out the parent formula id after marking parent in Flask App
    * A Quality of Life change to allow users to know which formula has which parents
* More commands
    * Add commands such as edit and export
* Export and Import  Tree
    * In theory, the history in the TreeShell class can be exported text file
    * Then this text file can be used to recreate the tree
* Create an adapter that takes in formula input and change it into something forsetti can parse
    * Allow user to type (a & b) instead of and(a,b)
* Refactor to eliminate duplicates due to color classes, styles
* Re-integrate auto-solve truth tree from original fork
* Center the Tree in CSS
* Bi-conditionals should be tested more

    
