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

kdetect = re.compile(r"(?P<type>[k|m|M|l])_?(?P<subscript>\w+)")

rdetect = re.compile(r"\w+")

singleletter = re.compile(r"(\w)")

stoichfind = re.compile(r"{(\d+)}(\w+)")

fractdetect = re.compile(r".+/.+")

# test2 = test[:-10]
# test2
# fractdivide.match(test2).group(1)

fractdivide = re.compile(r"""
(?P<num>[a-zA-Z\*\d]+)
\s?/\s?
\((?P<denom>.+)\)
\s?
(?P<rest>.+)?
""", re.VERBOSE)

# fractdivide.match(string).group(3)

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
            if ptype.group(1) in ["Reactions",'reacts']:
                reactionmode,parmmode,initmode = True,False,False
            if ptype.group(1) in ["Parameters",'parms']:
                reactionmode,parmmode,initmode = False,True,False
            if ptype.group(1) in ["Initialvalues",'ics']:
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
               # Parse propensity if fraction
                if not fractdetect.match(line) == None:
                    temp = equify(processfract(sline))
                    print curreaction, temp
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
    if customsubs.has_key(item):
        return customsubs[item]

    kval = kdetect.search(item)
    try:
        return latexify(kval.group('type'))+r'_{\text{'+kval.group('subscript')+'}}'
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

def renderlatex():
    pass

if __name__ == '__main__':
    django.conf.settings.configure()

    try:
        inputfile = open(str(sys.argv[1]),'r')
    except:
        logging.info("Specify input file, default is currently used")
        inputfile = open('FPLac.psc','r')

    try:
        title, author = str(sys.argv[2]), str(sys.argv[3])
    except:
        logging.info("Specify title and author of output file, defaults are used")
        title, author = "Mymodel", "Maarten" 

    reactionsdict, parmslist, initslist =  parsefile(inputfile)
    reactionslist = []
    for key in sorted(reactionsdict.keys()):
        reactionslist.append(reactionsdict[key][:2])
        
    pp(reactionslist)
    # exit()
    # pp(initslist)
    # pp(parmslist)

    with open("template.tex") as f:
        t = Template(f.read())

    c = Context({"reactions":reactionslist, "parms":parmslist,
        "inits":initslist, "modeltitle": title, "author": author})
    output = t.render(c)
    strippedoutput = re.sub(r'\n[ \t]*(?=\n)','',output)

    with open("model.tex", 'w') as out_f:
        out_f.write(strippedoutput)
