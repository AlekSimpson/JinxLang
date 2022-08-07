Better scopes:
* Stored centrally
** So that every scope that is created can be monitored and debugged

* Rework how the Parser parses DotNode operations
** Sould not hold the entire reference chain in one DotNode
** Should be one DotNode that leads to n-number of DotNodes, each comprised of one LHS and RHS
** This makes it easier to emit the IR code

* should add linked list data type to store complex types inside of arrays

* Name ideas
** Breeze

