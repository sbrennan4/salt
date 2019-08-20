pipeline {
    agent { label 'syscore-salt'}
    environment {
        TEST_VAR1 = 'true'
        TEST_VAR2 = 'sqlite'
        BBGH_TOKEN = credentials('bbgithub_token')
        TWINE_PASSWORD = credentials('salt_jenkins_ad_user_pass_escaped')
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
                sh 'bash ./build/dev-build.sh -v -b 20190821001'
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
                sh 'skipping the publish to pypi step for now'
                // sh 'bash ./build/dev-build.sh -b 20190821001 -K -s -u'
            }
        }
    }
    post {
        always {
            echo 'This will always run'
        }    
    }
}
