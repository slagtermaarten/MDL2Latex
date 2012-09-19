import re, sys
import logging
import os
logging.basicConfig(level=logging.DEBUG)
from pprint import pprint as pp
import django
from django.template import Template, Context
import json
home = os.getenv('home')

# Define dictionary of user definable substitutions which will be given
# the highest substitution priority
regsubs = {
    'VEcoli' : r'\text{V}_{\text{Ecoli}}',
    'Na' : r'\text{N}_{\text{A}}',
    'NA' : r'\text{N}_{\text{A}}',
    '>': r'\rightarrow',
    r'*': r'\cdot', 
    r'+': '+',
    r'-': '-',
    r'$pool' : '\oslash',
    r'l' : '\lambda'
}


reactionnum = re.compile(r"""
^R
(?P<num>\d+)
:
\s*$
""", re.VERBOSE)

kdetect = re.compile(r"(?P<type>[k|m|M|l|S|s])_?(?P<subscript>\w+)")

rdetect = re.compile(r"\w+")

word = re.compile(r"(\w)+")

stoichfind = re.compile(r"{(\d+)}(\w+)")

fractdetect = re.compile(r".+/.+")

fractdivide = re.compile(r"""
(?P<num>[a-zA-Z\*\d]+)
\s?/\s?
\((?P<denom>.+)\)
\s?
(?P<rest>.+)?
""", re.VERBOSE)

parsetype = re.compile("\#\s*(\w+)")

numberdetect = re.compile('(\d\.?\d*)')

minfind = re.compile(r'\((\w+)([-\+]\d)\)')

def parsefile(filehandle):
    """Parse psc-file and store in file structure"""
    # Dictionary with reaction number as key, [[reaction], [propensity]] as
    # value
    reactionsdict, parmslist, initslist = {}, [], []

    reactionmode, parmmode, initmode = False, False, False
    equationmode, propmode = False, False

    lines = filehandle.readlines()

    for line in lines:
        sline = line.strip('\n')

        if sline == '':
            continue

        # Determine type of parser required for following lines
        ptype = parsetype.match(line)

        # Parse according to one of three parsing types
        if ptype != None:
            # print parsetype.group(1)
            # print reactionmode,parmmode,initmode
            if ptype.group(1).lower() in ["reactions",'reacts','equations','eqs']:
                reactionmode,parmmode,initmode = True,False,False
            if ptype.group(1).lower() in ["parameters",'parms','initpar']:
                reactionmode,parmmode,initmode = False,True,False
            if ptype.group(1).lower() in ["initialvalues",'ics','initvar','initials']:
                reactionmode,parmmode,initmode = False,False,True
            else:
                # Single lines starting with # are matched for parsetype, but
                # do not affect the program due to above logic
                pass
            continue

        if reactionmode == True:
            m = reactionnum.match(line)
            try:
                curreaction = int(m.group('num'))
                reactionsdict[curreaction] = []
                equationmode, propmode = True, False
                # Next line is going to be an equation
                continue
            except:
                pass

            if equationmode == True:
                logging.debug(sline)
                # Process line regular way, as there are never fractions in the
                # reactions, no need to test for it
                temp = equify(processreg(sline))
                reactionsdict[curreaction].append(temp)
                # Next line is going to be a propensity
                equationmode, propmode = False, True
                continue

            if propmode == True:
                # Substitute all '*' for ' * '
                sline = re.sub('\*',' * ',sline)
                # Parse propensity if fraction
                if not fractdetect.match(line) == None:
                    temp = equify(processfract(sline))
                    reactionsdict[curreaction].append(temp)

                # Parse reaction as if not containing fraction
                else:
                    temp = equify(processreg(sline))
                    reactionsdict[curreaction].append(temp)
                continue

                # Next line should be another reaction number
                equationmode, propmode = False, False

        elif parmmode == True:
            parmslist.append(assignmentparse(sline))

        elif initmode == True:
            initslist.append(assignmentparse(sline))

        else:
            pass
    
    return reactionsdict, parmslist, initslist

def equify(string):
    if string is not None:
        return "$ "+string+" $"
    return None

def assignmentparse(li):
    """ Process lines of format 'key = val' with a variable amount of
    spacing"""

    # Remove trailing comments
    li = re.sub('\s+\#.+$','',li)

    # Split line at "=" sign
    var = li.split('=')

    # Remove empty space in between
    stripped = [latexify(x.replace(' ','')) for x in var]
    # return '$'+' '.join(stripped)
    return stripped


def processreg(line):
    if fractdetect.match(line) is not None:
        return processfract(line)
    else:
        latexified = [latexify(x) for x in line.split(' ') if x != '']
        return ' '.join(latexified)

def processfract(line):
    split = line.split('/')
    num =  split[0]
    ind = split[1].index(')')
    denum = split[1][1:(ind)]

    fdenum = processreg(denum)
    fnum = processreg(num)

    result =  r'\frac{'+fnum+r'}{'+fdenum+r'}'

    try:
        rest = processreg(split[1][(ind+1):])
        result+=rest
    except:
        pass

    return result

def latexify(item):
    # First try and match the 'word' with a key in one of two substitution
    # dicts
    if regsubs.has_key(item):
        return regsubs[item]

    if usersubs:
        if usersubs.has_key(item):
            return usersubs[item]

    kval = kdetect.search(item)
    try:
        return latexify(kval.group('type'))+r'_{\text{'+kval.group('subscript')\
                +'}}'
    except:
        pass

    try:
        minus = minfind.match(item)
        return(r'(\text{'+minus.group(1)+r'}'+minus.group(2)+')')
    except:
        pass

    try:
        number = numberdetect.match(item)
        return(r'$'+number.group(0)+r'$')
    except:
        pass
    
    try:
        single = word.match(item)
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

if __name__ == '__main__':
    django.conf.settings.configure()

    # Parse command line options, stick to defaults if absent
    try:
        inputfilename = str(sys.argv[1])
        inputfile = open(inputfilename,'r')
    except:
        logging.info("Specify input file, default is currently used")
        inputfilename = 'Stochpy/pscmodels/DecayingDimerizing.psc'
        inputfile = open(inputfilename,'r')

    try:
        title, author = str(sys.argv[2]), str(sys.argv[3])
    except:
        logging.info("Specify title and author of output file, defaults are",
                "used")
        title, author = inputfilename[:-4], "Maarten" 

    try: 
        usersubs = json.loads(open('usersubs.txt','r').read())
        logging.debug(usersubs)
    except Exception as e:
        logging.debug(e)
        logging.info("No custom subs found, please place in 'usersubs.txt'")

    outputfilename = inputfilename[:-4]+'.tex'

    # Parse inputfile
    reactionsdict, parmslist, initslist = parsefile(inputfile)

    # Convert dict to list for easy usage in the Django template...
    reactionslist = list(reactionsdict.values())
    # for key in sorted(reactionsdict.keys()):
    #     reactionslist.append(reactionsdict[key][:2])
        
    # Parse data structure to .tex format and write to output file
    with open("template.tex") as f:
        t = Template(f.read())

    c = Context({"reactions":reactionslist, "parms":parmslist,
        "inits":initslist, "modeltitle": title, "author": author})
    output = t.render(c)

    # Remove empty lines, introduced by the Django template
    strippedoutput = re.sub(r'\n[ \t]*(?=\n)','',output)

    logging.debug("Outputting to %s" % outputfilename)
    with open(outputfilename, 'w') as out_f:
        out_f.write(strippedoutput)
