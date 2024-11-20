pipeline {
    agent any

    environment {
        BRANCH_NAME = "${env.CHANGE_BRANCH ?: env.BRANCH_NAME}"
        PARENT_PATH = "/var/jenkins_home/workspace"
        REPO_URL = "https://github.com/calacademy-research/cas-web-asset-server.git"
        LOCKFILE = "/tmp/jenkins_script.lock"
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    if (env.CHANGE_ID) {
                        // Fetch and checkout the PR branch
                        checkout([
                            $class: 'GitSCM',
                            branches: [[name: "FETCH_HEAD"]],
                            extensions: [],
                            userRemoteConfigs: [[
                                url: env.REPO_URL,
                                refspec: "+refs/pull/${env.CHANGE_ID}/head"
                            ]]
                        ])
                        // Checkout the fetched PR branch using FETCH_HEAD
                        sh "git checkout FETCH_HEAD"
                    } else {
                        // For normal branch checkout
                        checkout scm
                        sh "git fetch --all"
                        sh "git reset --hard origin/${BRANCH_NAME}"
                    }
                }
            }
        }

        stage('Find and Save Directory') {
            steps {
                script {
                    def dirName = "${WORKSPACE}"
                    if (dirName) {
                        env.FOUND_DIR = dirName
                    } else {
                        error "Directory containing 'allbranch_${BRANCH_NAME}' and not containing '@tmp' not found"
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
                    sh "cp ${PARENT_PATH}/web-asset-server-ci/server_jenkins_config.sh ${env.FOUND_DIR}/server_jenkins_config.sh"
                    sh "cp ${PARENT_PATH}/web-asset-server-ci/docker-compose.yml ${env.FOUND_DIR}/docker-compose.yml"
                    sh "cp ${PARENT_PATH}/web-asset-server-ci/images_ddl.sql ${env.FOUND_DIR}/images_ddl.sql"
                    sh "cp ${PARENT_PATH}/web-asset-server-ci/nginx_test.conf ${env.FOUND_DIR}/nginx.conf"
                }
            }
        }

        stage('Run Script') {
            steps {
                script {
                    // Retry logic: check for lockfile and wait if another instance is running
                    def lockFile = env.LOCKFILE
                    def retries = 10
                    def waitTime = 30 // seconds

                    while (fileExists(lockFile) && retries > 0) {
                        echo "Lockfile detected, waiting for ${waitTime} seconds before retrying..."
                        sleep(waitTime)
                        retries--
                    }

                    if (retries == 0) {
                        error "Another instance of the script is already running. Timeout reached."
                    } else {
                        // No lockfile, proceed with running the script
                        sh "cd ${env.FOUND_DIR} && ./server_jenkins.sh"
                    }
                }
            }
        }
    }

    post {
        always {
            // Clean up workspace with specified options
            cleanWs(
                cleanWhenNotBuilt: false,
                deleteDirs: true,
                disableDeferredWipeout: true,
                notFailBuild: true,
                patterns: [
                    [pattern: '.gitignore', type: 'INCLUDE'],
                    [pattern: '.propsfile', type: 'EXCLUDE']
                ]
            )
        }
    }
}