pipeline {
    agent any

    environment {
        DOCKER_COMPOSE_FILE= 'docker-compose.yml'
        DJANGO_SECRET_KEY="${env.DJANGO_SECRET_KEY}"
        DJANGO_DEBUG="${env.DJANGO_DEBUG}"
        KAKAO_MAP_API_KEY="${env.KAKAO_MAP_API_KEY}"
        ALLOWED_HOSTS="${env.ALLOWED_HOSTS}"
        DB_NAME="${env.DB_NAME}"
        DB_USER="${env.DB_USER}"
        DB_PASSWORD="${env.DB_PASSWORD}"
        DB_HOST="${env.DB_HOST}"
        DB_PORT="${env.DB_PORT}"
        KAKAO_AK="${env.KAKAO_AK}"
        CELERY_BROKER_URL="${env.CELERY_BROKER_URL}"
        CELERY_RESULT_BACKEND="${env.CELERY_RESULT_BACKEND}"
        DJANGO_SETTINGS_MODULE="${env.DJANGO_SETTINGS_MODULE}"
        RABBITMQ_USER="${env.RABBITMQ_USER}"
        RABBITMQ_PASSWORD="${env.RABBITMQ_PASSWORD}"
        DISABLE_BLINK_FEATURES="${env.DISABLE_BLINK_FEATURES}"
        EXCLUDE_SWITCHES="${env.EXCLUDE_SWITCHES}"
        USE_AUTOMATION_EXTENSION="${env.USE_AUTOMATION_EXTENSION}"
        USER_AGENT="${env.USER_AGENT}"
        OPENAI_API_KEY="${env.OPENAI_API_KEY}"
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
                    sh "docker compose -f ${DOCKER_COMPOSE_FILE} build"
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
                    sh "docker compose -f ${DOCKER_COMPOSE_FILE} up -d"
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
