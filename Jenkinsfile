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
                // 비밀 텍스트를 워크스페이스에 복사
                withCredentials([file(credentialsId: "${ENV_FILE}", variable: 'ENV_FILE_PATH')]) {
                    sh 'cp $ENV_FILE_PATH .env'
                    // .env 파일이 올바르게 복사되었는지 확인
                    sh 'ls -la ${WORKSPACE}'
                }
            }
        }

        stage('Verify nginx.conf') {
            steps {
                script {
                    def nginxConfPath = "${WORKSPACE}/nginx/nginx.conf"
                    def result = sh(script: "if [ -f ${nginxConfPath} ]; then echo 'File exists'; else echo 'File not found'; fi", returnStdout: true).trim()
                    if (result == 'File not found') {
                        error("nginx.conf file not found at ${nginxConfPath}")
                    } else {
                        echo "nginx.conf file found at ${nginxConfPath}"
                    }
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
                    // 기존의 모든 컨테이너를 중지하고 제거합니다.
                    sh "docker compose --env-file .env -f ${DOCKER_COMPOSE_FILE} down"
                    // 사용하지 않는 모든 자원을 정리합니다.
                    sh "docker system prune -f"
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
            script {
                echo 'Build or deployment failed.'
                sh 'docker logs testing-jenkins_develop-nginx-1' // Nginx 컨테이너 로그 확인
            }
        }
    }
}
