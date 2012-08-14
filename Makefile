MDLfile=CellDivision

all: $(MDLfile).pdf

$(MDLfile).pdf: $(MDLfile).tex
	pdflatex $(MDLfile).tex

$(MDLfile).tex: template.tex mdl2latex.py $(MDFfile).psc
	python mdl2latex.py $(MDLfile).psc

$(MDFfile).psc:

clean:
	rm *.log *.aux *.pyc
	rm *.pdf

