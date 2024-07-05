
J212.tc: J212.config
	python -m curvetracer -c $< tc

J212.oc: J212.config
	python -m curvetracer -c $< oc

J212.tc.png: J212.tc
	rm -f $@
	python -m curvetracer -i $< -o $@ plot

J212.tc.temp.png: J212.tc
	rm -f $@
	python -m curvetracer -i $< -o $@ -t plot

J212.oc.png: J212.oc
	rm -f $@
	python -m curvetracer -i $< -o $@ plot

pngs: J212.tc.png J212.tc.temp.png J212.oc.png
