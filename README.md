# measure_risk_aversion
## Introduction
In this project we try to estimate the coefficient of relative risk aversion using time series insurance data. The theoretical model follows Szpiro (1986) closely.

This term project is for the course Effective Programming Practices for Economists. I use the Waf [template](https://github.com/hmgaudecker/econ-project-templates) structured by Hans-Martin von Gaudecker.

## How to use it
Please clone this repository to your local directory. Open a shell in the project (For Windows: if you didn't add Python to your environment variables, just use Anaconda Prompt) and enter ``python waf.py configure`` and ``python waf.py build`` in order. The building process will pause when the figures appear. Close them if you want to continue building the project.

If the project is built successfully, all outputs will be stored in the directory *bld*. ``python waf.py install`` will copy the paper/presentation/documentation outputs to the main directory and you don't have to go inside *bld* to find these files.

If you want to know the workflow of this project, please check the Directed Acyclic Graph (DAG) stored in *bld/out/figures*.