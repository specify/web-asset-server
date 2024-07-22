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

        stage('Find and Save Directory') {
            steps {
                script {
                    // Find the directory name containing the substring "multibranch_${BRANCH_NAME}" but not containing "@tmp"
                    def dirName = sh(script: "find ${PARENT_PATH} -type d -name '*multibranch_${BRANCH_NAME}*' ! -name '*@tmp*' -print -quit", returnStdout: true).trim()
                    if (dirName) {
                        env.FOUND_DIR = dirName
                    } else {
                        error "Directory containing 'multibranch_${BRANCH_NAME}' and not containing '@tmp' not found"
                    }
                }
            }
        }

        stage('Copy non-tracked files') {
            steps {
                script {
                    // Copy non-tracked files from web-asset-server-ci to the found directory
                    sh "cp ${PARENT_PATH}/web-asset-server-ci/settings.py ${env.FOUND_DIR}/settings.py"
                    sh "cp ${PARENT_PATH}/web-asset-server-ci/server_jenkins.sh ${env.FOUND_DIR}/server_jenkins.sh"
                    sh "cp ${PARENT_PATH}/web-asset-server-ci/docker-compose.yml ${env.FOUND_DIR}/docker-compose.yml"
                    sh "cp ${PARENT_PATH}/web-asset-server-ci/images_ddl.sql ${env.FOUND_DIR}/images_ddl.sql"
                }
            }
        }

        stage('Run Script') {
            steps {
                script {
                    // Run the provided shell script as root within the Docker container
                    sh "cd ${env.FOUND_DIR} && ./server_jenkins.sh"
                }
            }
        }
    }
}
