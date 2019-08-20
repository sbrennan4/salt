pipeline {
    agent { label 'syscore-salt'}
    environment {
        TEST_VAR1 = 'true'
        TEST_VAR2 = 'sqlite'
        BBGH_TOKEN = credentials('bbgithub_token')
        TWINE_PASSWORD_1 = credentials('salt_jenkins_ad_user_pass_escaped')
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
                sh 'bash -x ./build/dev-build.sh -b 20190819004'
                // sh 'curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python'
            }
        }
        stage('test') {
            steps {
                sh 'echo ========================'                
                sh 'echo running Test Stage'
            }
        }        
        stage('deploy') {
            steps {
                sh 'echo ========================='
                sh 'echo running Deploy Stage'
                sh 'bash ./build/dev-build.sh -b 20190819004 -k -K -s -u'
            }
        }
    }
    post {
        always {
            echo 'This will always run'
        }    
    }
}
