# APEx: Accuracy-Aware Differentially Private Data Exploration

Source code for the ACM SIGMOD 2019 paper:
> Chang Ge, Xi He, Ihab F. Ilyas, Ashwin Machanavajjhala: APEx: Accuracy-Aware Differentially Private Data Exploration. SIGMOD Conference 2019: 177-194

Full papper is available on [arXiv](https://arxiv.org/pdf/1712.10266.pdf). You can also watch a [video](https://av.tib.eu/media/42854) for a quick introduction.

## Installation

APEx was built using Python and MySQL as the backend data management. It was tested on Python 3.6 and MySQL Server 5.5. As the first step, clone this rep:

```bash##
git clone https://github.com/cgebest/APEx.git 
cd APEx
```

### 1. Install Python dependencies

The dependencies are listed in the `environment.yml`. If you use [`conda`](https://docs.conda.io/projects/conda/en/latest/user-guide/install/) as the package manger, dependencies can be installed using the following command:

```bash
conda env create -f=environment.yml
conda activate apex
```

### 2. Install and configure MySQL

If you do not have a native MySQL server running on your system, an easy way is to start a MySQL docker container.

```bash
docker run --name apexsql -e MYSQL_ROOT_PASSWORD=rootPass -p 3306:3306 -d mysql
```
We provide an US Census database image for the testing purpose. To import the image:

```bash
cd data
./importDB.sh
```

## Run APEx

To run the sample queries, simply go to the `test` directory, and run the following command:
```bash
cd test
python test_census.py
```

To run your own queries, please refer the following folders to define your data and queries:
+ `./query/`: workload query definition. See examples of `census` and `location`.
+ `./privacy/`: privacy engine and many differential privacy mechanisms.
+ `./conn/`: database connection.

## Questions?

Please reach out to Chang Ge (chang.ge AT uwaterloo.ca) for questions and comments. 
