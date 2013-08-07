#!/bin/bash

function escape () {
	echo $@ | sed -e 's/ /\\ /g' -e 's/\//\\\//g'
}

export MYDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"

[ -z "$ENV_PREFIX" ] && export ENV_PREFIX="/tmp"

echo "Setting environment to $ENV_PREFIX"

mkdir $ENV_PREFIX/pastatest
mkdir $ENV_PREFIX/pastaroot
cd $ENV_PREFIX/pastatest
git init --bare
git clone "$ENV_PREFIX/pastatest" "$ENV_PREFIX/pastatest-local" > /dev/null 2>&1
git clone "$ENV_PREFIX/pastatest" "$ENV_PREFIX/another" > /dev/null 2>&1
cd "$ENV_PREFIX/another"
cp -r $MYDIR/../example/* .
git add . > /dev/null
git commit -m "init" > /dev/null 2>&1
git push origin master > /dev/null 2>&1

SEDBASEDIR="`escape $BASEDIR`"
SED_PREFIX="`escape "$ENV_PREFIX"`"
cat $MYDIR/../hooks/post-receive |sed -e "s/\(PASTASPYGE =\).*/\1 \"${SEDBASEDIR}\"/" \
-e "s/\(PAGE_REPO =\).*/\1 \"$SED_PREFIX\/pastatest-local\"/" \
-e "s/\(DOCUMENT_ROOT =\).*/\1 \"$SED_PREFIX\/pastaroot\"/" > "$ENV_PREFIX/pastatest/hooks/post-receive"

chmod a+x "$ENV_PREFIX/pastatest/hooks/post-receive"

echo "REPOSITORY: $ENV_PREFIX/pastatest"
echo "Local copy: $ENV_PREFIX/another"
echo "Document root: $ENV_PREFIX/pastaroot"
