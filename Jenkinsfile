pipeline {
    agent any

    environment {
        BRANCH_NAME = "${env.CHANGE_BRANCH ?: env.BRANCH_NAME}"
        PARENT_PATH = "/var/jenkins_home/workspace"
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    // Checkout the branch related to the PR
                    checkout scm
                }
            }
        }

        stage('Copy non-tracked files') {
            steps {
                script {
                    // Copy non-tracked files from web-asset-server-ci to rver_multibranch_<BRANCH_NAME>
                    sh "cp ${PARENT_PATH}/web-asset-server-ci/settings.py ${PARENT_PATH}/rver_multibranch_${BRANCH_NAME}/settings.py"
                    sh "cp ${PARENT_PATH}/web-asset-server-ci/server_jenkins.sh ${PARENT_PATH}/rver_multibranch_${BRANCH_NAME}/server_jenkins.sh"
                    sh "cp ${PARENT_PATH}/web-asset-server-ci/docker-compose.yml ${PARENT_PATH}/rver_multibranch_${BRANCH_NAME}/docker-compose.yml"


                }
            }
        }

        stage('Run Script') {
            steps {
                script {
                    // Run the provided shell script as root within the Docker container
                    sh "cd ${PARENT_PATH}/rver_multibranch_${BRANCH_NAME} && ./server_jenkins.sh"
                }
            }
        }
    }
}
