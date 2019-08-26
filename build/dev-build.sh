#!/bin/bash
# ================================================
#
#   Core Auto build script for
#
#              salt
#
# ================================================
#
#   This script builds a wheel for saltstack.
#
#   Purpose:
#       Core Auto is constantly enhancing and fixing mistakes in salt upstream. However, these enhancements
#       and fixes can take months to be merged into a proper Salstack release. Since these updates
#       can be critical to fixing operating behavior or enhancing the produt to fufill a concept, Core Auto
#       needs to build and deploy our own version of salt.
#

TRUE=1
FALSE=0

# Change metadata here for version bump
_LibName=salt
_LibVer=2018.3.3
_LibVerArr=(${_LibVer//./ })
_LibUrl=@bbgithub.dev.bloomberg.com/saltstack/salt.git
_LibBranch=v${_LibVer}-ca
_LibTag=v${_LibVer}

# Define build specific user opts
_PypiEnv=dev
_Upload=$FALSE
_Prod=$FALSE
_KeepBuildDir=$FALSE
_KeepVirtEnv=$FALSE
_PostBuildTag=
_BuildBranch=
_SkipBuild=$FALSE

# Define general const
NS=bloomberg.coreauto
ADMIN_PY=/opt/python/3.7.3/bin/python3
ROOT_PATH=`pwd`
BUILD_PATH=${ROOT_PATH}/build
ASSETS_PATH=${BUILD_PATH}/assets
BUILD_LOG=${BUILD_PATH}/build.log
VIRTENV_PATH=${BUILD_PATH}/buildenv
RELEASE_URL=https://bbgithub.dev.bloomberg.com/api/v3/repos/saltstack/salt/releases

# Define lib const
LIB_NAME_VER=${_LibName}-${_LibVer}
LIB_PATH=${ROOT_PATH}
LIB_DIST_PATH=${LIB_PATH}/dist
LIB_PATCHES_PATH=${LIB_PATH}/patches


# env set
export https_proxy=http://devproxy.bloomberg.com:82
export no_proxy=artprod.dev.bloomberg.com,bbgithub.dev.bloomberg.com
export USE_SETUPTOOLS=True

usage() {
    cat << EOT
  Usage :  build.sh [options]

  Options:
    -h  Display this message
    -a  Admin Python location.
    -b  Build tag. Typically the build date with out a delimiter such as '20190403'.
        If multiple builds on the same date are necessary, just add the next
        available number such as '201904031'. (Default: '')
    -B  Specify a build branch from the salt repo (Default: $_LibBranch)
    -k  Don't delete the python virtual env. Useful if you don't want to
        keep building a new virtual env every time. (Default: False)
    -p  Upload the wheel to the production pypi repo. (Default: False)
    -q  credential for uploading to pypi. You can also use PYPI_CREDENTIAL_PSW
        environment variable or input the cred a the console. 
    -s  Skip build steps. Useful if you built the artifacts earlier and 
        are only interested in uploading them
    -t  bbgithub token for creating a release
    -u  Upload the wheel to Artifactory pypi (Default: False)
    -v  Debug output
EOT
}

while getopts ':ha:b:B:kpq:suvt:' opt
do
  case "${opt}" in
    h ) usage; exit 0                               ;;
    a ) _AdminPythonLocation=$OPTARG                ;;
    b ) _PostBuildTag=$OPTARG                       ;;
    B ) _BuildBranch=$OPTARG                        ;;
    t ) _BbghToken=$OPTARG                          ;;
    k ) _KeepVirtEnv=$TRUE                          ;;
    p ) _Prod=$TRUE                                 ;;
    q ) _PypiCredential=$OPTARG                     ;;
    s ) _SkipBuild=$TRUE                            ;;
    u ) _Upload=$TRUE                               ;;
    v ) set -x                                      ;;
    \?)  echo
         echo "Option does not exist : $OPTARG"
         usage
         exit 1
         ;;

  esac
done
shift $((OPTIND-1))

# --------------------------------------------------------
#           checks
# --------------------------------------------------------

# TODO
#   install admin py 37 as i'm sure we'll need this for jenkins
if [[ -z $_AdminPythonLocation ]]; then
    echo 'default admin python location'
    _AdminPythonLocation=$ADMIN_PY
fi

if [[ ! -f $_AdminPythonLocation ]]; then
    echo "admin python necessary to build ${_Lib}. exiting."
    exit 1
fi

if  ($_AdminPythonLocation -V); then
    echo "able to run admin python"
else
    echo "Unable to run admin python. Check that it's installed and permissioned properly"
    exit 1
fi

if [[ -z $_BbghToken && $_Prod == 1 ]]; then
    if [[ -z $BBGH_TOKEN_PSW ]]; then
        echo "BBGH token is necessary to create a prod release. Please use -t or set BBGH_TOKEN_PSW"
        exit 1
    fi
    _BbghToken=$BBGH_TOKEN_PSW
fi

# Check post build tag is a number
if [[ ! -z $_PostBuildTag ]] && [[ ! $_PostBuildTag =~ ^[0-9]+$ ]]; then
    echo "error: Post build tag is Not a number!" >&2
    exit 1
fi

if [[ -z $_BuildBranch ]]; then
    _BuildBranch=$_LibBranch
fi

# --------------------------------------------------------
#           functions
# --------------------------------------------------------

function setup_build_env {
    # if virtenv path is present, determine if we want to clean house
    # or keep it. Otherwise just create the virtenv path
    if [[ -d $VIRTENV_PATH ]]; then

        if [[ "$_KeepVirtEnv" -eq "$FALSE" ]]; then
            echo "Found old virtenv dir... deleting"
            rm -rf $VIRTENV_PATH
            $_AdminPythonLocation -m venv $VIRTENV_PATH
        else
            echo "KeepVirtEnv enabled... skipping virtenv dir removal"
        fi

    else
        # virtenv not present so create it
        $_AdminPythonLocation -m venv $VIRTENV_PATH
    fi

    cp $ASSETS_PATH/pip.conf $VIRTENV_PATH

    # activate virtenv and install build deps
    . $VIRTENV_PATH/bin/activate
    if [ $? -ne 0 ]; then
        echo "Unable to activate venv"
        exit 1
    fi
    pip install --upgrade -r $ASSETS_PATH/requirements.txt
}

function pull_salt {
    # no longer needed with single repo
    return

    cd $BUILD_PATH

    # If not present, clone the repo and checkout the branch
    # Otherwise do some house cleaning bc we know we kept the build
    # dir.
    if [[ ! -d $LIB_PATH ]]; then
        git clone $_TokenUrl $LIB_NAME_VER
        if [ $? -eq 0 ]; then
            echo "git clone succeeded"
        else
            echo "git clone failed. Check permissions"
            exit 1
        fi
        cd $LIB_PATH
        git fetch origin
        git checkout ${_BuildBranch}
    else
        cd $LIB_PATH
        git clean -f -d
        git reset --hard origin/develop
        git checkout develop
        git pull origin develop
        git rev-parse --verify ${_BuildBranch} > /dev/null 2>&1
        if [[ ${PIPESTATUS[0]} -eq 0 ]]; then
            echo "deleting old ${_BuildBranch} ... "
            git branch -D ${_BuildBranch}
        fi
        git checkout ${_BuildBranch}
    fi
}

function build_salt {
    cd $LIB_PATH

    # copy in our requirements files as we need to use specific libs
    # and versions
    cp $ASSETS_PATH/base.txt $LIB_PATH/requirements/base.txt
    cp $ASSETS_PATH/zeromq.txt $LIB_PATH/requirements/zeromq.txt

    # copy in our setup.py
    cp $ASSETS_PATH/setup.py $LIB_PATH/setup.py

    # Create the post-release tag for this build
    #
    # NOTE:
    #   --with-salt-version only works when specifically executing `python setup.py build`.
    #   Since sdist does not build from the build dir, we need to hijack `salt/_version.py` and
    #   drop in our own version to get a post build release.
    #
    #   see https://github.com/saltstack/salt/pull/43955
    cat <<EOF > ${LIB_PATH}/salt/_version.py
from salt.version import SaltStackVersion
__saltstack_version__ = SaltStackVersion(${_LibVerArr[0]}, ${_LibVerArr[1]}, ${_LibVerArr[2]}, None, '_', ${_PostBuildTag}, None, None)
EOF

    # clean up if told to
    if [[ "$_KeepBuildDir" -eq "$TRUE" ]];then
        python setup.py clean --all
    fi

    # Build the src distro
    python setup.py sdist 2>&1 | tee -a ${BUILD_LOG}
    if [[ ${PIPESTATUS[0]} -ne 0 ]]; then
        echo "python build exited non-zero: $?. Please check build.log for details"
        exit ${PIPESTATUS[0]}
    fi

    if [[ ! -f ${_SrcPath} ]]; then
        echo "Seems ${_SrcPath} is not present. Did it build correctly? Please check build.log"
        exit 1
    fi

}

function publish_salt {

    # This needs to align with aliases defined in
    # assets/pypirc
    if [[ $_Prod -eq $TRUE ]]; then
        exit 1
        _PypiEnv="prod"
    fi
    echo "Uploading ${_SrcFile} to ${_PypiEnv} pypi ..."

    if [[ -z $_PypiCredential ]]; then
        _PypiCredential=$PYPI_CREDENTIAL_PSW
    fi
    if [[ -z $_PypiCredential ]]; then
        twine upload --config-file ${BUILD_PATH}/assets/pypirc -r $_PypiEnv $_SrcPath 2>&1 | tee -a ${BUILD_LOG}
    else
        _PypiCredential_modified=$(echo $_PypiCredential | tr -d '\\')
        twine upload --config-file ${BUILD_PATH}/assets/pypirc -p $_PypiCredential_modified -r $_PypiEnv $_SrcPath 2>&1 | tee -a ${BUILD_LOG}
    fi

    if [[ ${PIPESTATUS[0]} -ne 0 ]]; then
        echo "Attempt to publish the wheel failed with rc: $?. Please check build.log for details"
        exit 1
    fi

}

function gen_post_data {
    tag=v${_LibVer}-${_PostBuildTag}
    cat <<EOF
{
    "name": "$tag",
    "tag_name": "$tag",
    "target_commitish": "$_BuildBranch",
    "body": "NOTICE: This is Bloomberg's patched version of Saltstack and may contain breaking changes or code not available to the upstream repository."
}
EOF
}

function create_release {
    # TODO: Handle errors by capturing the output
    curl $RELEASE_URL -H "Authorization: token ${_BbghToken}" -d "$(gen_post_data)"

    if [[ ${PIPESTATUS[0]} -ne 0 ]]; then
        echo "Attempt to create a release failed with rc: $?. Please check build.log for details"
        exit ${PIPESTATUS[0]}
    fi
}

# --------------------------------------------------------
#           main
# --------------------------------------------------------

# setup
setup_build_env
if [[ "$_SkipBuild" -ne "$TRUE" ]]; then
    pull_salt
    if [[ -z $_PostBuildTag ]]; then
        cd $LIB_PATH
        git fetch --tags
        _last_build=$(git describe --abbrev=0 --tags | cut -d - -f2)
        if [[ ! -z $_last_build  && $_last_build =~ ^[0-9]+$ ]]; then
            _PostBuildTag=$(expr $_last_build + 1)
        else
            _PostBuildTag=0
        fi
    fi
fi
_SrcFile=${NS}.${LIB_NAME_VER}-${_PostBuildTag}.tar.gz
_SrcPath=${LIB_DIST_PATH}/${_SrcFile}

if [[ "$_SkipBuild" -ne "$TRUE" ]]; then
    echo
    echo "Building new source distro for sysca salt from branch '${_BuildBranch}' on release ${_PostBuildTag} ..."
    echo
    build_salt
fi

# publish
if [[ "$_Upload" -eq "$TRUE" ]]; then
    if [[ $_Prod -eq $TRUE ]];then
        # Only create a release if publishing to prod
        create_release
    fi
    publish_salt
else
    echo "Will not upload wheel to ${_PypiEnv} pypi. File is available at:"
    echo ${_SrcPath}
fi
exit 0
