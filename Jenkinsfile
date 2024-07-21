pipeline {
    agent any

    environment {
        DOCKER_COMPOSE_FILE = 'docker-compose.yml'
        ENV_FILE = '.env'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'develop', url: 'https://github.com/2024-Summer-Bootcamp-Team-N/Backend.git'
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
                    // .env 파일을 Docker Compose 빌드 명령에 포함시킵니다.
                    sh "docker compose --env-file ${ENV_FILE} -f ${DOCKER_COMPOSE_FILE} build"
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
                    // .env 파일을 Docker Compose 업 명령에 포함시킵니다.
                    sh "docker compose --env-file ${ENV_FILE} -f ${DOCKER_COMPOSE_FILE} up -d"
                }
            }
        }
    }

    post {
        success {
            echo 'Build and deployment successful!'
        }
        failure {
            echo 'Build or deployment failed.'
        }
    }
}
