MDL2LaTeX
=========

Ever dreamed of automatic LaTeX-conversion of your MDL files?
This script accepts [Stochpy](http://stompy.sourceforge.net/ )MDL files and churns out nicely-formatted, human readable LaTeX.
It does this by 'LaTeXifying' every single term in your reactions to a LaTeX representation.

Instructions
------------
Edit the `Makefile` inside of the root folder and change the PSCfile variable to the filepath of the the .psc (MDL model) file you want to convert. N.B. exclude .psc file extension!
Then run `make`

## Fractions in propensities ##
If the propensities in your functions contain fractions, place them in the beginnning of the propensity definition. Only this way, they will be rendered correctly

Example:
`TFactive/(TFactive+kX)*kmRNAsyn` instead of `kmRNAsyn*TFactive/(TFactive+kX)`

## Custom mappings ##
Unhappy with an automatic conversion the script provides? 
Supply your own mappings in the file `usersubs.txt` and they will be granted priority over the automatic mappings.

Dependencies
------------
Requires UNIX-utility make, Django for templatingStargazers github.
Has been successfully tested in various Linux environments.
