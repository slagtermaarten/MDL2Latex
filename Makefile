MDLfile=FPlac.psc

all: model.pdf
	rm *.log *.aux *.pyc

model.pdf: model.tex
	pdflatex $<

model.tex: template.tex mdl2latex.py
	python mdl2latex.py $(MDLfile)
