#!/usr/bin/env bash

cd basic_code

# cd copyData
# zip -r -j -D copyData.zip *
# mv copyData.zip ../
# cd ../


# cd createRepo
# zip -r -j -D createRepo.zip *
# mv createRepo.zip ../
# cd ../


# cd endpointWait
# zip -r -j -D endpointWait.zip *
# mv endpointWait.zip ../
# cd ../


# cd maintenance
# zip -r -j -D maintenance.zip *
# mv maintenance.zip ../
# cd ../


# cd fraudFunction
# zip -r -j -D fraudFunction.zip *
# mv fraudFunction.zip ../
# cd ../


# cd triggerModelTraining
# zip -r -j -D triggerModelTraining.zip *
# mv triggerModelTraining.zip ../
# cd ../


# cd modelTest
# zip -r -j -D modelTest.zip *
# mv modelTest.zip ../
# cd ../

#################
# building layers
mkdir layers
cd ./layers

mkdir numpyLibraryPython38
cd numpyLibraryPython38
pip install --target ./python numpy -i https://pypi.douban.com/simple
zip -rg numpyLibraryPython38.zip .
mv numpyLibraryPython38.zip ../
cd ../

mkdir pandasLibraryPython38
cd pandasLibraryPython38
pip install --target ./python pandas -i https://pypi.douban.com/simple
zip -rg pandasLibraryPython38.zip .
mv pandasLibraryPython38.zip ../
cd ../

mkdir psycopg2Python37
cd psycopg2Python37
pip install --target ./python psycopg2-binary -i https://pypi.douban.com/simple
zip -rg psycopg2Python37.zip .
mv psycopg2Python37.zip ../
cd ../

mkdir sagemakerLibraryPython38
cd sagemakerLibraryPython38
pip install --target ./python sagemaker -i https://pypi.douban.com/simple
zip -rg sagemakerLibraryPython38.zip .
mv sagemakerLibraryPython38.zip ../
cd ../