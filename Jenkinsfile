pipeline {
    agent any

    environment {
        DOCKER_COMPOSE_FILE = 'docker-compose.yml'
        ENV_FILE = 'env-file' // Jenkins 관리 설정에서 추가한 비밀 텍스트 ID
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'develop', url: 'https://github.com/2024-Summer-Bootcamp-Team-N/Backend.git'
            }
        }

        stage('Copy .env') {
            steps {
                // 비밀 텍스트를 워크스페이스에 복사
                withCredentials([file(credentialsId: "${ENV_FILE}", variable: 'ENV_FILE_PATH')]) {
                    sh 'cp $ENV_FILE_PATH .env'
                    // 파일 목록 확인
                    sh 'ls -la ${WORKSPACE}'
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
                    // .env 파일을 Docker Compose 빌드 명령에 포함시킵니다.
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
                    // .env 파일을 Docker Compose 업 명령에 포함시킵니다.
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
            echo 'Build or deployment failed.'
        }
    }
}
