java -version
brew install openjdk

conda install -c conda-forge pypdf2
conda install -c conda-forge pymupdf
conda install -c conda-forge jpype1
conda install -c conda-forge tabula-py
conda install -c conda-forge numpy pandas
conda install -c conda-forge openjdk

export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which javac))))
