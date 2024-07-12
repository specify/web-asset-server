pipeline {
    agent any

    environment {
        BRANCH_NAME = "${env.CHANGE_BRANCH ?: env.BRANCH_NAME}"
        PARENT_PATH = "/var/jenkins_home/workspace"
        RSYNC_PATH = "/usr/bin/rsync"
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

//         stage('Reset to Origin') {
//             steps {
//                 script {
//                     // Ensure the working directory matches the origin
//                     sh "cd ${PARENT_PATH}/rver_multibranch_${BRANCH_NAME}"
//                     sh "git reset --hard origin/${BRANCH_NAME}"
//                 }
//             }
//         }

        stage('Copy non-tracked files') {
            steps {
                script {
                    // Copy non-tracked files from web-asset-server-ci to rver_multibranch_<BRANCH_NAME>
                    sh "${RSYNC_PATH} -av --ignore-existing ${PARENT_PATH}/web-asset-server-ci/ ${PARENT_PATH}/rver_multibranch_${BRANCH_NAME}/"
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
