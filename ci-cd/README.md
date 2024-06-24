# CI/CD

This pipeline shows how to create a workflow that gets your code from github, builds your container images and runs the images.

It contains two stages:

1. Image Build
2. Run Built Images

```
Stages:     Build Images(jobs run in parallel)   --->   Run Build Images
             -------------------------------             ---------------------             -----------------------
            | Firts useless job image build |           | Firts useless job   |   ---->   | Second useless job    |
             -------------------------------             ---------------------             -----------------------


             --------------------------------
            | Second useless job image build |
             --------------------------------

```

i8i.yaml file is configured to run this example.
