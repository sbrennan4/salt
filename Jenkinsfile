pipeline {
    agent { label 'syscore-salt'}
    environment {
        BBGH_TOKEN = credentials('bbgithub_token')
        PYPI_CREDENTIAL = credentials('salt_jenkins_ad_user_pass_escaped')
    }
    stages {
        stage('build') {
            when {
                changeRequest()
            }
            steps {
                sh 'echo ========================'
                sh 'echo running Build Stage'
                sh 'whoami'
                sh 'python --version'
                sh 'hostname'
                sh 'pwd'
                sh 'printenv'
                sh 'bash ./build/build.sh -b $CHANGE_ID'
            }
        }
        stage('test') {
            when {
                changeRequest()
            }
            steps {
                sh 'echo ========================'                
                sh 'echo running Test Stage'
            }
        }        
        stage('deploy to dev pypi') {
            when {
                changeRequest()
            }
            steps {
                sh 'echo ========================='
                sh 'echo running Deploy to dev Stage'
                sh 'bash ./build/build.sh -b $CHANGE_ID -k -s -u'
            }
        }
        stage('deploy to ose pypi') {
            when {
                anyOf {
                    branch 'v2018.3.3-ca'
                }
            }
            steps {
                sh 'echo ========================='
                sh 'echo running Deploy to ose pypi Stage'
                sh 'bash ./build/build.sh -u -p -t $BBGH_TOKEN_PSW'
            }
        }
    }
}
