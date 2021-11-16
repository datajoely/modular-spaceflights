# Remove artifacts created by python + intermediate data files
clean:
	find . -type d -name  "__pycache__" -exec rm -r {} +
	find data -type f | grep -E '.+0[2-9]' | grep -v '.gitkeep' | xargs rm -fr   
	find data -type d | grep -E '.+0[2-9]_[a-z]+/.+/' | grep -o 'data/.._.*/' | sort -u | xargs rm -rf  

# Create environment
env:
	conda create -n mod-spaceflights python=3.8 -y --force