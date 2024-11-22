#!/bin/bash
## sole parameter is an integer indicating incremental daily version
## git branch --set-upstream-to=origin/das_dev das_dev	

if [[ ( $@ == "--help") ||  $@ == "-h" ]]; then
    echo "$0 <optional: --no-cache>"
    exit 1
fi

if [ $# -eq 1 ]; then
    NO_CACHE=$1
fi


GIT_BRANCH=$1
date_var=$(date +%Y.%m.%d.%H.%M%S)
BUILD_TAG=dbcawa/commercialoperator:$date_var
#git checkout $GIT_BRANCH &&
#git pull &&
#cd commercialoperator/frontend/commercialoperator/ &&
#npm run build &&
#cd ../../../ &&
#source venv/bin/activate &&
#./manage.py collectstatic --no-input &&
docker image build $NO_CACHE --tag $BUILD_TAG . &&
echo $BUILD_TAG &&
docker push $BUILD_TAG
