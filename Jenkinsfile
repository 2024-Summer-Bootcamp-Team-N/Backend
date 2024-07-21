pipeline {
    agent any

    environment {
        DOCKER_COMPOSE_FILE = 'docker-compose.yml'
        ENV_FILE = 'env-file' // 크리덴셜 ID를 적절히 설정합니다.
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'develop', url: 'https://github.com/2024-Summer-Bootcamp-Team-N/Backend.git'
            }
        }

        stage('Copy .env') {
            steps {
                withCredentials([file(credentialsId: "${ENV_FILE}", variable: 'ENV_FILE_PATH')]) {
                    sh 'cp $ENV_FILE_PATH .env'
                    sh 'ls -la ${WORKSPACE}'
                }
            }
        }

        stage('Install file command') {
            steps {
                sh 'apt-get update && apt-get install -y file'
            }
        }

        stage('Verify nginx.conf') {
            steps {
                script {
                    def nginxConfPath = "${WORKSPACE}/nginx/nginx.conf"
                    sh """
                    if [ -f ${nginxConfPath} ]; then
                      echo 'File exists';
                    else
                      echo 'File not found';
                      exit 1;
                    fi
                    file ${nginxConfPath}
                    """
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    sh "docker --version"
                    sh "docker compose --version"
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    sh "docker compose --env-file .env -f ${DOCKER_COMPOSE_FILE} build"
                }
            }
        }

        stage('Deploy') {
            when {
                anyOf {
                    branch 'develop'
                    branch 'master'
                }
            }
            steps {
                script {
                    sh "docker compose --env-file .env -f ${DOCKER_COMPOSE_FILE} down"
                    sh "docker system prune -f"
                    sh "docker compose --env-file .env -f ${DOCKER_COMPOSE_FILE} up -d"
                }
            }
        }
    }

    post {
        success {
            echo 'Build and deployment successful!'
        }
        failure {
            script {
                echo 'Build or deployment failed.'
                sh 'docker logs testing-jenkins_develop-nginx-1 || true'
            }
        }
    }
}
