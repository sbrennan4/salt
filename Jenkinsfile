pipeline {
    agent { label 'syscore-salt'}
    environment {
        BBGH_TOKEN = credentials('bbgithub_token')
        PYPI_CREDENTIAL = credentials('salt_jenkins_ad_user_pass_escaped')
    }
    stages {
        stage('build') {
            steps {
                sh 'echo ========================'
                sh 'echo running Build Stage'
                sh 'whoami'
                sh 'python --version'
                sh 'hostname'
                sh 'pwd'
                sh 'printenv'
                sh 'bash ./build/dev-build.sh -v -b $CHANGE_ID'
            }
        }
        stage('test') {
            steps {
                sh 'echo ========================'                
                sh 'echo running Test Stage'
            }
        }        
        stage('deploy to dev pypi') {
            steps {
                sh 'echo ========================='
                sh 'echo running Deploy Stage'
                sh 'bash ./build/dev-build.sh -b $CHANGE_ID -k -s -u'
            }
        }
    }
}
