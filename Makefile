MDLfile=~/Stochpy/igemmodels/FPspeed

all: $(MDLfile).pdf

$(MDLfile).pdf: $(MDLfile).tex
	pdflatex $(MDLfile).tex

$(MDLfile).tex: template.tex mdl2latex.py
	python mdl2latex.py $(MDLfile).psc

clean:
	rm *.log 
	rm *.aux 
