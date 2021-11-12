clean:
	find . -type d -name  "__pycache__" -exec rm -r {} +

rm-pipeline-data
	find data -type f | grep -E '.+0[2-9]' | grep -v '.gitkeep' | xargs rm -fr   