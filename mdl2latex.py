import re
import logging
import os
logging.basicConfig(level=logging.DEBUG)
from pprint import pprint as pp
import django
from django.template import Template, Context

# Define dictionary of user definable substitutions which will be given
# the highest substitution priority
customsubs = {
'VEcoli' : r'\text{V}_{\text{Ecoli}}',
'Na' : r'\text{N}_{\text{A}}',
'NA' : r'\text{N}_{\text{A}}',
'FP' : r'\text{FP}',
'Iex' : r'\text{I}_{\text{ex}}',
'YIex' : r'\text{YI}_{\text{ex}}',
'>': r'\rightarrow',
r'*': r'\times', 
r'+': '+',
r'$pool' : '\oslash',
r'l' : '\lambda'
}

def assignmentparse(li):
    """ Process lines of format 'key = val' with a variable amount of
    spacing"""

    var = li.split('=')
    stripped = [x.replace(' ','') for x in var]

    return stripped

def parsefile(filename):
    """Parse psc-file and store in file structure"""

    # Dictionary with reaction number as key, [[reaction], [propensity]] as
    # value
    reactionslist = []
    parmslist = []
    initslist = []

    reactionmode = False
    parmmode = False
    initmode = False

    inputfile = open(filename,'r')
    lines = inputfile.readlines()

    for line in lines:
        sline = line.strip('\n')
        # if len(sline) == 1:
            # continue
        if sline == '':
            continue

        # Determine type of parser required for following lines
        parsetype = re.match("#\s*(\w+)",line)

        # Parse according to one of three parsing types
        if parsetype != None:
            if parsetype.group(1) == "Reactions":
                reactionmode = True
                parmmode = False
                initmode = False
            if parsetype.group(1) == "Parameters":
                reactionmode = False
                parmmode = True
                initmode = False
            if parsetype.group(1) == "Initialvalues":
                reactionmode = False
                parmmode = False
                initmode = True
            continue

        if reactionmode == True:
            m = reactionnum.match(line)
            try:
                curreaction = int(m.group('num'))
                reactionslist.append([])
                logging.debug(curreaction)
                continue
            except:
                pass

            # Parse reaction if fraction
            if not fractdetect.search(line) == None:
                processfract(line.replace('\n',''))
            else:
                units = [x.replace('\n','') for x in line.split(" ") if x != '']
                if len(units) != 1:
                    reactionslist[(curreaction-1)].append(units)

        elif parmmode == True:
            parmslist.append(assignmentparse(sline))

        elif initmode == True:
            initslist.append(assignmentparse(sline))

        else:
            pass
    
    return reactionslist, parmslist, initslist

def pline(line):
    return [latexify(x) for x in line.split(' ') if x != '']

def processfract(line):
    fract = fractdivide.match(line)
    num = pline(fract.group(1))
    denum = pline(fract.group(2))
    rest = pline(fract.group(3))

reactionnum = re.compile(r"""
^R
(?P<num>\d+)
:
\s*$
""", re.VERBOSE)

kdetect = re.compile(r"(?P<type>[k|m|M|l])_?(?P<subscript>\w+)")

rdetect = re.compile(r"\w+")

singleletter = re.compile(r"(\w)")

stoichfind = re.compile(r"{(\d+)}(\w+)")

fractdetect = re.compile(r"/")

fractdivide = re.compile(r"""
((?P<num>\w+))
\s?/\s?
((?P<denom>.+))
""", re.VERBOSE)


def latexify(item):
    if customsubs.has_key(item):
        return customsubs[item]

    if not fractdetect.search(item) == None:
        m = fractdivide.match(item) 
        num = [latexify(x) for x in m.group('num').split(' ')] 
        denom = [latexify(x) for x in m.group('denom').split(' ')] 
        joinednum = ' '.join(num)
        joineddenom = ' '.join(denom)
        res =  r'\frac{'+joinednum+'}{'+joineddenom+'}'
        return res

    kval = kdetect.search(item)
    try:
        return r'\text{'+latexify(kval.group('type'))+r'}_{\text{'+kval.group('subscript')+'}}'
    except:
        pass

    try:
        re.match('\w').group(0)
        return(r'\text{'+item+r'}')
    except:
        pass

    try:
        single = singleletter.match(item)
        return(r'\text{'+single.group(0)+'}')
    except:
        pass

    try:
        coef = stoichfind.search(item)
        return coef.group(1)+latexify(coef.group(2))
    except:
        pass

    species = rdetect.search(item)
    try:
        resstring = []
        for x in list(species.group(0)):
            try:
                num = re.match('\d',x).group(0)
                resstring.append('_{'+num+'}')
            except:
                resstring.append(x)
        return ''.join(resstring)

    except:
        pass

    # if item.startswith('\w'):
        # return re.sub(r'(\d)',r'_{\1}',item)

    # if re.match('\w',item):
    #     return(r'\text{'+item+r'}')
    # re.sub('r(?P<letter>\w)','(?

def stringify(inputli):
    temp = ' '.join(inputli)
    return r'\begin{equation} '+temp+r' \end{equation}'

def formatreactions(reactionslist):
    reactlist, proplist = [],[]

    for rnum in reactionslist:
        logging.debug(rnum)
        reaction = [latexify(x) for x in rnum[0] if x != '']
        prop  = [latexify(x) for x in rnum[1] if x != '']

        reactlist.append(stringify(reaction))
        proplist.append(stringify(prop))

    return reactlist, proplist

if __name__ == '__main__':
    # parsefile -> 
    reactionslist, parmslist, initslist = \
    parsefile('/home/maarten/Dropbox/igem_dropbox/Stochpy/pscmodels/FPLac.psc')
    reactlist, proplist = formatreactions(reactionslist)
    final = []
    for i in xrange(len(reactlist)):
        final.append(reactlist[i])
        final.append(proplist[i])

    formattedfinal = '\n'.join(final)
    print formattedfinal
    exit()

    latextemplate = r"""
    \documentclass[a4paper]{article}
    \usepackage{amsmath}
    \begin{document}
    \author{iGEM Amsterdam}
    \title{Test}
    \maketitle
    """ +formattedfinal+ """
    \end{document}
    """

    with open('output.tex','w') as output:
        output.write(latextemplate)
    os.system('pdflatex output.tex')
