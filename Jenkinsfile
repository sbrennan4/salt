def unique_container_name = "unit-tests-${env.BUILD_ID}${env.JOB_NAME.replace("/", "-")}"
def image_name = "artprod.dev.bloomberg.com/bb-inf/salt-minion:2018.3.3"

pipeline {
    agent { label 'syscore-salt'}
    environment {
        BBGH_TOKEN = credentials('bbgithub_token')
        PYPI_CREDENTIAL = credentials('salt_jenkins_ad_user_pass_escaped')
    }
    options {
        ansiColor('xterm')
        // Currently builds take an hour and 30 minutes.
        // If every executor is used, this will give enough time for the queue to pass and this build to run
        // timeout(time: 3, unit: 'HOURS')
        // Keep up to 10 builds (artifacts/console output) from master and each branch retains up to 5 builds of that specific branch
        buildDiscarder(logRotator(numToKeepStr: env.BRANCH_NAME == 'master' ? '10' : '5'))
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
                script {
                    // We are running inside a container so we can have the bbcpu.lst/alias
                    docker.withRegistry('https://artprod.dev.bloomberg.com', 'syscore_jenkins_docker_jwt_tuple') {
                        sh "docker pull ${image_name}"
                    }
                    // Jenkins docker integration is confusing wrapper and doesn't seem to work as expected
                    sh "docker run --name ${unique_container_name} -d -v `pwd`:`pwd` -w `pwd` ${image_name}"
                    sh "docker exec ${unique_container_name} pip install -r requirements/dev_bloomberg.txt"
                    sh "docker exec ${unique_container_name} ./tests/runtests.py -n unit.test_master.AESFuncsTestCase -n unit.test_pillar.Pillar -n unit.utils.test_state.UtilStateGetSlsOptsTestcase"
                }
            } 
            post {
                cleanup {
                    node("syscore-salt") {
                        script {
                            deleteDir() /* clean up our workspace */
                            
                            try {
                                sh "docker stop ${unique_container_name}"
                            } catch(Exception e) {
                                // continue
                            }
                        }
                    }
                }
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
