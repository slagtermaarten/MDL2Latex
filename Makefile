MDLfile=FPlac.psc

all: model.pdf

model.pdf: model.tex
	pdflatex $<

model.tex: template.tex mdl2latex.py $(MDLfile)
	python mdl2latex.py $(MDLfile)
