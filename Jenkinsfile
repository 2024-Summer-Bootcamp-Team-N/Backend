pipeline {
    agent any

    environment {
        DOCKER_COMPOSE_FILE = 'docker-compose.yml'
        ENV_FILE = '.env' // .env 파일의 경로 설정
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'develop', url: 'https://github.com/2024-Summer-Bootcamp-Team-N/Backend.git'
            }
        }

        stage('Copy .env') {
            steps {
                // .env 파일을 Jenkins 작업 디렉토리로 복사합니다.
                sh 'cp ${WORKSPACE}/.env .'
                // 파일 목록 확인
                sh 'ls -la ${WORKSPACE}'
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
                    sh "docker compose --env-file ${WORKSPACE}/${ENV_FILE} -f ${WORKSPACE}/${DOCKER_COMPOSE_FILE} build"
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
                    sh "docker compose --env-file ${WORKSPACE}/${ENV_FILE} -f ${WORKSPACE}/${DOCKER_COMPOSE_FILE} up -d"
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
