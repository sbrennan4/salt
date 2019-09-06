pipeline {
    agent { label 'syscore-salt'}
    environment {
        BBGH_TOKEN = credentials('bbgithub_token')
        PYPI_CREDENTIAL = credentials('salt_jenkins_ad_user_pass_escaped')
    }
    stages {
        stage('Build') {
            when {changeRequest()}
            steps {
                sh 'bash ./build/build.sh -b $CHANGE_ID'
            }
        }
        stage('Run Upstream Salt Unit Tests') {
            when {changeRequest()}
            steps {
                sh '''
                    /usr/local/bin/tox -e pylint-tests --notest
                    source .tox/pylint-tests/bin/activate
                    python tests/runtests.py --unit
                '''
            }
        }        
        stage('Deploy to dev pypi') {
            when {changeRequest()}
            steps {
                sh 'bash ./build/build.sh -b $CHANGE_ID -k -s -u'
            }
        }
        stage('Deploy to ose pypi') {
            when {anyOf {branch 'v2018.3.3-ca'}}
            steps {
                sh 'bash ./build/build.sh -u -p -t $BBGH_TOKEN_PSW'
            }
        }
    }
}
