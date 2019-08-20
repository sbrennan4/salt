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
                sh './blp_build/dev-build.sh -b 20190819003'
                // sh 'curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python'
            }
        }
        stage('test') {
            steps {
                sh 'echo ========================'                
                sh 'echo running Test Stage'
                sh 'python --version'
                sh 'hostname'
                sh 'pwd'
                sh 'printenv'
            }
        }        
        stage('deploy') {
            steps {
                sh 'echo ========================='
                sh 'echo running Deploy Stage'
            }
        }
    }
    post {
        always {
            echo 'This will always run'
        }    
    }
}
