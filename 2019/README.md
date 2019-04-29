# Handy Logic Doodahs-Truth Trees Manual Creation
## Authors
2016:
Matt Peveler

2019:
Ji hann Hong
Terry Nguyen

## About
This is a flask app (with a python module backing it) that can be used to manually create a truth tree. 

This project is built off of Matt Peveler's Handy Logic Doodas-Truth Trees program.
https://github.com/Bram-Hub/HLD-TT

GitLab repository.
https://gitlab.com/GHanSolo42/truth_tree

![Flask App](https://raw.githubusercontent.com/MasterOdin/TruthTrees/master/static/screenshot.png)

It uses a functional format for inputting logical formulas. This is the base identity for inputs:
```
A
not(A)
and(A, B)
or(A, B)
if(A, B)
iff(A, B)
```
where `A` and `B` can either be atomic statements or a functional operator. All operators are either unary (not) or binary (and, or, if, iff) and there is no support for a generalized notation. This means that ```and(A, B, C)``` will thrown an error.
