pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'transfert-denrees-api'
        DOCKER_TAG = "${BUILD_NUMBER}"
        DOCKER_REGISTRY = 'maremediouf885'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Récupération du code source...'
                checkout scm
            }
        }
        
        stage('Run Tests') {
            agent {
                docker {
                    image 'python:3.11-slim'
                    args '-v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                echo 'Installation des dépendances et tests...'
                sh '''
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    python -m pytest tests/ -v --tb=short
                '''
            }
            post {
                always {
                    echo 'Tests terminés'
                }
                failure {
                    echo 'ÉCHEC: Tests unitaires'
                }
            }
        }
        
        stage('Build Docker Image') {
            agent {
                docker {
                    image 'docker:latest'
                    args '-v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                echo 'Construction de l\'image Docker...'
                sh """
                    docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                """
            }
        }
        
        stage('Deploy Info') {
            steps {
                echo 'Pipeline terminé avec succès!'
                echo "Image créée: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                echo 'Pour déployer manuellement:'
                echo "docker run -d --name transfert-denrees-app -p 8000:8000 ${DOCKER_IMAGE}:latest"
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline terminé'
        }
        success {
            echo 'SUCCÈS: Pipeline exécuté avec succès!'
        }
        failure {
            echo 'ÉCHEC: Le pipeline a échoué'
        }
    }
}